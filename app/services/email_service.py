"""
Abstract email service for sending verification and password reset emails.
"""

import logging
import secrets
from typing import Optional

from app.redis_client import get_redis

logger = logging.getLogger(__name__)

# Config
TOKEN_EXPIRE_MINUTES = 60

async def generate_and_store_token(prefix: str, user_id: int) -> str:
    """Generate a secure token and store it in Redis."""
    token = secrets.token_urlsafe(32)
    key = f"{prefix}:{token}"
    client = await get_redis()
    await client.setex(key, TOKEN_EXPIRE_MINUTES * 60, str(user_id))
    return token

async def verify_and_consume_token(prefix: str, token: str) -> Optional[int]:
    """Verify a token and delete it (single-use). Return user_id if valid."""
    key = f"{prefix}:{token}"
    client = await get_redis()
    user_id_str = await client.get(key)
    if not user_id_str:
        return None
    await client.delete(key)
    return int(user_id_str)

async def send_verification_email(email: str, user_id: int) -> None:
    """Send an email verification link."""
    token = await generate_and_store_token("email_verify", user_id)
    # In a real app, send the email here (e.g. using SendGrid or SMTP)
    logger.info(f"EMAIL SENT TO {email}: Verify your email with token -> {token}")

async def send_password_reset_email(email: str, user_id: int) -> None:
    """Send a password reset link."""
    token = await generate_and_store_token("password_reset", user_id)
    # In a real app, send the email here
    logger.info(f"EMAIL SENT TO {email}: Reset your password with token -> {token}")
