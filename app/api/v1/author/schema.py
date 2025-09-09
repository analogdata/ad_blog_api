from pydantic import BaseModel, Field, RootModel
from typing import Optional, Dict, List
from datetime import datetime


class SocialMediaDict(RootModel):
    """Model for social media links"""

    root: Dict[str, str]


class AuthorBase(BaseModel):
    """Base model for author data"""

    name: str = Field(..., min_length=1, max_length=100, description="Author name")
    bio: Optional[str] = Field(None, description="Author biography")
    profile_image: Optional[str] = Field(None, description="URL to author profile image")
    website: Optional[str] = Field(None, description="Author website URL")
    social_media: Optional[Dict[str, str]] = Field(None, description="Social media links")


class AuthorCreate(AuthorBase):
    """Request model for author creation"""

    pass


class AuthorUpdate(AuthorBase):
    """Request model for full author update"""

    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Author name")


class AuthorResponse(AuthorBase):
    """Response model for author data"""

    id: int
    slug: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AuthorListResponse(BaseModel):
    """Response model for paginated author list"""

    items: List[AuthorResponse]
    total: int


class AuthorArticleCount(BaseModel):
    """Response model for author with article count"""

    id: int
    name: str
    slug: str
    article_count: int
    profile_image: Optional[str] = None


class SocialMediaUpdate(BaseModel):
    """Request model for updating a single social media link"""

    platform: str = Field(..., description="Social media platform name")
    url: str = Field(..., description="Social media profile URL")
