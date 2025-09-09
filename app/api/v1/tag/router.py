import logging
from fastapi import APIRouter, Depends, Query, Path, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import Optional, List
import re

from app.db.db_init import get_session
from app.api.v1.tag import service
from app.api.v1.tag.schema import TagCreate, TagUpdate, TagResponse, TagListResponse, TagArticleCount
from app.api.v1.auth.dependencies import AdminUser

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/",
    response_model=TagListResponse,
    summary="Get all tags",
    responses={
        200: {"description": "List of tags retrieved successfully"},
        500: {"description": "Internal server error"},
    },
)
async def get_tags(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search term for tag name or description"),
    db: AsyncSession = Depends(get_session),
):
    """Get all tags with optional pagination and search"""
    try:
        tags, total = await service.get_tags(db=db, skip=skip, limit=limit, search=search)
        return TagListResponse(items=tags, total=total)
    except SQLAlchemyError as e:
        logger.error(f"Database error when fetching tags: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error when fetching tags: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.post(
    "/",
    response_model=TagResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new tag (admin only)",
    responses={
        201: {"description": "Tag created successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized"},
        409: {"description": "Tag with this name already exists"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"},
    },
)
async def create_tag(
    tag_data: TagCreate, 
    admin_user: AdminUser,
    db: AsyncSession = Depends(get_session)
):
    """Create a new tag (admin only)
    
    This endpoint is restricted to admin users only.
    """
    try:
        # Check if a tag with this name already exists
        existing_tag = await service.get_tag_by_name(db, tag_data.name)
        if existing_tag:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=f"Tag with name '{tag_data.name}' already exists"
            )

        # Create the tag
        tag = await service.create_tag(db=db, tag_data=tag_data)
        if not tag:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create tag")
        return tag
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except IntegrityError as e:
        logger.error(f"Integrity error when creating tag: {str(e)}")
        # Check for unique constraint violation on slug
        error_str = str(e)
        if "unique constraint" in error_str.lower() and "slug" in error_str.lower():
            # Extract the slug value from the error message
            slug_match = re.search(r"Key \(slug\)=\((.+?)\)", error_str)
            slug = slug_match.group(1) if slug_match else "unknown"
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Tag with slug '{slug}' already exists"
            )
        # Check for other unique constraint violations
        elif "unique constraint" in error_str.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A tag with these details already exists"
            )
        else:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database integrity error")
    except SQLAlchemyError as e:
        logger.error(f"Database error when creating tag: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error when creating tag: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.get(
    "/popular",
    response_model=List[TagArticleCount],
    summary="Get popular tags with article count",
    responses={
        200: {"description": "Popular tags retrieved successfully"},
        500: {"description": "Internal server error"},
    },
)
async def get_popular_tags(
    limit: int = Query(10, ge=1, le=50, description="Maximum number of tags to return"),
    db: AsyncSession = Depends(get_session),
):
    """Get popular tags with article count for widgets"""
    try:
        return await service.get_tags_with_article_count(db=db, limit=limit)
    except SQLAlchemyError as e:
        logger.error(f"Database error when fetching popular tags: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error when fetching popular tags: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.get(
    "/slug/{slug}",
    response_model=TagResponse,
    summary="Get tag by slug",
    responses={
        200: {"description": "Tag retrieved successfully"},
        404: {"description": "Tag not found"},
        500: {"description": "Internal server error"},
    },
)
async def get_tag_by_slug(slug: str = Path(...), db: AsyncSession = Depends(get_session)):
    """Get a specific tag by its slug"""
    try:
        tag = await service.get_tag_by_slug(db=db, slug=slug)
        if not tag:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tag with slug '{slug}' not found")
        return tag
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error when fetching tag by slug '{slug}': {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error when fetching tag by slug '{slug}': {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.get(
    "/{tag_id}",
    response_model=TagResponse,
    summary="Get tag by ID",
    responses={
        200: {"description": "Tag retrieved successfully"},
        404: {"description": "Tag not found"},
        500: {"description": "Internal server error"},
    },
)
async def get_tag_by_id(tag_id: int = Path(..., ge=1), db: AsyncSession = Depends(get_session)):
    """Get a specific tag by its ID"""
    try:
        tag = await service.get_tag_by_id(db=db, tag_id=tag_id)
        if not tag:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tag with ID {tag_id} not found")
        return tag
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error when fetching tag ID {tag_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error when fetching tag ID {tag_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.put(
    "/{tag_id}",
    response_model=TagResponse,
    summary="Update a tag (full update) (admin only)",
    responses={
        200: {"description": "Tag updated successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized"},
        404: {"description": "Tag not found"},
        409: {"description": "Tag with this name already exists"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"},
    },
)
async def update_tag(
    tag_data: TagUpdate, 
    admin_user: AdminUser,
    tag_id: int = Path(..., ge=1), 
    db: AsyncSession = Depends(get_session)
):
    """Update an existing tag with a complete replacement (PUT) (admin only)
    
    This endpoint is restricted to admin users only.
    """
    try:
        # Check if tag exists
        tag = await service.get_tag_by_id(db=db, tag_id=tag_id)
        if not tag:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tag with ID {tag_id} not found")

        # Check for name conflict if name is being updated
        if tag_data.name and tag_data.name != tag.name:
            existing_tag = await service.get_tag_by_name(db, tag_data.name)
            if existing_tag:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, detail=f"Tag with name '{tag_data.name}' already exists"
                )

        # Update the tag
        updated_tag = await service.update_tag(db=db, tag_id=tag_id, tag_data=tag_data)
        return updated_tag
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error when updating tag ID {tag_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error when updating tag ID {tag_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.patch(
    "/{tag_id}",
    response_model=TagResponse,
    summary="Partially update a tag (admin only)",
    responses={
        200: {"description": "Tag partially updated successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized"},
        404: {"description": "Tag not found"},
        409: {"description": "Tag with this name already exists"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"},
    },
)
async def patch_tag(
    tag_data: TagUpdate, 
    admin_user: AdminUser,
    tag_id: int = Path(..., ge=1), 
    db: AsyncSession = Depends(get_session)
):
    """Partially update an existing tag (PATCH) (admin only)
    
    This endpoint is restricted to admin users only.
    """
    try:
        # Check if tag exists
        tag = await service.get_tag_by_id(db=db, tag_id=tag_id)
        if not tag:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tag with ID {tag_id} not found")

        # Check for name conflict if name is being updated
        if tag_data.name is not None and tag_data.name != tag.name:
            existing_tag = await service.get_tag_by_name(db, tag_data.name)
            if existing_tag:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, detail=f"Tag with name '{tag_data.name}' already exists"
                )

        # Update the tag
        updated_tag = await service.patch_tag(db=db, tag_id=tag_id, tag_data=tag_data)
        return updated_tag
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error when patching tag ID {tag_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error when patching tag ID {tag_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.delete(
    "/{tag_id}",
    summary="Delete a tag (admin only)",
    responses={
        200: {"description": "Tag deleted successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized"},
        404: {"description": "Tag not found"},
        500: {"description": "Internal server error"},
    },
)
async def delete_tag(
    admin_user: AdminUser,
    tag_id: int = Path(..., ge=1), 
    db: AsyncSession = Depends(get_session)
):
    """Delete a tag (admin only)
    
    This endpoint is restricted to admin users only.
    """
    try:
        # Check if tag exists
        tag = await service.get_tag_by_id(db=db, tag_id=tag_id)
        if not tag:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tag with ID {tag_id} not found")

        # Delete the tag
        result = await service.delete_tag(db=db, tag_id=tag_id)
        return result
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error when deleting tag ID {tag_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error when deleting tag ID {tag_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")
