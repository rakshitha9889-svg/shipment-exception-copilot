from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from qdrant_client import QdrantClient

from app.llm import AllProvidersFailed, Provider, classify_note
from app.main import app, get_providers, get_store
from app.rag import RuleStore
from app.schemas import LLMOutput

GOOD = LLMOutput(category="customs_hold", urgency="high", language="en",
                 summary_en="Held at customs, documents missing.",
                 next_action="Request the commercial invoice from the sender.", rule_id="R05")


class FakeClient:
    """Mimics client.chat.completions.parse; fails the first `fail` calls."""

    def __init__(self, fail: int = 0):
        self.fail, self.calls = fail, 0
        self.chat = SimpleNamespace(completions=SimpleNamespace(parse=self.parse))

    def parse(self, **kwargs):
        self.calls += 1
        if self.calls <= self.fail:
            raise TimeoutError("provider timeout")
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(parsed=GOOD))])


class FakeEmbedder:
    """Deterministic 8-dim bag-of-letters vectors, so tests need no model download."""

    def embed(self, texts):
        for t in texts:
            yield [t.lower().count(c) + 0.01 for c in "aeioucdh"]


@pytest.fixture
def store(tmp_path):
    s = RuleStore(client=QdrantClient(":memory:"), embedder=FakeEmbedder())
    s.load("data/rules.jsonl")
    return s


def test_rules_load_and_search(store):
    hits = store.search("customs documents missing", k=3)
    assert len(hits) == 3 and all("id" in h for h in hits)


def test_retry_then_success():
    p = Provider("primary", FakeClient(fail=2), "m")
    out, name = classify_note("note", [], [p])
    assert name == "primary" and out.rule_id == "R05" and p.client.calls == 3


def test_failover_to_fallback():
    primary, fallback = Provider("primary", FakeClient(fail=99), "m"), Provider("fallback", FakeClient(), "m")
    _, name = classify_note("note", [], [primary, fallback])
    assert name == "fallback"


def test_all_providers_fail():
    with pytest.raises(AllProvidersFailed):
        classify_note("note", [], [Provider("primary", FakeClient(fail=99), "m")])


def test_api_classify_and_health(store):
    app.dependency_overrides[get_store] = lambda: store
    app.dependency_overrides[get_providers] = lambda: [Provider("primary", FakeClient(), "m")]
    client = TestClient(app)  # no `with`: skips lifespan, so no real Qdrant or model is needed
    assert client.get("/health").json() == {"status": "ok"}
    r = client.post("/classify", json={"note": "Zolldokumente fehlen, Paket am Hub"})
    assert r.status_code == 200 and r.json()["category"] == "customs_hold" and r.json()["provider"] == "primary"
    assert client.post("/classify", json={"note": "x"}).status_code == 422  # Pydantic rejects too-short notes
    app.dependency_overrides.clear()
