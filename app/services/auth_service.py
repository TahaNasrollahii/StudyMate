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

async def revoke_all_sessions(user_id: int) -> None:
    """Revoke all sessions for a user by storing a cutoff timestamp."""
    import time
    client = await get_redis()
    cutoff_time = int(time.time())
    await client.set(f"revoke_all:{user_id}", str(cutoff_time))

async def is_session_valid(user_id: int, iat: int) -> bool:
    """Check if the session was issued before a global revocation."""
    client = await get_redis()
    cutoff_time_str = await client.get(f"revoke_all:{user_id}")
    if cutoff_time_str:
        cutoff_time = int(cutoff_time_str)
        if iat <= cutoff_time:
            return False
    return True
