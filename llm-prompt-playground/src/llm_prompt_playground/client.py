import asyncio
import json
import time
from typing import Dict, Any, List

import httpx

from .config import Config


class LLMClient:
    """Async client for OpenAI-compatible /v1/chat/completions."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.session = httpx.AsyncClient(timeout=30.0)

    async def close(self) -> None:
        await self.session.aclose()

    async def chat(
        self, messages: List[Dict[str, str]], model: str = "gpt-4o-mini"
    ) -> Dict[str, Any]:
        """Send chat request, mock if no auth."""
        start_time = time.time()

        if not self.config.api_key:
            result = await self._mock_chat(messages)
        else:
            result = await self._api_chat(messages, model)

        result["latency_ms"] = round((time.time() - start_time) * 1000)
        return result

    async def _api_chat(self, messages: List[Dict], model: str) -> Dict[str, Any]:
        url = f"{self.config.base_url.rstrip('/')}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": model,
            "messages": messages,
            "temperature": 0.1,
            "stream": False,
        }

        resp = await self.session.post(url, headers=headers, json=data)
        resp.raise_for_status()
        return resp.json()

    async def _mock_chat(self, messages: List[Dict]) -> Dict[str, Any]:
        # Deterministic mock based on prompt
        prompt_text = " ".join(m["content"][:50] for m in messages if m["role"] == "user")
        content = f"Mock response to: {prompt_text}... [Set API_KEY or config for real LLM]"
        return {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": content,
                    }
                }
            ],
        }
