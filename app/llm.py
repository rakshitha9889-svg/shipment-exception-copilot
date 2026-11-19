import logging
from dataclasses import dataclass

from langfuse.openai import OpenAI  # drop-in replacement: every call is traced in Langfuse
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings
from app.schemas import LLMOutput

log = logging.getLogger(__name__)

SYSTEM_PROMPT = """You triage courier exception notes for a parcel network.
Notes may be German, English or mixed, with typos and abbreviations.
Classify the note, summarise it in English, and choose the next action
ONLY from the handling rules provided. Cite the rule_id you used.
If no rule fits, set rule_id to "none" and next_action to "escalate to a human agent"."""


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
        timeout=20,
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
