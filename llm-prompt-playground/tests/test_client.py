import httpx
from unittest.mock import AsyncMock, patch

import pytest

from llm_prompt_playground.client import LLMClient
from llm_prompt_playground.config import Config


@pytest.mark.asyncio
async def test_mock_chat():
    config = Config(api_key=None)
    client = LLMClient(config)
    messages = [{"role": "user", "content": "test"}]
    result = await client.chat(messages)
    assert "Mock response" in result["choices"][0]["message"]["content"]


@pytest.mark.asyncio
@patch("httpx.AsyncClient.post", new_callable=AsyncMock)
async def test_api_chat(mock_post):
    mock_post.return_value.json.return_value = {"choices": [{"message": {"content": "ok"}}]}
    config = Config(base_url="http://test", api_key="key")
    client = LLMClient(config)
    result = await client.chat([{}], "model")
    assert result["choices"][0]["message"]["content"] == "ok"
