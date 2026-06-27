"""
Redis client configuration and utilities.
"""

from typing import Optional

import redis.asyncio as aioredis

from app.config import settings

redis_client: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    """Get Redis client instance."""
    global redis_client
    if redis_client is None:
        redis_client = aioredis.from_url(
            settings.REDIS_URL, encoding="utf-8", decode_responses=True
        )
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
