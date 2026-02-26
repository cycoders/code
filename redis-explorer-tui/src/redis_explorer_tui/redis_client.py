import json
import redis.asyncio as aioredis
from typing import Any, Dict, List, Optional

class RedisClient:
    """
    Async Redis client wrapper with common methods for explorer.
    """

    def __init__(
        self,
        host: str,
        port: int,
        password: Optional[str],
        db: int,
        ssl: bool = False,
    ):
        self.host = host
        self.port = port
        self.password = password
        self.db = db
        self.ssl = ssl
        self._redis: Optional[aioredis.Redis] = None

    async def connect(self) -> None:
        kwargs = {
            "host": self.host,
            "port": self.port,
            "db": self.db,
            "decode_responses": True,
            "socket_timeout": 5,
            "socket_connect_timeout": 5,
        }
        if self.password:
            kwargs["password"] = self.password
        if self.ssl:
            kwargs["ssl"] = True
            kwargs["ssl_cert_reqs"] = None  # Dev-friendly, skip verify
        self._redis = aioredis.Redis(**kwargs)
        await self._redis.ping()

    async def close(self) -> None:
        if self._redis:
            await self._redis.aclose()

    async def get_keys(self, pattern: str = "*", count: int = 200) -> List[str]:
        if not self._redis:
            raise RuntimeError("Not connected")
        keys = []
        cursor = 0
        while True:
            cursor, partial = await self._redis.scan(cursor, match=pattern, count=count)
            keys.extend(partial)
            if cursor == 0:
                break
        return keys

    async def get_key_type(self, key: str) -> str:
        typ = await self._redis.type(key)
        return typ.decode() if isinstance(typ, bytes) else typ

    async def get_ttl(self, key: str) -> Optional[int]:
        ttl = await self._redis.ttl(key)
        return ttl if ttl >= 0 else None

    async def memory_usage(self, key: str) -> int:
        try:
            return await self._redis.memory_usage(key)
        except:
            return 0

    async def get_value(self, key: str) -> str:
        typ = await self.get_key_type(key)
        try:
            if typ == "string":
                val = await self._redis.get(key)
                if val and val.startswith("{"):
                    return json.dumps(json.loads(val), indent=2)[:5000] + "..."
                return repr(val)[:5000] + "..."
            elif typ == "list":
                vals = await self._redis.lrange(key, 0, 20)
                return f"List [{len(vals)} items]\n" + "\n".join(repr(v) for v in vals[:10])
            elif typ == "set":
                vals = await self._redis.smembers(key)
                return f"Set [{len(vals)} items]\n" + "\n".join(repr(v) for v in list(vals)[:10])
            elif typ == "hash":
                vals = await self._redis.hgetall(key)
                return json.dumps(dict(vals), indent=2)[:5000] + "..."
            elif typ == "zset":
                vals = await self._redis.zrange(key, 0, 10, withscores=True)
                return f"ZSet top 10:\n" + "\n".join(f"{k}: {score}" for k, score in vals)
            elif typ == "stream":
                vals = await self._redis.xrange(key, "-", "+", count=10)
                return f"Stream top 10:\n" + "\n".join(str(v) for v in vals)
            else:
                return f"[{typ.upper()}] Preview not supported"
        except Exception:
            return "Error fetching value"

    async def info(self) -> Dict[str, Any]:
        raw = await self._redis.info()
        return {k.decode(): v if isinstance(v, (int, str)) else str(v) for k, v in raw.items()}

    async def memory_stats(self) -> Dict[str, Any]:
        try:
            raw = await self._redis.memory_stats()
            return {k.decode(): v for k, v in raw.items()}
        except:
            return {}

    async def slowlog_get(self, num: int = 20) -> List[List[Any]]:
        try:
            return await self._redis.slowlog_get(num)
        except:
            return []
