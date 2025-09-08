from typing import Optional
from sqlmodel import SQLModel, Field


class ArticleTag(SQLModel, table=True):
    """Link table for many-to-many relationship between Article and Tag"""

    __tablename__ = "article_tags"

    article_id: Optional[int] = Field(
        default=None, foreign_key="articles.id", primary_key=True
    )
    tag_id: Optional[int] = Field(default=None, foreign_key="tags.id", primary_key=True)
