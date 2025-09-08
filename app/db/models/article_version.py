from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Text
from app.db.models.base import TimestampMixin, AuditMixin

if TYPE_CHECKING:
    from app.db.models.article import Article


class ArticleVersion(TimestampMixin, AuditMixin, SQLModel, table=True):
    """Stores versions of article content for revision history"""

    __tablename__ = "article_versions"

    id: int = Field(default=None, primary_key=True)
    article_id: int = Field(foreign_key="articles.id", index=True)
    version_number: int = Field(index=True)
    title: str = Field()
    content: Optional[str] = Field(default=None, sa_column=Column(Text))
    summary: Optional[str] = Field(default=None)
    change_comment: Optional[str] = Field(default=None)

    # Relationship
    article: "Article" = Relationship(back_populates="versions")

    class Config:
        arbitrary_types_allowed = True
