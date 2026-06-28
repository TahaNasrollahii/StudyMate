"""
Redis client configuration and utilities.
"""

from typing import Optional, Union

import redis.asyncio as aioredis

from app.config import settings

class DummyRedis:
    def __init__(self):
        self.store = {}
    
    async def close(self):
        pass

    async def get(self, key):
        return self.store.get(key)
    
    async def setex(self, key, ttl, value):
        self.store[key] = value

    async def exists(self, key):
        return 1 if key in self.store else 0

redis_client: Optional[Union[aioredis.Redis, DummyRedis]] = None


async def get_redis() -> Union[aioredis.Redis, DummyRedis]:
    """Get Redis client instance or fallback."""
    global redis_client
    if redis_client is None:
        try:
            client = aioredis.from_url(
                settings.REDIS_URL, encoding="utf-8", decode_responses=True
            )
            await client.ping()
            redis_client = client
        except Exception:
            redis_client = DummyRedis()
    return redis_client


async def close_redis() -> None:
    """Close Redis connection."""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None


async def get_cached_result(key: str) -> Optional[str]:
    """Get result from Redis cache."""
    client = await get_redis()
    return await client.get(key)


async def set_cached_result(key: str, value: str, ttl: int = 3600) -> None:
    """Set result in Redis cache with TTL."""
    client = await get_redis()
    await client.setex(key, ttl, value)
