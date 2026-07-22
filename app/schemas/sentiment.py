from pydantic import BaseModel


class SingleAnalysisRequest(BaseModel):
    text: str


class SentimentResult(BaseModel):
    text: str
    label: str
    confidence: float
    scores: dict


class BatchAnalysisResponse(BaseModel):
    total: int
    results: list[SentimentResult]
