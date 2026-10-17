from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from app.schemas.sentiment import (
    BatchAnalysisResponse,
    SentimentResult,
    SingleAnalysisRequest,
)
from app.services.sentiment_engine import SemanticSentimentEngine
from app.services.verosight_client import VerosightClient

engine: SemanticSentimentEngine | None = None
client: VerosightClient | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global engine, client
    engine = SemanticSentimentEngine()
    client = VerosightClient()
    yield


app = FastAPI(title="Indonesian Sentiment API", version="1.0.0", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/v1/analyze", response_model=SentimentResult)
async def analyze_text(req: SingleAnalysisRequest):
    if not engine:
        raise HTTPException(503, "Engine not ready")
    result = engine.analyze_text(req.text)
    return SentimentResult(text=req.text, **result)


@app.get("/api/v1/fetch-and-analyze", response_model=BatchAnalysisResponse)
async def fetch_and_analyze(
    keyword: str = "Asing", days: int = 30, limit: int = 50
):
    if not engine or not client:
        raise HTTPException(503, "Service not ready")
    try:
        comments = await client.fetch_comments(
            keyword=keyword, days=days, limit=limit
        )
    except RuntimeError as e:
        raise HTTPException(502, str(e))

    results = []
    for text in comments:
        result = engine.analyze_text(text)
        results.append(SentimentResult(text=text, **result))

    return BatchAnalysisResponse(total=len(results), results=results)
