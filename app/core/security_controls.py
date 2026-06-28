"""
Security controls including rate limiting and brute force protection.
"""

from fastapi import HTTPException, Request, status

from app.redis_client import get_redis

# Config limits
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_MINUTES = 15
RATE_LIMIT_REQUESTS = 10
RATE_LIMIT_WINDOW_SEC = 60

def _get_rate_limit_key(request: Request, endpoint: str) -> str:
    """Generate a rate limit key based on IP and endpoint."""
    ip = request.client.host if request.client else "unknown"
    return f"rate_limit:{endpoint}:{ip}"

def _get_brute_force_key(email: str) -> str:
    """Generate brute force tracking key."""
    return f"bf_track:{email}"

def _get_lockout_key(email: str) -> str:
    """Generate lockout key."""
    return f"bf_lockout:{email}"

async def check_rate_limit(request: Request, endpoint: str) -> None:
    """Check if the client has exceeded the rate limit."""
    client = await get_redis()
    key = _get_rate_limit_key(request, endpoint)
    
    current = await client.incr(key)
    if current == 1:
        await client.expire(key, RATE_LIMIT_WINDOW_SEC)
        
    if current > RATE_LIMIT_REQUESTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later."
        )

async def check_login_allowed(email: str) -> None:
    """Check if the user is currently locked out."""
    client = await get_redis()
    key = _get_lockout_key(email)
    
    if await client.exists(key):
        ttl = await client.ttl(key)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Account temporarily locked due to multiple failed login attempts. Try again in {ttl // 60} minutes."
        )

async def record_failed_login(email: str) -> None:
    """Record a failed login attempt and lock if threshold exceeded."""
    client = await get_redis()
    track_key = _get_brute_force_key(email)
    lock_key = _get_lockout_key(email)
    
    attempts = await client.incr(track_key)
    if attempts == 1:
        await client.expire(track_key, LOCKOUT_MINUTES * 60)
        
    if attempts >= MAX_LOGIN_ATTEMPTS:
        await client.setex(lock_key, LOCKOUT_MINUTES * 60, "locked")
        await client.delete(track_key)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many failed login attempts. Account locked for {LOCKOUT_MINUTES} minutes."
        )

async def reset_login_attempts(email: str) -> None:
    """Reset failed login attempts on successful login."""
    client = await get_redis()
    await client.delete(_get_brute_force_key(email))
