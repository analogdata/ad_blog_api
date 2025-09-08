from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING, Dict, Any
import enum
from pydantic import EmailStr, model_validator
from sqlmodel import SQLModel, Field, Relationship, Column, JSON
import bcrypt
import secrets

if TYPE_CHECKING:
    from app.db.models.permission import Permission
    from app.db.models.author import Author


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    AUTHOR = "author"


class User(SQLModel, table=True):
    __tablename__ = "users"
    id: int = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    password: str = Field()
    first_name: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)
    role: UserRole = Field(default=UserRole.AUTHOR)
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    verification_token: Optional[str] = Field(default=None)
    verified_at: Optional[datetime] = Field(default=None)
    last_login: Optional[datetime] = Field(default=None)
    profile_image: Optional[str] = Field(default=None)
    preferences: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    permissions: List["Permission"] = Relationship(back_populates="user")
    author_id: Optional[int] = Field(default=None, foreign_key="authors.id")
    author: Optional["Author"] = Relationship(back_populates="user")

    def __init__(self, **data):
        # Hash password if provided in plain text
        if "password" in data and not data["password"].startswith("$2b$"):
            data["password"] = self.hash_password(data["password"])
        super().__init__(**data)

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password for storing."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    def verify_password(self, password: str) -> bool:
        """Check if provided password matches stored hash."""
        return bcrypt.checkpw(password.encode("utf-8"), self.password.encode("utf-8"))

    def generate_verification_token(self) -> str:
        """Generate a verification token for email verification."""
        token = secrets.token_urlsafe(32)
        self.verification_token = token
        return token

    def verify_user(self) -> None:
        """Mark user as verified."""
        self.is_verified = True
        self.verified_at = datetime.now(timezone.utc)
        self.verification_token = None

    def update_last_login(self) -> None:
        """Update the last login timestamp."""
        self.last_login = datetime.now(timezone.utc)

    def has_permission(self, permission_name: str) -> bool:
        """Check if user has a specific permission."""
        return any(p.name == permission_name for p in self.permissions)

    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.role == UserRole.ADMIN

    def can_edit_article(self, article) -> bool:
        """Check if user can edit the given article"""
        if self.is_admin():
            return True
        return self.author and self.author.id == article.author_id

    def get_full_name(self) -> str:
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        return "User"

    @model_validator(mode="after")
    def validate_email(self) -> "User":
        """Validate email format."""
        if self.email:
            # Use pydantic's EmailStr validation
            EmailStr.validate(self.email)
        return self
