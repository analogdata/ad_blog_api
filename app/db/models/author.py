from datetime import datetime
from typing import Optional, Dict, List, TYPE_CHECKING, ClassVar
from pydantic import model_validator
from sqlmodel import SQLModel, Field, Column, JSON, Relationship
from sqlalchemy import Column as SQLAColumn, DateTime, func
from app.db.models.base import (
    URLValidationMixin,
    HttpUrlFieldMixin,
    SlugGeneratorMixin,
)

if TYPE_CHECKING:
    from app.db.models.article import Article
    from app.db.models.user import User


class Author(
    URLValidationMixin,
    HttpUrlFieldMixin,
    SlugGeneratorMixin,
    SQLModel,
    table=True,
):
    # Define URL fields for validation
    url_fields: ClassVar[list[str]] = ["profile_image", "website"]

    # Define source field for slug generation
    slug_source_field: ClassVar[str] = "name"
    __tablename__ = "authors"
    id: int = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    bio: Optional[str] = Field(default=None)
    slug: str = Field(unique=True, index=True)
    profile_image: Optional[str] = Field(default=None)
    website: Optional[str] = Field(default=None)
    social_media: Optional[Dict[str, str]] = Field(default=None, sa_column=Column(JSON))

    # Timestamps
    created_at: datetime | None = Field(
        default=None,
        sa_column=SQLAColumn(DateTime(timezone=False), server_default=func.now(), nullable=False),
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_column=SQLAColumn(DateTime(timezone=False), server_default=func.now(), onupdate=func.now(), nullable=False),
    )

    # Relationships
    articles: List["Article"] = Relationship(back_populates="author")
    user: Optional["User"] = Relationship(back_populates="author")

    @model_validator(mode="after")
    def validate_social_media(self) -> "Author":
        """Validate social media URLs"""
        if self.social_media:
            self.social_media = self.validate_url_dict(self.social_media)
        return self

    def __init__(self, **data):
        # Slug generation is now handled by SlugGeneratorMixin
        super().__init__(**data)

    def add_social_media(self, platform: str, url: str) -> None:
        """Add or update a social media profile."""
        if self.social_media is None:
            self.social_media = {}
        self.social_media[platform] = self.validate_url(url)

    def remove_social_media(self, platform: str) -> bool:
        """Remove a social media profile. Returns True if successful."""
        if self.social_media and platform in self.social_media:
            del self.social_media[platform]
            return True
        return False

    def get_social_media_platforms(self) -> List[str]:
        """Get a list of all social media platforms for this author."""
        if self.social_media:
            return list(self.social_media.keys())
        return []

    # generate_slug method now comes from SlugGeneratorMixin
