from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Text, DateTime, func
from app.db.models.base import AuditMixin

if TYPE_CHECKING:
    from app.db.models.article import Article


class ArticleVersion(AuditMixin, SQLModel, table=True):
    """Stores versions of article content for revision history"""

    __tablename__ = "article_versions"

    id: int = Field(default=None, primary_key=True)
    article_id: int = Field(foreign_key="articles.id", index=True)
    version_number: int = Field(index=True)
    title: str = Field()
    content: Optional[str] = Field(default=None, sa_column=Column(Text))
    summary: Optional[str] = Field(default=None)
    change_comment: Optional[str] = Field(default=None)

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
    article: "Article" = Relationship(back_populates="versions")

    class Config:
        arbitrary_types_allowed = True
