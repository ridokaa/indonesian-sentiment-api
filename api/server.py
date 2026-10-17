from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from data.fetch_data import load_comments
from model.analyzer import analyze_sentiment, analyze_batch, summary_statistics

app = FastAPI(
    title="Indonesian Sentiment API",
    description="API analisis sentimen komentar media sosial Bahasa Indonesia",
    version="1.0.0",
)


class SentimentRequest(BaseModel):
    text: str


class SentimentResponse(BaseModel):
    text: str
    label: str
    score: float
    positive_words: List[str] = []
    negative_words: List[str] = []
    cleaned_text: Optional[str] = None


class BatchRequest(BaseModel):
    comments: List[str]


class BatchResponse(BaseModel):
    results: List[SentimentResponse]
    summary: dict


@app.get("/")
def root():
    return {
        "service": "Indonesian Sentiment API",
        "docs": "/docs",
        "endpoints": {
            "GET /analyze?text=...": "Analisis sentimen teks tunggal",
            "POST /analyze": "Analisis sentimen via POST JSON",
            "POST /batch": "Analisis batch banyak teks",
            "GET /comments": "Ambil komentar dari sumber data",
            "GET /comments/sentiment": "Analisis sentimen semua komentar tersedia",
        },
    }


@app.get("/analyze", response_model=SentimentResponse)
def analyze_get(text: str = Query(..., description="Teks yang akan dianalisis")):
    if not text.strip():
        raise HTTPException(status_code=400, detail="Teks tidak boleh kosong")
    result = analyze_sentiment(text)
    return SentimentResponse(
        text=result["text"],
        label=result["label"],
        score=result["score"],
        positive_words=result.get("positive_words", []),
        negative_words=result.get("negative_words", []),
        cleaned_text=result.get("cleaned_text"),
    )


@app.post("/analyze", response_model=SentimentResponse)
def analyze_post(req: SentimentRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Teks tidak boleh kosong")
    result = analyze_sentiment(req.text)
    return SentimentResponse(
        text=result["text"],
        label=result["label"],
        score=result["score"],
        positive_words=result.get("positive_words", []),
        negative_words=result.get("negative_words", []),
        cleaned_text=result.get("cleaned_text"),
    )


@app.post("/batch", response_model=BatchResponse)
def analyze_batch_endpoint(req: BatchRequest):
    if not req.comments:
        raise HTTPException(status_code=400, detail="Daftar komentar tidak boleh kosong")
    results = analyze_batch(req.comments)
    summary = summary_statistics(results)
    return BatchResponse(
        results=[
            SentimentResponse(
                text=r["text"],
                label=r["label"],
                score=r["score"],
                positive_words=r.get("positive_words", []),
                negative_words=r.get("negative_words", []),
                cleaned_text=r.get("cleaned_text"),
            )
            for r in results
        ],
        summary=summary,
    )


@app.get("/comments")
def get_comments(
    days: int = Query(20, ge=1, le=365),
    limit: int = Query(50, ge=1, le=200),
    keyword: str = Query("BBM"),
):
    comments, source = load_comments(days, limit, keyword)
    return {"source": source, "total": len(comments), "comments": comments}


@app.get("/comments/sentiment")
def comments_sentiment(
    days: int = Query(20, ge=1, le=365),
    limit: int = Query(50, ge=1, le=200),
    keyword: str = Query("BBM"),
):
    comments, source = load_comments(days, limit, keyword)
    results = analyze_batch(comments)
    summary = summary_statistics(results)
    return {"source": source, "summary": summary, "results": results}
