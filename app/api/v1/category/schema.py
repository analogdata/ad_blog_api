from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CategoryBase(BaseModel):
    """Base model for category data"""
    name: str = Field(..., min_length=1, max_length=100, description="Category name")
    description: Optional[str] = Field(None, description="Category description")
    category_icon: Optional[str] = Field(None, description="URL to category icon")
    category_image: Optional[str] = Field(None, description="URL to category image")


class CategoryCreate(CategoryBase):
    """Request model for category creation"""
    pass


class CategoryUpdate(CategoryBase):
    """Request model for full category update"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Category name")


class CategoryResponse(CategoryBase):
    """Response model for category data"""
    id: int
    slug: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CategoryListResponse(BaseModel):
    """Response model for paginated category list"""
    items: List[CategoryResponse]
    total: int


class CategoryArticleCount(BaseModel):
    """Response model for category with article count"""
    id: int
    name: str
    slug: str
    article_count: int
    category_icon: Optional[str] = None
