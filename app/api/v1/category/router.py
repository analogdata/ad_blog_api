import logging
from fastapi import APIRouter, Depends, Query, Path, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import Optional, List
import re

from app.db.db_init import get_session
from app.api.v1.category import service
from app.api.v1.category.schema import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryListResponse,
    CategoryArticleCount,
)
from app.api.v1.auth.dependencies import AdminUser

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/",
    response_model=CategoryListResponse,
    summary="Get all categories",
    responses={
        200: {"description": "List of categories retrieved successfully"},
        500: {"description": "Internal server error"},
    },
)
async def get_categories(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search term for category name or description"),
    db: AsyncSession = Depends(get_session),
):
    """Get all categories with optional pagination and search"""
    try:
        categories, total = await service.get_categories(db=db, skip=skip, limit=limit, search=search)
        return CategoryListResponse(items=categories, total=total)
    except SQLAlchemyError as e:
        logger.error(f"Database error when fetching categories: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error when fetching categories: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new category (admin only)",
    responses={
        201: {"description": "Category created successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized"},
        409: {"description": "Category with this name already exists"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"},
    },
)
async def create_category(
    category_data: CategoryCreate, admin_user: AdminUser, db: AsyncSession = Depends(get_session)
):
    """Create a new category (admin only)

    This endpoint is restricted to admin users only.
    """
    try:
        # Check if a category with this name already exists
        existing_category = await service.get_category_by_name(db, category_data.name)
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=f"Category with name '{category_data.name}' already exists"
            )

        # Create the category
        category = await service.create_category(db=db, category_data=category_data)
        if not category:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create category")
        return category
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except IntegrityError as e:
        logger.error(f"Integrity error when creating category: {str(e)}")
        # Check for unique constraint violation on slug
        error_str = str(e)
        if "unique constraint" in error_str.lower() and "slug" in error_str.lower():
            # Extract the slug value from the error message
            slug_match = re.search(r"Key \(slug\)=\((.+?)\)", error_str)
            slug = slug_match.group(1) if slug_match else "unknown"
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=f"Category with slug '{slug}' already exists"
            )
        # Check for other unique constraint violations
        elif "unique constraint" in error_str.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="A category with these details already exists"
            )
        else:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database integrity error")
    except SQLAlchemyError as e:
        logger.error(f"Database error when creating category: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error when creating category: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.get(
    "/popular",
    response_model=List[CategoryArticleCount],
    summary="Get popular categories with article count",
    responses={
        200: {"description": "Popular categories retrieved successfully"},
        500: {"description": "Internal server error"},
    },
)
async def get_popular_categories(
    limit: int = Query(10, ge=1, le=50, description="Maximum number of categories to return"),
    db: AsyncSession = Depends(get_session),
):
    """Get popular categories with article count for widgets"""
    try:
        return await service.get_categories_with_article_count(db=db, limit=limit)
    except SQLAlchemyError as e:
        logger.error(f"Database error when fetching popular categories: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error when fetching popular categories: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.get(
    "/slug/{slug}",
    response_model=CategoryResponse,
    summary="Get category by slug",
    responses={
        200: {"description": "Category retrieved successfully"},
        404: {"description": "Category not found"},
        500: {"description": "Internal server error"},
    },
)
async def get_category_by_slug(slug: str = Path(...), db: AsyncSession = Depends(get_session)):
    """Get a specific category by its slug"""
    try:
        category = await service.get_category_by_slug(db=db, slug=slug)
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Category with slug '{slug}' not found")
        return category
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error when fetching category by slug '{slug}': {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error when fetching category by slug '{slug}': {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Get category by ID",
    responses={
        200: {"description": "Category retrieved successfully"},
        404: {"description": "Category not found"},
        500: {"description": "Internal server error"},
    },
)
async def get_category_by_id(category_id: int = Path(..., ge=1), db: AsyncSession = Depends(get_session)):
    """Get a specific category by its ID"""
    try:
        category = await service.get_category_by_id(db=db, category_id=category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Category with ID {category_id} not found"
            )
        return category
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error when fetching category ID {category_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error when fetching category ID {category_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Update a category (full update) (admin only)",
    responses={
        200: {"description": "Category updated successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized"},
        404: {"description": "Category not found"},
        409: {"description": "Category with this name already exists"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"},
    },
)
async def update_category(
    category_data: CategoryUpdate,
    admin_user: AdminUser,
    category_id: int = Path(..., ge=1),
    db: AsyncSession = Depends(get_session),
):
    """Update an existing category with a complete replacement (PUT) (admin only)

    This endpoint is restricted to admin users only.
    """
    try:
        # Check if category exists
        category = await service.get_category_by_id(db=db, category_id=category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Category with ID {category_id} not found"
            )

        # Check for name conflict if name is being updated
        if category_data.name and category_data.name != category.name:
            existing_category = await service.get_category_by_name(db, category_data.name)
            if existing_category:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Category with name '{category_data.name}' already exists",
                )

        # Update the category
        updated_category = await service.update_category(db=db, category_id=category_id, category_data=category_data)
        return updated_category
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error when updating category ID {category_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error when updating category ID {category_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.patch(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Partially update a category (admin only)",
    responses={
        200: {"description": "Category partially updated successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized"},
        404: {"description": "Category not found"},
        409: {"description": "Category with this name already exists"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"},
    },
)
async def patch_category(
    category_data: CategoryUpdate,
    admin_user: AdminUser,
    category_id: int = Path(..., ge=1),
    db: AsyncSession = Depends(get_session),
):
    """Partially update an existing category (PATCH) (admin only)

    This endpoint is restricted to admin users only.
    """
    try:
        # Check if category exists
        category = await service.get_category_by_id(db=db, category_id=category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Category with ID {category_id} not found"
            )

        # Check for name conflict if name is being updated
        if category_data.name is not None and category_data.name != category.name:
            existing_category = await service.get_category_by_name(db, category_data.name)
            if existing_category:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Category with name '{category_data.name}' already exists",
                )

        # Update the category
        updated_category = await service.patch_category(db=db, category_id=category_id, category_data=category_data)
        return updated_category
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error when patching category ID {category_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error when patching category ID {category_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.delete(
    "/{category_id}",
    summary="Delete a category (admin only)",
    responses={
        200: {"description": "Category deleted successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized"},
        404: {"description": "Category not found"},
        500: {"description": "Internal server error"},
    },
)
async def delete_category(
    admin_user: AdminUser, category_id: int = Path(..., ge=1), db: AsyncSession = Depends(get_session)
):
    """Delete a category (admin only)

    This endpoint is restricted to admin users only.
    """
    try:
        # Check if category exists
        category = await service.get_category_by_id(db=db, category_id=category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Category with ID {category_id} not found"
            )

        # Delete the category
        result = await service.delete_category(db=db, category_id=category_id)
        return result
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error when deleting category ID {category_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error when deleting category ID {category_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")
