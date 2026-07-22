import re
from model.lexicon import analyze_lexicon


PREPROCESS_PATTERNS = [
    (r"http\S+", ""),
    (r"@\w+", ""),
    (r"#(\w+)", r"\1"),
    (r"\b(\w+)\1{2,}\b", r"\1"),
    (r"([a-zA-Z])\1{2,}", r"\1"),
]


def preprocess_text(text):
    text = text.lower()
    for pattern, repl in PREPROCESS_PATTERNS:
        text = re.sub(pattern, repl, text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def analyze_sentiment(text, preprocess=True):
    if not text or not text.strip():
        return {"label": "netral", "score": 0.0, "text": text}
    cleaned = preprocess_text(text) if preprocess else text
    result = analyze_lexicon(cleaned)
    result["text"] = text
    result["cleaned_text"] = cleaned
    return result


def analyze_batch(comments, text_key="text"):
    results = []
    for item in comments:
        text = item.get("content", "") if isinstance(item, dict) else item
        sentiment = analyze_sentiment(text)
        if isinstance(item, dict):
            sentiment.update(item)
        results.append(sentiment)
    return results


def summary_statistics(results):
    labels = [r["label"] for r in results]
    total = len(labels)
    if total == 0:
        return {"total": 0, "positif": 0, "negatif": 0, "netral": 0}
    return {
        "total": total,
        "positif": labels.count("positif"),
        "negatif": labels.count("negatif"),
        "netral": labels.count("netral"),
    }
