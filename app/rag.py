import json
import uuid
from pathlib import Path

from fastembed import TextEmbedding
from qdrant_client import QdrantClient, models

from app.config import settings


class RuleStore:
    """Handling rules in Qdrant, embedded with a multilingual model so German notes match English rules."""

    def __init__(self, client: QdrantClient | None = None, embedder=None):
        self.client = client or QdrantClient(url=settings.qdrant_url)
        self.embedder = embedder or TextEmbedding(settings.embed_model)
        self.collection = settings.rules_collection

    def _embed(self, texts: list[str]) -> list[list[float]]:
        return [list(map(float, v)) for v in self.embedder.embed(texts)]

    def load(self, path: str | Path) -> int:
        rules = [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]
        vectors = self._embed([r["text"] for r in rules])
        if self.client.collection_exists(self.collection):
            self.client.delete_collection(self.collection)
        self.client.create_collection(
            self.collection,
            vectors_config=models.VectorParams(size=len(vectors[0]), distance=models.Distance.COSINE),
        )
        self.client.upsert(self.collection, points=[
            models.PointStruct(id=str(uuid.uuid5(uuid.NAMESPACE_URL, r["id"])), vector=v, payload=r)
            for r, v in zip(rules, vectors, strict=True)
        ])
        return len(rules)

    def search(self, note: str, k: int = settings.top_k) -> list[dict]:
        hits = self.client.query_points(self.collection, query=self._embed([note])[0], limit=k).points
        return [h.payload for h in hits]

    def healthy(self) -> bool:
        try:
            return self.client.collection_exists(self.collection)
        except Exception:  # noqa: BLE001
            return False
