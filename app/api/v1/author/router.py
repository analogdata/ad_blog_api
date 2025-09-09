import logging
import re
from fastapi import APIRouter, Depends, Query, Path, status, HTTPException, Body, Security
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import Optional, List

from app.db.db_init import get_session
from app.api.v1.author import service
from app.api.v1.author.schema import (
    AuthorCreate,
    AuthorUpdate,
    AuthorResponse,
    AuthorListResponse,
    AuthorArticleCount,
    SocialMediaUpdate,
)
from app.api.v1.auth.dependencies import get_admin_user, get_author_user
from app.db.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/",
    response_model=AuthorListResponse,
    summary="Get all authors",
    responses={
        200: {"description": "List of authors retrieved successfully"},
        500: {"description": "Internal server error"},
    },
)
async def get_authors(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search term for author name or bio"),
    db: AsyncSession = Depends(get_session),
):
    """Get all authors with optional pagination and search"""
    try:
        authors, total = await service.get_authors(db=db, skip=skip, limit=limit, search=search)
        return AuthorListResponse(items=authors, total=total)
    except SQLAlchemyError as e:
        logger.error(f"Database error when fetching authors: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error when fetching authors: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.post(
    "/",
    response_model=AuthorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new author (admin only)",
    responses={
        201: {"description": "Author created successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized"},
        409: {"description": "Author with this name already exists"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"},
    },
)
async def create_author(
    author_data: AuthorCreate,
    db: AsyncSession = Depends(get_session),
    admin_user: User = Security(get_admin_user),
):
    """Create a new author (admin only)

    This endpoint is restricted to admin users only.
    """
    try:
        # Check if an author with this name already exists
        existing_author = await service.get_author_by_name(db, author_data.name)
        if existing_author:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=f"Author with name '{author_data.name}' already exists"
            )

        # Create the author
        author = await service.create_author(db=db, author_data=author_data)
        if not author:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create author")
        return author
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except IntegrityError as e:
        logger.error(f"Integrity error when creating author: {str(e)}")
        # Check for unique constraint violation on slug
        error_str = str(e)
        if "unique constraint" in error_str.lower() and "slug" in error_str.lower():
            # Extract the slug value from the error message
            slug_match = re.search(r"Key \(slug\)=\((.+?)\)", error_str)
            slug = slug_match.group(1) if slug_match else "unknown"
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=f"Author with slug '{slug}' already exists"
            )
        # Check for other unique constraint violations
        elif "unique constraint" in error_str.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="An author with these details already exists"
            )
        else:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database integrity error")
    except SQLAlchemyError as e:
        logger.error(f"Database error when creating author: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error when creating author: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.get(
    "/popular",
    response_model=List[AuthorArticleCount],
    summary="Get popular authors with article count",
    responses={
        200: {"description": "Popular authors retrieved successfully"},
        500: {"description": "Internal server error"},
    },
)
async def get_popular_authors(
    limit: int = Query(10, ge=1, le=50, description="Maximum number of authors to return"),
    db: AsyncSession = Depends(get_session),
):
    """Get popular authors with article count for widgets"""
    try:
        return await service.get_authors_with_article_count(db=db, limit=limit)
    except SQLAlchemyError as e:
        logger.error(f"Database error when fetching popular authors: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error when fetching popular authors: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.get(
    "/slug/{slug}",
    response_model=AuthorResponse,
    summary="Get author by slug",
    responses={
        200: {"description": "Author retrieved successfully"},
        404: {"description": "Author not found"},
        500: {"description": "Internal server error"},
    },
)
async def get_author_by_slug(slug: str = Path(...), db: AsyncSession = Depends(get_session)):
    """Get a specific author by its slug"""
    try:
        author = await service.get_author_by_slug(db=db, slug=slug)
        if not author:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Author with slug '{slug}' not found")
        return author
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error when fetching author by slug '{slug}': {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error when fetching author by slug '{slug}': {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.get(
    "/me",
    response_model=AuthorResponse,
    summary="Get author's own profile (author only)",
    responses={
        200: {"description": "Author profile retrieved successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized"},
        404: {"description": "Author profile not found"},
        500: {"description": "Internal server error"},
    },
)
async def get_own_author_profile(
    db: AsyncSession = Depends(get_session),
    current_user: User = Security(get_author_user),
):
    """Get author's own profile (author only)

    This endpoint allows authors to retrieve their own profile information.
    Only users with the AUTHOR role can access this endpoint.
    """
    try:
        # Check if user has an author profile
        if not current_user.author_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You don't have an author profile")

        # Get author profile
        author = await service.get_author_by_id(db=db, author_id=current_user.author_id)
        if not author:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author profile not found")

        return author

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error when retrieving author profile: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error when retrieving author profile: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.patch(
    "/me",
    response_model=AuthorResponse,
    summary="Update author's own profile (author only)",
    responses={
        200: {"description": "Author profile updated successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized"},
        404: {"description": "Author profile not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"},
    },
)
async def update_own_author_profile(
    author_data: AuthorUpdate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Security(get_author_user),
):
    """Update author's own profile (author only)

    This endpoint allows authors to update their own profile information.
    Only users with the AUTHOR role can access this endpoint.
    """
    try:
        # Check if user has an author profile
        if not current_user.author_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You don't have an author profile")

        # Get author profile
        author = await service.get_author_by_id(db=db, author_id=current_user.author_id)
        if not author:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author profile not found")

        # Update author profile (partial update)
        updated_author = await service.patch_author(db=db, author_id=current_user.author_id, author_data=author_data)
        return updated_author

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error when updating author profile: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error when updating author profile: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.post(
    "/me/social-media",
    response_model=AuthorResponse,
    summary="Add or update social media link (author only)",
    responses={
        200: {"description": "Social media link added or updated successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized"},
        404: {"description": "Author profile not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"},
    },
)
async def add_own_social_media(
    social_data: SocialMediaUpdate = Body(...),
    db: AsyncSession = Depends(get_session),
    current_user: User = Security(get_author_user),
):
    """Add or update a social media link for author's own profile (author only)

    This endpoint allows authors to add or update social media links on their own profile.
    Only users with the AUTHOR role can access this endpoint.
    """
    try:
        # Check if user has an author profile
        if not current_user.author_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You don't have an author profile")

        # Add or update social media link
        updated_author = await service.update_social_media(
            db=db, author_id=current_user.author_id, social_data=social_data
        )
        if not updated_author:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author profile not found")

        return updated_author

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error when adding social media for author: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error when adding social media for author: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.delete(
    "/me/social-media/{platform}",
    response_model=AuthorResponse,
    summary="Delete social media link (author only)",
    responses={
        200: {"description": "Social media link deleted successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized"},
        404: {"description": "Author profile or social media platform not found"},
        500: {"description": "Internal server error"},
    },
)
async def delete_own_social_media(
    platform: str = Path(...),
    db: AsyncSession = Depends(get_session),
    current_user: User = Security(get_author_user),
):
    """Delete a social media link from author's own profile (author only)

    This endpoint allows authors to delete social media links from their own profile.
    Only users with the AUTHOR role can access this endpoint.
    """
    try:
        # Check if user has an author profile
        if not current_user.author_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You don't have an author profile")

        # Delete social media link
        updated_author = await service.delete_social_media(db=db, author_id=current_user.author_id, platform=platform)
        if not updated_author:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author profile not found")

        return updated_author

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error when deleting social media for author: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error when deleting social media for author: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.get(
    "/{author_id}",
    response_model=AuthorResponse,
    summary="Get author by ID",
    responses={
        200: {"description": "Author retrieved successfully"},
        404: {"description": "Author not found"},
        500: {"description": "Internal server error"},
    },
)
async def get_author_by_id(
    author_id: int = Path(..., ge=1),
    db: AsyncSession = Depends(get_session),
):
    """Get a specific author by its ID"""
    try:
        author = await service.get_author_by_id(db=db, author_id=author_id)
        if not author:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Author with ID {author_id} not found")
        return author
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error when fetching author ID {author_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error when fetching author ID {author_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.put(
    "/{author_id}",
    response_model=AuthorResponse,
    summary="Update an author (full update) (admin only)",
    responses={
        200: {"description": "Author updated successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized"},
        404: {"description": "Author not found"},
        409: {"description": "Author with this name already exists"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"},
    },
)
async def update_author(
    author_data: AuthorUpdate,
    author_id: int = Path(..., ge=1),
    db: AsyncSession = Depends(get_session),
    admin_user: User = Security(get_admin_user),
):
    """Update an existing author with a complete replacement (PUT) (admin only)

    This endpoint is restricted to admin users only.
    """
    try:
        # Check if author exists
        author = await service.get_author_by_id(db=db, author_id=author_id)
        if not author:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Author with ID {author_id} not found")

        # Check for name conflict if name is being updated
        if author_data.name and author_data.name != author.name:
            existing_author = await service.get_author_by_name(db, author_data.name)
            if existing_author:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Author with name '{author_data.name}' already exists",
                )

        # Update the author
        updated_author = await service.update_author(db=db, author_id=author_id, author_data=author_data)
        return updated_author
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error when updating author ID {author_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error when updating author ID {author_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.patch(
    "/{author_id}",
    response_model=AuthorResponse,
    summary="Partially update an author (admin only)",
    responses={
        200: {"description": "Author partially updated successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized"},
        404: {"description": "Author not found"},
        409: {"description": "Author with this name already exists"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"},
    },
)
async def patch_author(
    author_data: AuthorUpdate,
    author_id: int = Path(..., ge=1),
    db: AsyncSession = Depends(get_session),
    admin_user: User = Security(get_admin_user),
):
    """Partially update an existing author (PATCH) (admin only)

    This endpoint is restricted to admin users only.
    """
    try:
        # Check if author exists
        author = await service.get_author_by_id(db=db, author_id=author_id)
        if not author:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Author with ID {author_id} not found")

        # Check for name conflict if name is being updated
        if author_data.name is not None and author_data.name != author.name:
            existing_author = await service.get_author_by_name(db, author_data.name)
            if existing_author:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Author with name '{author_data.name}' already exists",
                )

        # Update the author
        updated_author = await service.patch_author(db=db, author_id=author_id, author_data=author_data)
        return updated_author
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error when patching author ID {author_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error when patching author ID {author_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.delete(
    "/{author_id}",
    summary="Delete an author (admin only)",
    responses={
        200: {"description": "Author deleted successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized"},
        404: {"description": "Author not found"},
        500: {"description": "Internal server error"},
    },
)
async def delete_author(
    author_id: int = Path(..., ge=1),
    db: AsyncSession = Depends(get_session),
    admin_user: User = Security(get_admin_user),
):
    """Delete an author (admin only)

    This endpoint is restricted to admin users only.
    """
    try:
        # Check if author exists
        author = await service.get_author_by_id(db=db, author_id=author_id)
        if not author:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Author with ID {author_id} not found")

        # Delete the author
        result = await service.delete_author(db=db, author_id=author_id)
        return result
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error when deleting author ID {author_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error when deleting author ID {author_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.post(
    "/{author_id}/social-media",
    response_model=AuthorResponse,
    summary="Add or update social media link (admin only)",
    responses={
        200: {"description": "Social media link added or updated successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized"},
        404: {"description": "Author not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"},
    },
)
async def add_social_media(
    author_id: int = Path(..., ge=1),
    social_data: SocialMediaUpdate = Body(...),
    db: AsyncSession = Depends(get_session),
    admin_user: User = Security(get_admin_user),
):
    """Add or update a social media link for an author (admin only)

    This endpoint is restricted to admin users only.
    """
    try:
        # Check if author exists
        author = await service.get_author_by_id(db=db, author_id=author_id)
        if not author:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Author with ID {author_id} not found")

        # Add or update social media link
        updated_author = await service.update_social_media(db=db, author_id=author_id, social_data=social_data)
        return updated_author
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error when adding social media for author ID {author_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error when adding social media for author ID {author_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.delete(
    "/{author_id}/social-media/{platform}",
    response_model=AuthorResponse,
    summary="Delete social media link (admin only)",
    responses={
        200: {"description": "Social media link deleted successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized"},
        404: {"description": "Author or social media platform not found"},
        500: {"description": "Internal server error"},
    },
)
async def delete_social_media(
    author_id: int = Path(..., ge=1),
    platform: str = Path(...),
    db: AsyncSession = Depends(get_session),
    admin_user: User = Security(get_admin_user),
):
    """Delete a social media link for an author (admin only)

    This endpoint is restricted to admin users only.
    """
    try:
        # Check if author exists
        author = await service.get_author_by_id(db=db, author_id=author_id)
        if not author:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Author with ID {author_id} not found")

        # Delete social media link
        updated_author = await service.delete_social_media(db=db, author_id=author_id, platform=platform)
        return updated_author
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error when deleting social media for author ID {author_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error when deleting social media for author ID {author_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.get(
    "/me",
    response_model=AuthorResponse,
    summary="Get author's own profile (author only)",
    responses={
        200: {"description": "Author profile retrieved successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized"},
        404: {"description": "Author profile not found"},
        500: {"description": "Internal server error"},
    },
)
async def get_own_author_profile(  # noqa:
    db: AsyncSession = Depends(get_session),
    current_user: User = Security(get_author_user),
):
    """Get author's own profile (author only)

    This endpoint allows authors to retrieve their own profile information.
    Only users with the AUTHOR role can access this endpoint.
    """
    try:
        # Check if user has an author profile
        if not current_user.author_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You don't have an author profile")

        # Get author profile
        author = await service.get_author_by_id(db=db, author_id=current_user.author_id)
        if not author:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author profile not found")

        return author

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error when retrieving author profile: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error when retrieving author profile: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.patch(
    "/me",
    response_model=AuthorResponse,
    summary="Update author's own profile (author only)",
    responses={
        200: {"description": "Author profile updated successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized"},
        404: {"description": "Author profile not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"},
    },
)
async def update_own_author_profile(  # noqa:
    author_data: AuthorUpdate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Security(get_author_user),
):
    """Update author's own profile (author only)

    This endpoint allows authors to update their own profile information.
    Only users with the AUTHOR role can access this endpoint.
    """
    try:
        # Check if user has an author profile
        if not current_user.author_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You don't have an author profile")

        # Get author profile
        author = await service.get_author_by_id(db=db, author_id=current_user.author_id)
        if not author:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author profile not found")

        # Update author profile (partial update)
        updated_author = await service.patch_author(db=db, author_id=current_user.author_id, author_data=author_data)
        return updated_author

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error when updating author profile: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error when updating author profile: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.post(
    "/me/social-media",
    response_model=AuthorResponse,
    summary="Add or update social media link (author only)",
    responses={
        200: {"description": "Social media link added or updated successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized"},
        404: {"description": "Author profile not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"},
    },
)
async def add_own_social_media(  # noqa:
    social_data: SocialMediaUpdate = Body(...),
    db: AsyncSession = Depends(get_session),
    current_user: User = Security(get_author_user),
):
    """Add or update a social media link for author's own profile (author only)

    This endpoint allows authors to add or update social media links on their own profile.
    Only users with the AUTHOR role can access this endpoint.
    """
    try:
        # Check if user has an author profile
        if not current_user.author_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You don't have an author profile")

        # Add or update social media link
        updated_author = await service.update_social_media(
            db=db, author_id=current_user.author_id, social_data=social_data
        )
        if not updated_author:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author profile not found")

        return updated_author

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error when adding social media for author: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error when adding social media for author: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.delete(
    "/me/social-media/{platform}",
    response_model=AuthorResponse,
    summary="Delete social media link (author only)",
    responses={
        200: {"description": "Social media link deleted successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized"},
        404: {"description": "Author profile or social media platform not found"},
        500: {"description": "Internal server error"},
    },
)
async def delete_own_social_media(  # noqa:
    platform: str = Path(...),
    db: AsyncSession = Depends(get_session),
    current_user: User = Security(get_author_user),
):
    """Delete a social media link from author's own profile (author only)

    This endpoint allows authors to delete social media links from their own profile.
    Only users with the AUTHOR role can access this endpoint.
    """
    try:
        # Check if user has an author profile
        if not current_user.author_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You don't have an author profile")

        # Delete social media link
        updated_author = await service.delete_social_media(db=db, author_id=current_user.author_id, platform=platform)
        if not updated_author:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author profile not found")

        return updated_author

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error when deleting social media for author: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error when deleting social media for author: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")
