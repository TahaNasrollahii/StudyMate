"""
User router.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from pydantic import BaseModel
from fastapi import Request

from app.api import deps
from app.crud.user import create_user, get_user_by_email, get_user_by_id, update_user
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserRead
from app.core.security_controls import check_rate_limit
from app.services.email_service import send_verification_email, verify_and_consume_token

class VerifyEmailRequest(BaseModel):
    token: str

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(
    request: Request,
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Register a new user."""
    await check_rate_limit(request, "register")
    user = await get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )
    user = await create_user(db, user_in=user_in)
    await send_verification_email(user.email, user.id)
    return user


@router.post("/verify-email")
async def verify_email(
    request: Request,
    data: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Verify email address using token."""
    await check_rate_limit(request, "verify_email")
    user_id = await verify_and_consume_token("email_verify", data.token)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")
    
    user = await get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    await update_user(db, user, {"is_verified": True})
    return {"message": "Email successfully verified."}


@router.get("/me", response_model=UserRead)
async def read_user_me(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Get current user."""
    return current_user
