from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request

from app import pipeline
from app.llm import AllProvidersFailed, Provider, build_providers
from app.rag import RuleStore
from app.schemas import ClassifyRequest, ClassifyResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.store = RuleStore()
    app.state.providers = build_providers()
    yield


app = FastAPI(title="Shipment Exception Copilot", lifespan=lifespan)


def get_store(request: Request) -> RuleStore:
    return request.app.state.store


def get_providers(request: Request):
    return request.app.state.providers


Store = Annotated[RuleStore, Depends(get_store)]
Providers = Annotated[list[Provider], Depends(get_providers)]


@app.get("/health")
def health(store: Store):
    if not store.healthy():
        raise HTTPException(503, "rules collection not ready")
    return {"status": "ok"}


@app.post("/classify", response_model=ClassifyResponse)
def classify(req: ClassifyRequest, store: Store, providers: Providers):
    try:
        return pipeline.run(req.note, store, providers)
    except AllProvidersFailed as e:
        raise HTTPException(502, f"all LLM providers failed: {e}") from e
