from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

from app.api.v1.auth.schema import UserRole


class UserProfileUpdate(BaseModel):
    """Model for updating user profile"""

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    profile_image: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    confirm_password: Optional[str] = Field(None, min_length=8)


class UserResponse(BaseModel):
    """Response model for user profile"""

    id: int
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: UserRole
    is_active: bool
    is_verified: bool
    profile_image: Optional[str] = None
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AdminUserResponse(UserResponse):
    """Extended user response model for admin users"""

    # Additional fields that only admins can see
    verification_token: Optional[str] = None

    class Config:
        from_attributes = True


class ProfileUpdateResponse(BaseModel):
    """Response model for profile update operations"""

    user: UserResponse
    message: str
    email_changed: bool = False
    verification_required: bool = False


class AdminPasswordResetRequest(BaseModel):
    """Request model for admin password reset"""

    password: Optional[str] = Field(
        None, min_length=8, description="Custom password to set. If not provided, a random password will be generated."
    )
