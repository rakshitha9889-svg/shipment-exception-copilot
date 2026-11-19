import time

from langfuse import observe

from app.llm import Provider, classify_note
from app.rag import RuleStore
from app.schemas import ClassifyResponse


@observe(name="classify-note")  # one Langfuse trace per note: retrieval + LLM call nested inside
def run(note: str, store: RuleStore, providers: list[Provider]) -> ClassifyResponse:
    start = time.perf_counter()
    rules = store.search(note)
    out, provider = classify_note(note, rules, providers)
    latency_ms = round((time.perf_counter() - start) * 1000, 1)
    return ClassifyResponse(**out.model_dump(), provider=provider, latency_ms=latency_ms)
