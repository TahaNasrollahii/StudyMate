"""
Pydantic schemas for User.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Shared properties."""
    email: EmailStr


class UserCreate(UserBase):
    """Properties to receive via API on creation."""
    password: str = Field(..., min_length=8, description="User password")


class UserUpdate(UserBase):
    """Properties to receive via API on update."""
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class UserRead(UserBase):
    """Properties to return via API."""
    id: int
    is_active: bool
    is_verified: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
