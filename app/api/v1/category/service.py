import logging
from typing import List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status

from app.db.models.category import Category
from app.api.v1.category.schema import CategoryCreate, CategoryUpdate, CategoryArticleCount

logger = logging.getLogger(__name__)


async def get_categories(
    db: AsyncSession, skip: int = 0, limit: int = 100, search: Optional[str] = None
) -> Tuple[List[Category], int]:
    """
    Get a list of categories with pagination and optional search

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        search: Optional search term for category name or description

    Returns:
        Tuple of (List of Category objects, Total count)
    """
    try:
        # Build query
        query = select(Category)

        # Apply search filter if provided
        if search:
            search_term = f"%{search}%"
            query = query.where((Category.name.ilike(search_term)) | (Category.description.ilike(search_term)))

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query)

        # Apply pagination
        query = query.offset(skip).limit(limit).order_by(Category.name)

        # Execute query
        result = await db.execute(query)
        categories = result.scalars().all()

        return list(categories), total

    except SQLAlchemyError as e:
        logger.error(f"Database error when fetching categories: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")


async def get_category_by_id(db: AsyncSession, category_id: int) -> Optional[Category]:
    """
    Get a category by ID

    Args:
        db: Database session
        category_id: Category ID

    Returns:
        Category object or None if not found
    """
    try:
        result = await db.execute(select(Category).where(Category.id == category_id))
        return result.scalars().first()

    except SQLAlchemyError as e:
        logger.error(f"Database error when fetching category ID {category_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")


async def get_category_by_slug(db: AsyncSession, slug: str) -> Optional[Category]:
    """
    Get a category by slug

    Args:
        db: Database session
        slug: Category slug

    Returns:
        Category object or None if not found
    """
    try:
        result = await db.execute(select(Category).where(Category.slug == slug))
        return result.scalars().first()

    except SQLAlchemyError as e:
        logger.error(f"Database error when fetching category by slug '{slug}': {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")


async def get_category_by_name(db: AsyncSession, name: str) -> Optional[Category]:
    """
    Get a category by name

    Args:
        db: Database session
        name: Category name

    Returns:
        Category object or None if not found
    """
    try:
        result = await db.execute(select(Category).where(func.lower(Category.name) == func.lower(name)))
        return result.scalars().first()

    except SQLAlchemyError as e:
        logger.error(f"Database error when fetching category by name '{name}': {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")


async def create_category(db: AsyncSession, category_data: CategoryCreate) -> Category:
    """
    Create a new category

    Args:
        db: Database session
        category_data: Category data

    Returns:
        Created Category object
    """
    try:
        # Create category with data from request
        data_dict = category_data.model_dump()

        # Create the category instance
        category = Category(**data_dict)

        # Explicitly generate slug if not present
        if not getattr(category, "slug", None) and category.name:
            category.slug = Category.generate_slug(category.name)

        db.add(category)
        await db.commit()
        await db.refresh(category)

        return category

    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error when creating category: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")


async def update_category(db: AsyncSession, category_id: int, category_data: CategoryUpdate) -> Category:
    """
    Update a category (full update)

    Args:
        db: Database session
        category_id: Category ID
        category_data: Category data

    Returns:
        Updated Category object
    """
    try:
        # Get category
        category = await get_category_by_id(db, category_id)
        if not category:
            return None

        # Update fields
        category_dict = category_data.model_dump(exclude_unset=False, exclude_none=True)
        for key, value in category_dict.items():
            setattr(category, key, value)

        # Update slug if name was changed
        if "name" in category_dict and category.name:
            category.slug = Category.generate_slug(category.name)

        await db.commit()
        await db.refresh(category)

        return category

    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error when updating category ID {category_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")


async def patch_category(db: AsyncSession, category_id: int, category_data: CategoryUpdate) -> Category:
    """
    Partially update a category

    Args:
        db: Database session
        category_id: Category ID
        category_data: Category data

    Returns:
        Updated Category object
    """
    try:
        # Get category
        category = await get_category_by_id(db, category_id)
        if not category:
            return None

        # Update only provided fields
        category_dict = category_data.model_dump(exclude_unset=True, exclude_none=True)
        for key, value in category_dict.items():
            setattr(category, key, value)

        # Update slug if name was changed
        if "name" in category_dict and category.name:
            category.slug = Category.generate_slug(category.name)

        await db.commit()
        await db.refresh(category)

        return category

    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error when patching category ID {category_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")


async def delete_category(db: AsyncSession, category_id: int) -> dict:
    """
    Delete a category

    Args:
        db: Database session
        category_id: Category ID

    Returns:
        Success message
    """
    try:
        # Get category
        category = await get_category_by_id(db, category_id)
        if not category:
            return None

        # Delete category
        await db.delete(category)
        await db.commit()

        return {"message": f"Category with ID {category_id} deleted successfully"}

    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error when deleting category ID {category_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")


async def get_categories_with_article_count(db: AsyncSession, limit: int = 10) -> List[CategoryArticleCount]:
    """
    Get popular categories with article count

    Args:
        db: Database session
        limit: Maximum number of categories to return

    Returns:
        List of categories with article count
    """
    try:
        # Use a more efficient approach with a join and count
        from sqlalchemy import func
        from app.db.models.article import Article

        # Query that counts articles per category
        query = (
            select(
                Category.id,
                Category.name,
                Category.slug,
                Category.category_icon,
                func.count(Article.id).label("article_count"),
            )
            .outerjoin(Article, Category.id == Article.category_id)
            .group_by(Category.id, Category.name, Category.slug, Category.category_icon)
            .order_by(func.count(Article.id).desc())
            .limit(limit)
        )

        result = await db.execute(query)
        rows = result.all()

        # Convert to response model
        category_counts = []
        for row in rows:
            category_counts.append(
                CategoryArticleCount(
                    id=row.id,
                    name=row.name,
                    slug=row.slug,
                    article_count=row.article_count,
                    category_icon=row.category_icon,
                )
            )

        return category_counts

    except SQLAlchemyError as e:
        logger.error(f"Database error when fetching categories with article count: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
