"""
Authentication router.
"""

from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
import jwt
from pydantic import BaseModel, EmailStr, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request

from app.api import deps
from app.config import settings
from app.core import security
from app.crud.user import authenticate_user, get_user_by_id, get_user_by_email, update_user
from app.database import get_db
from app.schemas.token import Token, TokenPayload
from app.schemas.user import UserRead
from app.services.auth_service import is_token_revoked, revoke_token, revoke_all_sessions, is_session_valid
from app.services.email_service import send_password_reset_email, verify_and_consume_token
from app.core.security_controls import check_rate_limit, check_login_allowed, record_failed_login, reset_login_attempts
router = APIRouter(prefix="/auth", tags=["auth"])

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


@router.post("/login/access-token", response_model=Token)
async def login_access_token(
    request: Request,
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """OAuth2 compatible token login, get an access token for future requests."""
    await check_rate_limit(request, "login")
    await check_login_allowed(form_data.username)
    user = await authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        await record_failed_login(form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    elif not user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified")

    await reset_login_attempts(form_data.username)

    access_token = security.create_access_token(subject=user.id)
    refresh_token = security.create_refresh_token(subject=user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/login/test-token", response_model=UserRead)
async def test_token(current_user=Depends(deps.get_current_user)) -> Any:
    """Test access token."""
    return current_user


@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: Request,
    refresh_token: str,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Refresh tokens using a refresh token."""
    await check_rate_limit(request, "refresh")
    if await is_token_revoked(refresh_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
        )

    try:
        payload = jwt.decode(
            refresh_token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        
        if token_data.type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
    except (jwt.PyJWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    user = await get_user_by_id(db, user_id=int(token_data.sub))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    # Check if session globally revoked
    if token_data.iat:
        if not await is_session_valid(user.id, int(token_data.iat)):
            # Reuse detection logic here: revoke entire family? Global revocation does this.
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session has been revoked",
            )

    # Issue new tokens
    access_token = security.create_access_token(subject=user.id)
    new_refresh_token = security.create_refresh_token(subject=user.id)
    
    # Revoke old refresh token (refresh token rotation)
    expires_in = settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60
    await revoke_token(refresh_token, expires_in=expires_in)

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@router.post("/logout")
async def logout(
    refresh_token: str,
    current_user=Depends(deps.get_current_user),
) -> Any:
    """Logout by revoking the refresh token."""
    expires_in = settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60
    await revoke_token(refresh_token, expires_in=expires_in)
    return {"message": "Successfully logged out"}


@router.post("/password-reset/request")
async def request_password_reset(
    request: Request,
    data: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Request a password reset email."""
    await check_rate_limit(request, "password_reset_request")

    user = await get_user_by_email(db, email=data.email)
    if user:
        await send_password_reset_email(user.email, user.id)
    # Always return 200 to prevent email enumeration
    return {"message": "If an account with this email exists, a password reset link has been sent."}


@router.post("/password-reset/confirm")
async def confirm_password_reset(
    request: Request,
    data: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Confirm password reset using token."""
    await check_rate_limit(request, "password_reset_confirm")
    
    user_id = await verify_and_consume_token("password_reset", data.token)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    user = await get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Update password
    new_hashed_password = security.get_password_hash(data.new_password)
    await update_user(db, user, {"hashed_password": new_hashed_password})
    
    # Revoke all sessions globally
    await revoke_all_sessions(user.id)
    
    return {"message": "Password successfully reset. All sessions have been logged out."}
