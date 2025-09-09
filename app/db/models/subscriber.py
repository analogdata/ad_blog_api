from datetime import datetime
import secrets
from typing import Optional
from pydantic import EmailStr, model_validator
from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime


class Subscriber(SQLModel, table=True):
    __tablename__ = "subscribers"
    # Primary key and identification
    id: int = Field(default=None, primary_key=True)
    email: EmailStr = Field(unique=True, index=True)

    # Status fields
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    verification_token: Optional[str] = Field(default=None)

    # Timestamp fields
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=False), server_default=func.now(), nullable=False),
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now(), nullable=False),
    )
    subscribed_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=False), server_default=func.now(), nullable=False)
    )
    verified_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=False)))
    unsubscribed_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=False)))

    @model_validator(mode="after")
    def validate_subscriber(self) -> "Subscriber":
        """Validate subscriber data and generate verification token if needed"""
        # Generate verification token if not provided and not verified
        if not self.is_verified and not self.verification_token:
            self.verification_token = self.generate_verification_token()
        return self

    @classmethod
    def generate_verification_token(cls) -> str:
        """Generate a secure random verification token"""
        return secrets.token_urlsafe(32)

    def verify(self) -> None:
        """Mark the subscriber as verified"""
        self.is_verified = True
        self.verified_at = datetime.utcnow()
        self.verification_token = None

    def unsubscribe(self) -> None:
        """Mark the subscriber as unsubscribed"""
        self.is_active = False
        self.unsubscribed_at = datetime.utcnow()

    def resubscribe(self) -> None:
        """Reactivate a previously unsubscribed subscriber"""
        if not self.is_active:
            self.is_active = True
            self.unsubscribed_at = None
            # If they were previously verified, keep that status
            if not self.is_verified:
                self.verification_token = self.generate_verification_token()
