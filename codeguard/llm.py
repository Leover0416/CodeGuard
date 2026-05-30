import json
import re

import httpx

from codeguard.config import settings
from codeguard.models import ReviewResult


class LLMClient:
    def __init__(self) -> None:
        if not settings.openai_api_key.strip():
            raise RuntimeError(
                "未配置 OPENAI_API_KEY。请在 .env 中设置（支持 OpenAI 兼容接口）。"
            )
        self._client = httpx.Client(
            base_url=settings.openai_base_url.rstrip("/"),
            headers={
                "Authorization": f"Bearer {settings.openai_api_key}",
                "Content-Type": "application/json",
            },
            timeout=120.0,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "LLMClient":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def complete_json(self, system: str, user: str) -> dict:
        payload = {
            "model": settings.openai_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }
        resp = self._client.post("/chat/completions", json=payload)
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        return _parse_json_content(content)


def _parse_json_content(content: str) -> dict:
    text = content.strip()
    # 部分模型仍会包裹 ```json
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if fence:
        text = fence.group(1).strip()
    return json.loads(text)


def parse_review_result(raw: dict) -> ReviewResult:
    return ReviewResult.model_validate(raw)
