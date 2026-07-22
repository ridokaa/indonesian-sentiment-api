import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from app.config import settings


class SemanticSentimentEngine:
    def __init__(self):
        self.model = SentenceTransformer(settings.embedding_model_name)

        self.anchor_sentences = {
            "POSITIVE": [
                "opini positif",
                "pujian dan dukungan",
                "sangat bagus dan menyenangkan",
                "setuju dan bersyukur",
            ],
            "NEGATIVE": [
                "opini negatif",
                "kritikan dan kebencian",
                "sangat buruk dan mengecewakan",
                "tidak setuju dan marah",
            ],
            "NEUTRAL": [
                "informasi netral",
                "berita atau fakta biasa",
                "tanpa emosi",
                "pernyataan umum",
            ],
        }

        self._anchor_embeddings: dict[str, np.ndarray] | None = None
        self._encode_anchors()

    def _encode_anchors(self):
        embeddings = {}
        for label, sentences in self.anchor_sentences.items():
            emb = self.model.encode(sentences, convert_to_numpy=True)
            embeddings[label] = emb
        self._anchor_embeddings = embeddings

    def analyze_text(self, text: str) -> dict:
        text_emb = self.model.encode([text], convert_to_numpy=True)

        scores = {}
        for label, anchor_emb in self._anchor_embeddings.items():
            sim_matrix = cosine_similarity(text_emb, anchor_emb)
            scores[label] = float(sim_matrix.max())

        total = sum(scores.values()) or 1.0
        confidence_scores = {k: v / total for k, v in scores.items()}

        label = max(confidence_scores, key=confidence_scores.get)
        confidence = confidence_scores[label]

        return {
            "label": label,
            "confidence": round(confidence, 4),
            "scores": {k: round(v, 4) for k, v in scores.items()},
        }
