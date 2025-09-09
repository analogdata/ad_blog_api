from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime
import re


class TagBase(BaseModel):
    """Base model for tag data"""

    name: str
    description: Optional[str] = None
    tag_icon: Optional[str] = None
    tag_image: Optional[str] = None

    @field_validator("tag_icon", "tag_image")
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate URL fields"""
        if v is None:
            return v
        # Simple URL validation
        url_pattern = re.compile(
            r"^https?://"
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+"
            r"(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"
            r"localhost|"
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
            r"(?::\d+)?"
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )
        if not url_pattern.match(v):
            raise ValueError(f"Invalid URL format: {v}")
        return v


class TagCreate(TagBase):
    """Model for creating a new tag"""

    pass


class TagUpdate(BaseModel):
    """Model for updating an existing tag"""

    name: Optional[str] = None
    description: Optional[str] = None
    tag_icon: Optional[str] = None
    tag_image: Optional[str] = None

    @field_validator("tag_icon", "tag_image")
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate URL fields"""
        if v is None:
            return v
        # Simple URL validation
        url_pattern = re.compile(
            r"^https?://"
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+"
            r"(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"
            r"localhost|"
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
            r"(?::\d+)?"
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )
        if not url_pattern.match(v):
            raise ValueError(f"Invalid URL format: {v}")
        return v


class Tag(TagBase):
    """Complete tag model with all fields"""

    id: int
    slug: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TagResponse(Tag):
    """Response model for tag operations"""

    pass


class TagListResponse(BaseModel):
    """Response model for listing tags"""

    items: List[Tag]
    total: int


class TagArticleCount(Tag):
    """Tag model with article count"""

    article_count: int
