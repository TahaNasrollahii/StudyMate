"""
Redis client configuration and utilities.
"""

from typing import Optional, Union

import redis.asyncio as aioredis

from app.config import settings

redis_client: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    """Get Redis client instance. Must be initialized before use."""
    global redis_client
    if redis_client is None:
        raise RuntimeError("Redis client is not initialized")
    return redis_client


async def init_redis() -> None:
    """Initialize Redis client and verify connection."""
    global redis_client
    if redis_client is None:
        client = aioredis.from_url(
            settings.REDIS_URL, encoding="utf-8", decode_responses=True
        )
        try:
            await client.ping()
        except Exception as e:
            raise RuntimeError(f"Failed to connect to Redis: {e}")
        redis_client = client


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
