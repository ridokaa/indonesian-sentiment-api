import httpx
from app.config import settings


class VerosightClient:
    def __init__(self):
        self.base_url = settings.verosight_base_url
        self.api_key = settings.verosight_api_key

    async def fetch_comments(
        self, keyword: str = "Asing", days: int = 30, limit: int = 50
    ) -> list[str]:
        url = f"{self.base_url}/v1/comments"
        params = {"keyword": keyword, "days": days, "limit": limit}

        headers = {"X-API-Key": self.api_key}

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                resp = await client.get(url, params=params, headers=headers)
                resp.raise_for_status()
                data = resp.json()

                comments = self._extract_texts(data)
                return comments[:limit]

            except httpx.HTTPStatusError as e:
                raise RuntimeError(
                    f"Verosight API returned {e.response.status_code}: {e.response.text}"
                )
            except httpx.TimeoutException:
                raise RuntimeError("Verosight API request timed out")
            except httpx.RequestError as e:
                raise RuntimeError(f"Verosight API request failed: {e}")

    def _extract_texts(self, data: dict) -> list[str]:
        texts = []
        items = data if isinstance(data, list) else data.get("data", [])
        for item in items:
            if isinstance(item, dict):
                text = item.get("text") or item.get("content") or item.get("message", "")
                if text:
                    texts.append(text)
            elif isinstance(item, str):
                texts.append(item)
        return texts
