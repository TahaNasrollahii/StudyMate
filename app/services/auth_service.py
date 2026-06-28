"""
Auth service for handling refresh tokens and session revocation.
"""

from typing import Optional

from app.redis_client import get_redis
from app.config import settings

def _get_revocation_key(token: str) -> str:
    """Get Redis key for revoked token."""
    return f"revoked_token:{token}"


async def revoke_token(token: str, expires_in: int) -> None:
    """Revoke a token by adding it to Redis blocklist with TTL."""
    client = await get_redis()
    await client.setex(_get_revocation_key(token), expires_in, "revoked")


async def is_token_revoked(token: str) -> bool:
    """Check if a token is in the blocklist."""
    client = await get_redis()
    return await client.exists(_get_revocation_key(token)) > 0
