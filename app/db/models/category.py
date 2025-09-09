from datetime import datetime
from typing import Optional, List, TYPE_CHECKING, ClassVar
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, func
from app.db.models.base import HttpUrlFieldMixin, SlugGeneratorMixin

if TYPE_CHECKING:
    from app.db.models.article import Article


class Category(HttpUrlFieldMixin, SlugGeneratorMixin, SQLModel, table=True):
    # Define URL fields for validation
    url_fields: ClassVar[list[str]] = ["category_icon", "category_image"]

    # Define source field for slug generation
    slug_source_field: ClassVar[str] = "name"
    __tablename__ = "categories"
    id: int = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: Optional[str] = Field(default=None)
    slug: str = Field(unique=True, index=True)
    category_icon: Optional[str] = Field(default=None)
    category_image: Optional[str] = Field(default=None)
    
    # Timestamps
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=False), server_default=func.now(), nullable=False),
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now(), nullable=False),
    )

    # Relationships
    articles: List["Article"] = Relationship(back_populates="category")

    def __init__(self, **data):
        # Slug generation is now handled by SlugGeneratorMixin
        super().__init__(**data)

    # generate_slug method now comes from SlugGeneratorMixin
