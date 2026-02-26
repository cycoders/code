import pytest
from unittest.mock import AsyncMock
import fakeredis.aioredis

from redis_explorer_tui.redis_client import RedisClient


@pytest.fixture
def fake_redis_client():
    client = RedisClient("localhost", 6379, None, 0, False)
    client._redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
    return client


@pytest.mark.asyncio
async def test_get_keys(fake_redis_client):
    await fake_redis_client._redis.set("test:key", "value")
    keys = await fake_redis_client.get_keys("test:*", 10)
    assert "test:key" in keys


@pytest.mark.asyncio
async def test_get_key_type(fake_redis_client):
    await fake_redis_client._redis.set("foo", "bar")
    typ = await fake_redis_client.get_key_type("foo")
    assert typ == "string"


@pytest.mark.asyncio
async def test_get_ttl(fake_redis_client):
    await fake_redis_client._redis.setex("expkey", 60, "val")
    ttl = await fake_redis_client.get_ttl("expkey")
    assert isinstance(ttl, int)


@pytest.mark.asyncio
async def test_memory_usage(fake_redis_client):
    await fake_redis_client._redis.set("key", "a" * 100)
    size = await fake_redis_client.memory_usage("key")
    assert size > 0


@pytest.mark.asyncio
async def test_get_value_json(fake_redis_client):
    await fake_redis_client._redis.set("jsonkey", '{"a":1}')
    value = await fake_redis_client.get_value("jsonkey")
    assert "{" in value


@pytest.mark.asyncio
async def test_info(fake_redis_client):
    info = await fake_redis_client.info()
    assert isinstance(info, dict)
    assert "redis_version" in info
