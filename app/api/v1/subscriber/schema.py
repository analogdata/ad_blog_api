from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr


class SubscriberBase(BaseModel):
    """Base model for subscriber data"""

    email: EmailStr


class SubscriberCreate(SubscriberBase):
    """Model for creating a new subscriber"""

    pass


class SubscriberUpdate(BaseModel):
    """Model for updating a subscriber"""

    is_active: Optional[bool] = None


class SubscriberResponse(SubscriberBase):
    """Response model for subscriber data"""

    id: int
    is_active: bool
    is_verified: bool
    verification_token: Optional[str] = None
    created_at: datetime
    subscribed_at: datetime
    verified_at: Optional[datetime] = None
    unsubscribed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SubscriberVerify(BaseModel):
    """Model for verifying a subscriber"""

    token: str


class SubscriberListResponse(BaseModel):
    """Response model for a list of subscribers"""

    items: List[SubscriberResponse]
    total: int
