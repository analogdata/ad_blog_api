from datetime import datetime
import re
from typing import Dict, Optional, Any, ClassVar
from pydantic import HttpUrl, model_validator
from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime


class URLValidationMixin(SQLModel):
    """Mixin to provide URL validation functionality"""

    __abstract__ = True

    @staticmethod
    def validate_url(url: str) -> str:
        """Validate and normalize a URL"""
        # Add https:// prefix if not present
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"

        # Basic URL validation
        if not re.match(r"^https?://[\w.-]+\.[a-zA-Z]{2,}", url):
            raise ValueError(f"Invalid URL: {url}")

        return url

    def validate_url_dict(self, url_dict: Dict[str, str]) -> Dict[str, str]:
        """Validate all URLs in a dictionary"""
        if not url_dict:
            return {}

        validated_dict = {}
        for key, url in url_dict.items():
            validated_dict[key] = self.validate_url(url)

        return validated_dict


class TimestampMixin(SQLModel):
    """Mixin to provide created_at and updated_at fields"""

    __abstract__ = True

    # IMPORTANT: Optional + default=None so SQLAlchemy will use server_default
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=False), server_default=func.now(), nullable=False),
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now(), nullable=False),
    )


class SoftDeleteMixin(SQLModel):
    """Mixin to provide soft delete functionality"""

    __abstract__ = True

    is_deleted: bool = Field(default=False, index=True)
    deleted_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=False)))

    def soft_delete(self) -> None:
        """Mark as deleted without removing from database"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()

    def restore(self) -> None:
        """Restore a soft-deleted item"""
        self.is_deleted = False
        self.deleted_at = None


class AuditMixin(SQLModel):
    """Mixin to track who created and modified records"""

    __abstract__ = True

    created_by_id: Optional[int] = Field(default=None, foreign_key="users.id")
    updated_by_id: Optional[int] = Field(default=None, foreign_key="users.id")

    def set_created_by(self, user_id: int) -> None:
        """Set the user who created this record"""
        self.created_by_id = user_id

    def set_updated_by(self, user_id: int) -> None:
        """Set the user who last updated this record"""
        self.updated_by_id = user_id


class HttpUrlFieldMixin(SQLModel):
    """Mixin to handle HttpUrl fields in SQLModel

    This mixin automatically validates URL fields defined in url_fields.
    URLs are stored as strings in the database but validated as HttpUrl.
    """

    # Define which fields should be treated as URLs
    url_fields: ClassVar[list[str]] = []

    @model_validator(mode="after")
    def validate_url_fields(self) -> Any:
        """Validate all URL fields and ensure they are stored as strings"""
        for field_name in self.__class__.url_fields:
            if hasattr(self, field_name):
                value = getattr(self, field_name)
                if value is not None:
                    # Convert HttpUrl objects to strings
                    if hasattr(value, "__str__") and not isinstance(value, str):
                        # This handles HttpUrl objects from Pydantic
                        value_str = str(value)
                        setattr(self, field_name, value_str)
                        value = value_str
                    
                    # Validate URL format
                    try:
                        # This will raise an error if invalid
                        HttpUrl.validate(value)
                    except Exception as e:
                        raise ValueError(f"Invalid URL in {field_name}: {value}. Error: {e}")
        return self


class SlugGeneratorMixin(SQLModel):
    """Mixin to generate slugs from a specified field"""

    __abstract__ = True

    # Define which field to use as source for the slug
    slug_source_field: ClassVar[str] = ""

    @classmethod
    def generate_slug(cls, text: str) -> str:
        """Generate a URL-friendly slug from text"""
        # Convert to lowercase
        slug = text.lower()
        # Replace spaces with hyphens
        slug = re.sub(r"\s+", "-", slug)
        # Remove special characters
        slug = re.sub(r"[^\w\-]", "", slug)
        # Remove multiple consecutive hyphens
        slug = re.sub(r"-+", "-", slug)
        # Remove leading/trailing hyphens
        slug = slug.strip("-")
        return slug

    @model_validator(mode="after")
    def generate_slug_if_missing(self) -> Any:
        """Generate slug from source field if slug is missing"""
        if self.__class__.slug_source_field and hasattr(self, "slug"):
            # If slug is not set but source field is, generate slug
            if not getattr(self, "slug", None) and getattr(self, self.__class__.slug_source_field, None):
                source_value = getattr(self, self.__class__.slug_source_field)
                setattr(self, "slug", self.generate_slug(source_value))
        return self
