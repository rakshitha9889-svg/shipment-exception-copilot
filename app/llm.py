import logging
from dataclasses import dataclass

from langfuse.openai import OpenAI  # drop-in replacement: every call is traced in Langfuse
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings
from app.schemas import LLMOutput

log = logging.getLogger(__name__)

SYSTEM_PROMPT = """You triage courier exception notes for a German parcel network.
Notes may be German, English or mixed, with typos and abbreviations.

Categories:
- recipient_absent: delivery attempted at a valid address, but nobody accepted it (includes long absence).
- address_issue: the address itself is wrong, incomplete or cannot be found; recipient or company moved.
- customs_hold: the parcel is held or checked by customs (documents, duties, inspection).
- damaged: physical damage to the parcel or its contents.
- refused: the recipient (or someone authorised for them) refused the parcel or a payment.
- delay: delivery postponed by traffic, weather, road closures, public events, hub or line-haul delays, or capacity.
- other: operational, equipment, safety or third-party problems that fit none of the above
  (scanner or vehicle problems, keys, access codes, animals, hazardous smells, disputes with neighbours).

Tie-break rules:
1. Label what happened last: if the recipient refused, use refused, even if the parcel was damaged or had customs fees.
2. If customs is still holding or inspecting the parcel, use customs_hold, even if it is damaged.
3. Road closures and blocked roads are delay; problems with the courier's own equipment or vehicle are other.

Urgency:
- high: every customs hold, and any refusal of customs duties; packaging split open or contents exposed,
  leaking or broken (also when the recipient refused because of it); a parcel so wet its barcode
  cannot be read; hazardous smells or threats to people (for example a police closure for a bomb threat).
- medium: second failed attempt or a long absence; an address that must be clarified or cannot be found
  (including a name missing on the doorbell); a refused cash-on-delivery payment, or a refusal because the
  box is damaged but contents are not exposed; delivery moved to the next day or the address cannot be
  reached at all (tour stopped, snow, capacity, road fully blocked, public event); damage that needs
  repacking or a claim; obstacles at the address (wasps, dogs, gate codes); locked-in keys; a system
  crash or parcels that must be entered manually.
- low: first failed attempt (card left, left with a neighbour, at a pickup point or a chosen place, or no
  safe place); a plain refusal that returns to sender; same-day delays of a few hours (traffic, accidents,
  hub, line-haul, train or flight delays); small or cosmetic damage with contents intact; minor issues the
  courier fixes on the spot (a scanner restart, a duplicate label, a renamed street)."""


@dataclass
class Provider:
    name: str
    client: OpenAI
    model: str


def build_providers() -> list[Provider]:
    providers = [Provider("primary", OpenAI(base_url=settings.llm_base_url,
                                            api_key=settings.llm_api_key, max_retries=0),
                          settings.llm_model)]
    if settings.fallback_model:
        providers.append(Provider("fallback", OpenAI(base_url=settings.fallback_base_url,
                                                     api_key=settings.fallback_api_key, max_retries=0),
                                  settings.fallback_model))
    return providers


class AllProvidersFailed(RuntimeError):
    pass


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=0.5, max=4), reraise=True)
def _call(provider: Provider, messages: list[dict]) -> LLMOutput:
    resp = provider.client.chat.completions.parse(
        model=provider.model,
        messages=messages,
        response_format=LLMOutput,
        temperature=0,
        timeout=60,
    )
    parsed = resp.choices[0].message.parsed
    if parsed is None:
        raise ValueError("model returned no parseable output")
    return parsed


def classify_note(note: str, rules: list[dict], providers: list[Provider]) -> tuple[LLMOutput, str]:
    rules_text = "\n".join(f"[{r['id']}] {r['text']}" for r in rules) or "(no rules found)"
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Handling rules:\n{rules_text}\n\nCourier note:\n{note}"},
    ]
    last_error: Exception | None = None
    for provider in providers:  # provider failover: try each in order
        try:
            return _call(provider, messages), provider.name
        except Exception as e:  # noqa: BLE001
            log.warning("provider %s failed: %s", provider.name, e)
            last_error = e
    raise AllProvidersFailed(str(last_error))
