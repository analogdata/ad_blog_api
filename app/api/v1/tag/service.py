from typing import List, Optional, Tuple, Any, Dict
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundException, ConflictException
from app.db.models.tag import Tag
from app.db.models.article_tag import ArticleTag
from app.api.v1.tag.schema import TagCreate, TagUpdate


async def get_tags(
    db: AsyncSession, skip: int = 0, limit: int = 100, search: Optional[str] = None
) -> Tuple[List[Tag], int]:
    """Get all tags with optional pagination and search

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        search: Optional search term for tag name or description

    Returns:
        Tuple of (list of tags, total count)
    """
    query = select(Tag)

    # Apply search filter if provided
    if search:
        query = query.where((Tag.name.ilike(f"%{search}%")) | (Tag.description.ilike(f"%{search}%")))

    # Get total count for pagination
    count_query = select(func.count()).select_from(query.subquery())
    result = await db.execute(count_query)
    total = result.scalar_one()

    # Apply pagination
    query = query.offset(skip).limit(limit)

    # Execute query
    result = await db.execute(query)
    tags = result.scalars().all()

    return tags, total


async def get_tag_by_id(db: AsyncSession, tag_id: int) -> Tag:
    """Get a tag by its ID

    Args:
        db: Database session
        tag_id: ID of the tag to retrieve

    Returns:
        Tag object

    Raises:
        HTTPException: If tag not found
    """
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    if not tag:
        raise NotFoundException(detail=f"Tag with ID {tag_id} not found", code="tag_not_found")
    return tag


async def get_tag_by_slug(db: AsyncSession, slug: str) -> Tag:
    """Get a tag by its slug

    Args:
        db: Database session
        slug: Slug of the tag to retrieve

    Returns:
        Tag object

    Raises:
        HTTPException: If tag not found
    """
    result = await db.execute(select(Tag).where(Tag.slug == slug))
    tag = result.scalar_one_or_none()
    if not tag:
        raise NotFoundException(detail=f"Tag with slug '{slug}' not found", code="tag_not_found")
    return tag


async def get_tag_by_name(db: AsyncSession, name: str) -> Tag:
    """Get a tag by its name

    Args:
        db: Database session
        name: Name of the tag to retrieve

    Returns:
        Tag object or None if not found
    """
    result = await db.execute(select(Tag).where(func.lower(Tag.name) == func.lower(name)))
    return result.scalar_one_or_none()


async def create_tag(db: AsyncSession, tag_data: TagCreate) -> Tag:
    """Create a new tag

    Args:
        db: Database session
        tag_data: Tag data for creation

    Returns:
        Created tag object

    Raises:
        HTTPException: If tag with same name already exists
    """
    # Check if tag with same name already exists
    result = await db.execute(select(Tag).where(func.lower(Tag.name) == func.lower(tag_data.name)))
    existing_tag = result.scalar_one_or_none()

    if existing_tag:
        raise ConflictException(detail=f"Tag with name '{tag_data.name}' already exists", code="tag_name_conflict")

    # Create new tag with proper slug generation
    tag_dict = tag_data.model_dump()
    
    # Create the tag instance and let the SlugGeneratorMixin handle slug creation
    tag = Tag(**tag_dict)
    
    # Ensure slug is generated if not present
    if not tag.slug:
        tag.slug = Tag.generate_slug(tag.name)
        
    db.add(tag)
    await db.commit()
    await db.refresh(tag)

    return tag


async def update_tag(db: AsyncSession, tag_id: int, tag_data: TagUpdate) -> Tag:
    """Update an existing tag (PUT method - full update)

    Args:
        db: Database session
        tag_id: ID of the tag to update
        tag_data: Tag data for update

    Returns:
        Updated tag object

    Raises:
        HTTPException: If tag not found or name conflict
    """
    # Get existing tag
    tag = await get_tag_by_id(db, tag_id)

    # Check for name conflict if name is being updated
    if tag_data.name and tag_data.name != tag.name:
        result = await db.execute(select(Tag).where(func.lower(Tag.name) == func.lower(tag_data.name)))
        existing_tag = result.scalar_one_or_none()

        if existing_tag:
            raise ConflictException(detail=f"Tag with name '{tag_data.name}' already exists", code="tag_name_conflict")

    # Update tag fields
    update_data = tag_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(tag, key, value)

    db.add(tag)
    await db.commit()
    await db.refresh(tag)

    return tag


async def patch_tag(db: AsyncSession, tag_id: int, tag_data: TagUpdate) -> Tag:
    """Partially update an existing tag (PATCH method)

    Args:
        db: Database session
        tag_id: ID of the tag to update
        tag_data: Partial tag data for update

    Returns:
        Updated tag object

    Raises:
        HTTPException: If tag not found or name conflict
    """
    # Get existing tag
    tag = await get_tag_by_id(db, tag_id)

    # Check for name conflict if name is being updated
    if tag_data.name is not None and tag_data.name != tag.name:
        result = await db.execute(select(Tag).where(func.lower(Tag.name) == func.lower(tag_data.name)))
        existing_tag = result.scalar_one_or_none()

        if existing_tag:
            raise ConflictException(detail=f"Tag with name '{tag_data.name}' already exists", code="tag_name_conflict")

    # Update only provided fields
    update_data = tag_data.model_dump(exclude_unset=True, exclude_none=True)
    for key, value in update_data.items():
        setattr(tag, key, value)

    db.add(tag)
    await db.commit()
    await db.refresh(tag)

    return tag


async def delete_tag(db: AsyncSession, tag_id: int) -> Dict[str, Any]:
    """Delete a tag

    Args:
        db: Database session
        tag_id: ID of the tag to delete

    Returns:
        Dictionary with deletion status

    Raises:
        HTTPException: If tag not found
    """
    tag = await get_tag_by_id(db, tag_id)

    # Delete tag
    await db.delete(tag)
    await db.commit()

    return {"success": True, "message": f"Tag '{tag.name}' successfully deleted"}


async def get_tags_with_article_count(db: AsyncSession, limit: int = 10) -> List[Dict[str, Any]]:
    """Get tags with article count for popular tags widget

    Args:
        db: Database session
        limit: Maximum number of tags to return

    Returns:
        List of tags with article count
    """
    query = (
        select(Tag, func.count(ArticleTag.article_id).label("article_count"))
        .join(ArticleTag, Tag.id == ArticleTag.tag_id, isouter=True)
        .group_by(Tag.id)
        .order_by(func.count(ArticleTag.article_id).desc())
        .limit(limit)
    )

    result = await db.execute(query)
    results = result.all()

    # Convert results to dictionaries with tag and count
    tags_with_count = [{**tag.__dict__, "article_count": count} for tag, count in results]

    return tags_with_count
