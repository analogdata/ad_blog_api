from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    AUTHOR = "author"


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class UserBase(BaseModel):
    """Base model for user data"""

    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: UserRole = UserRole.AUTHOR


class UserCreate(UserBase):
    """Model for creating a new user"""

    password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    """Model for user login"""

    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Model for updating user data"""

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    profile_image: Optional[str] = None
    password: Optional[str] = None
    confirm_password: Optional[str] = None


class UserResponse(UserBase):
    """Response model for user operations"""

    id: int
    is_active: bool
    is_verified: bool
    profile_image: Optional[str] = None
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Model for JWT token response"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # Seconds until access token expires


class TokenData(BaseModel):
    """Model for JWT token payload data"""

    sub: str  # User ID
    email: str
    role: UserRole
    type: TokenType
    exp: datetime  # Expiration time
    iat: datetime  # Issued at time


class RefreshToken(BaseModel):
    """Model for refresh token request"""

    refresh_token: str


class PasswordReset(BaseModel):
    """Model for password reset request"""

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Model for password reset confirmation"""

    token: str
    password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)


class EmailVerification(BaseModel):
    """Model for email verification"""

    token: str
