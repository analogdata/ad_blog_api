import logging
from typing import List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status

from app.db.models.author import Author
from app.db.models.user import User
from app.api.v1.author.schema import AuthorCreate, AuthorUpdate, AuthorArticleCount, SocialMediaUpdate

logger = logging.getLogger(__name__)


async def get_authors(
    db: AsyncSession, skip: int = 0, limit: int = 100, search: Optional[str] = None
) -> Tuple[List[Author], int]:
    """
    Get a list of authors with pagination and optional search

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        search: Optional search term for author name or bio

    Returns:
        Tuple of (List of Author objects, Total count)
    """
    try:
        # Build query
        query = select(Author)

        # Apply search filter if provided
        if search:
            search_term = f"%{search}%"
            query = query.where((Author.name.ilike(search_term)) | (Author.bio.ilike(search_term)))

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query)

        # Apply pagination
        query = query.offset(skip).limit(limit).order_by(Author.name)

        # Execute query
        result = await db.execute(query)
        authors = result.scalars().all()

        return list(authors), total

    except SQLAlchemyError as e:
        logger.error(f"Database error when fetching authors: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")


async def get_author_by_id(db: AsyncSession, author_id: int) -> Optional[Author]:
    """
    Get an author by ID

    Args:
        db: Database session
        author_id: Author ID

    Returns:
        Author object or None if not found
    """
    try:
        result = await db.execute(select(Author).where(Author.id == author_id))
        return result.scalars().first()

    except SQLAlchemyError as e:
        logger.error(f"Database error when fetching author ID {author_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")


async def get_author_by_slug(db: AsyncSession, slug: str) -> Optional[Author]:
    """
    Get an author by slug

    Args:
        db: Database session
        slug: Author slug

    Returns:
        Author object or None if not found
    """
    try:
        result = await db.execute(select(Author).where(Author.slug == slug))
        return result.scalars().first()

    except SQLAlchemyError as e:
        logger.error(f"Database error when fetching author by slug '{slug}': {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")


async def get_author_by_name(db: AsyncSession, name: str) -> Optional[Author]:
    """
    Get an author by name

    Args:
        db: Database session
        name: Author name

    Returns:
        Author object or None if not found
    """
    try:
        result = await db.execute(select(Author).where(func.lower(Author.name) == func.lower(name)))
        return result.scalars().first()

    except SQLAlchemyError as e:
        logger.error(f"Database error when fetching author by name '{name}': {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")


async def create_author(db: AsyncSession, author_data: AuthorCreate) -> Author:
    """
    Create a new author

    Args:
        db: Database session
        author_data: Author data

    Returns:
        Created Author object
    """
    try:
        # Create author with data from request
        data_dict = author_data.model_dump()

        # Create the author instance
        author = Author(**data_dict)

        # Explicitly generate slug if not present
        if not getattr(author, "slug", None) and author.name:
            author.slug = Author.generate_slug(author.name)

        db.add(author)
        await db.commit()
        await db.refresh(author)

        return author

    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error when creating author: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")


async def update_author(db: AsyncSession, author_id: int, author_data: AuthorUpdate) -> Author:
    """
    Update an author (full update)

    Args:
        db: Database session
        author_id: Author ID
        author_data: Author data

    Returns:
        Updated Author object
    """
    try:
        # Get author
        author = await get_author_by_id(db, author_id)
        if not author:
            return None

        # Update fields
        author_dict = author_data.model_dump(exclude_unset=False, exclude_none=True)
        for key, value in author_dict.items():
            setattr(author, key, value)

        # Update slug if name was changed
        if "name" in author_dict and author.name:
            author.slug = Author.generate_slug(author.name)

        await db.commit()
        await db.refresh(author)

        return author

    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error when updating author ID {author_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")


async def patch_author(db: AsyncSession, author_id: int, author_data: AuthorUpdate) -> Author:
    """
    Partially update an author

    Args:
        db: Database session
        author_id: Author ID
        author_data: Author data

    Returns:
        Updated Author object
    """
    try:
        # Get author
        author = await get_author_by_id(db, author_id)
        if not author:
            return None

        # Update only provided fields
        author_dict = author_data.model_dump(exclude_unset=True, exclude_none=True)
        for key, value in author_dict.items():
            setattr(author, key, value)

        # Update slug if name was changed
        if "name" in author_dict and author.name:
            author.slug = Author.generate_slug(author.name)

        await db.commit()
        await db.refresh(author)

        return author

    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error when patching author ID {author_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")


async def delete_author(db: AsyncSession, author_id: int) -> dict:
    """
    Delete an author

    Args:
        db: Database session
        author_id: Author ID

    Returns:
        Success message
    """
    try:
        # Get author
        author = await get_author_by_id(db, author_id)
        if not author:
            return None

        # Delete author
        await db.delete(author)
        await db.commit()

        return {"message": f"Author with ID {author_id} deleted successfully"}

    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error when deleting author ID {author_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")


async def update_social_media(db: AsyncSession, author_id: int, social_data: SocialMediaUpdate) -> Author:
    """
    Add or update a social media link for an author

    Args:
        db: Database session
        author_id: Author ID
        social_data: Social media data

    Returns:
        Updated Author object
    """
    try:
        # Get author
        author = await get_author_by_id(db, author_id)
        if not author:
            return None

        # Log before state
        logger.info(f"Before update - Author social media: {author.social_media}")
        logger.info(f"Adding platform: {social_data.platform}, URL: {social_data.url}")

        # Add or update social media link
        author.add_social_media(social_data.platform, social_data.url)

        # Log after state
        logger.info(f"After update - Author social media: {author.social_media}")

        # Explicitly set the social_media field to ensure it's marked as modified
        setattr(author, "social_media", author.social_media)

        # Add to session and commit
        db.add(author)
        await db.commit()
        await db.refresh(author)

        # Log final state after refresh
        logger.info(f"After refresh - Author social media: {author.social_media}")

        return author

    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error when updating social media for author ID {author_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")


async def delete_social_media(db: AsyncSession, author_id: int, platform: str) -> Author:
    """
    Delete a social media link for an author

    Args:
        db: Database session
        author_id: Author ID
        platform: Social media platform to delete

    Returns:
        Updated Author object
    """
    try:
        # Get author
        author = await get_author_by_id(db, author_id)
        if not author:
            return None

        # Remove social media link
        success = author.remove_social_media(platform)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Social media platform '{platform}' not found for author"
            )

        await db.commit()
        await db.refresh(author)

        return author

    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error when deleting social media for author ID {author_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")


async def can_manage_author(user: "User", author_id: int) -> bool:
    """
    Check if user can manage this author

    Args:
        user: User object
        author_id: Author ID to check permissions for

    Returns:
        True if user can manage this author, False otherwise
    """
    # Admin can manage any author
    if user.role == "admin":
        return True

    # Author can only manage their own profile
    return user.author_id == author_id


async def generate_unique_author_name(db: AsyncSession, base_name: str) -> str:
    """
    Generate a unique author name based on the user's name

    Args:
        db: Database session
        base_name: Base name to use (typically user's full name)

    Returns:
        Unique author name
    """
    name = base_name
    counter = 1

    # Check if name exists
    while await get_author_by_name(db, name):
        # Append counter to make unique
        name = f"{base_name} {counter}"
        counter += 1

    return name


async def get_authors_with_article_count(db: AsyncSession, limit: int = 10) -> List[AuthorArticleCount]:
    """
    Get popular authors with article count

    Args:
        db: Database session
        limit: Maximum number of authors to return

    Returns:
        List of authors with article count
    """
    try:
        # Use a more efficient approach with a join and count
        from sqlalchemy import func
        from app.db.models.article import Article

        # Query that counts articles per author
        query = (
            select(
                Author.id,
                Author.name,
                Author.slug,
                Author.profile_image,
                func.count(Article.id).label("article_count"),
            )
            .outerjoin(Article, Author.id == Article.author_id)
            .group_by(Author.id, Author.name, Author.slug, Author.profile_image)
            .order_by(func.count(Article.id).desc())
            .limit(limit)
        )

        result = await db.execute(query)
        rows = result.all()

        # Convert to response model
        author_counts = []
        for row in rows:
            author_counts.append(
                AuthorArticleCount(
                    id=row.id,
                    name=row.name,
                    slug=row.slug,
                    article_count=row.article_count,
                    profile_image=row.profile_image,
                )
            )

        return author_counts

    except SQLAlchemyError as e:
        logger.error(f"Database error when fetching authors with article count: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
