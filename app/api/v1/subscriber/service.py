import logging
from typing import List, Tuple, Optional
from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.subscriber import Subscriber
from app.api.v1.subscriber.schema import SubscriberCreate, SubscriberUpdate

logger = logging.getLogger(__name__)


async def get_subscribers(
    db: AsyncSession, skip: int = 0, limit: int = 100, search: Optional[str] = None
) -> Tuple[List[Subscriber], int]:
    """
    Get all subscribers with optional pagination and search

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        search: Optional search term for email

    Returns:
        Tuple of (list of subscribers, total count)
    """
    query = select(Subscriber)
    count_query = select(func.count()).select_from(Subscriber)

    # Apply search filter if provided
    if search:
        search_term = f"%{search}%"
        query = query.where(Subscriber.email.ilike(search_term))
        count_query = count_query.where(Subscriber.email.ilike(search_term))

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination
    query = query.offset(skip).limit(limit)

    # Execute query
    result = await db.execute(query)
    subscribers = result.scalars().all()

    return subscribers, total


async def get_subscriber_by_id(db: AsyncSession, subscriber_id: int) -> Optional[Subscriber]:
    """
    Get a subscriber by ID

    Args:
        db: Database session
        subscriber_id: ID of the subscriber to retrieve

    Returns:
        Subscriber object if found, None otherwise
    """
    query = select(Subscriber).where(Subscriber.id == subscriber_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_subscriber_by_email(db: AsyncSession, email: str) -> Optional[Subscriber]:
    """
    Get a subscriber by email

    Args:
        db: Database session
        email: Email of the subscriber to retrieve

    Returns:
        Subscriber object if found, None otherwise
    """
    query = select(Subscriber).where(Subscriber.email == email)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_subscriber_by_token(db: AsyncSession, token: str) -> Optional[Subscriber]:
    """
    Get a subscriber by verification token

    Args:
        db: Database session
        token: Verification token

    Returns:
        Subscriber object if found, None otherwise
    """
    query = select(Subscriber).where(Subscriber.verification_token == token)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_subscriber(db: AsyncSession, subscriber_data: SubscriberCreate) -> Subscriber:
    """
    Create a new subscriber

    Args:
        db: Database session
        subscriber_data: Data for creating the subscriber

    Returns:
        Created subscriber object

    Raises:
        HTTPException: If subscriber with this email already exists
    """
    # Check if subscriber with this email already exists
    existing_subscriber = await get_subscriber_by_email(db, subscriber_data.email)

    if existing_subscriber:
        # If subscriber exists but is inactive, reactivate them
        if not existing_subscriber.is_active:
            existing_subscriber.resubscribe()
            await db.commit()
            await db.refresh(existing_subscriber)
            return existing_subscriber
        # If subscriber is already active, raise an error
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Subscriber with email '{subscriber_data.email}' already exists",
        )

    # Create new subscriber
    subscriber = Subscriber(
        email=subscriber_data.email,
        is_active=True,
        is_verified=False,
    )
    
    # Explicitly generate verification token
    subscriber.verification_token = Subscriber.generate_verification_token()

    db.add(subscriber)
    await db.commit()
    await db.refresh(subscriber)

    return subscriber


async def verify_subscriber(db: AsyncSession, token: str) -> Subscriber:
    """
    Verify a subscriber using their verification token

    Args:
        db: Database session
        token: Verification token

    Returns:
        Verified subscriber object

    Raises:
        HTTPException: If token is invalid or subscriber not found
    """
    subscriber = await get_subscriber_by_token(db, token)

    if not subscriber:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid verification token")

    subscriber.verify()
    await db.commit()
    await db.refresh(subscriber)

    return subscriber


async def update_subscriber(db: AsyncSession, subscriber_id: int, subscriber_data: SubscriberUpdate) -> Subscriber:
    """
    Update a subscriber

    Args:
        db: Database session
        subscriber_id: ID of the subscriber to update
        subscriber_data: Data for updating the subscriber

    Returns:
        Updated subscriber object

    Raises:
        HTTPException: If subscriber not found
    """
    subscriber = await get_subscriber_by_id(db, subscriber_id)

    if not subscriber:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Subscriber with ID {subscriber_id} not found"
        )

    # Update fields if provided
    if subscriber_data.is_active is not None:
        if subscriber_data.is_active and not subscriber.is_active:
            subscriber.resubscribe()
        elif not subscriber_data.is_active and subscriber.is_active:
            subscriber.unsubscribe()

    await db.commit()
    await db.refresh(subscriber)

    return subscriber


async def delete_subscriber(db: AsyncSession, subscriber_id: int) -> dict:
    """
    Delete a subscriber

    Args:
        db: Database session
        subscriber_id: ID of the subscriber to delete

    Returns:
        Dictionary with success message

    Raises:
        HTTPException: If subscriber not found
    """
    subscriber = await get_subscriber_by_id(db, subscriber_id)

    if not subscriber:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Subscriber with ID {subscriber_id} not found"
        )

    await db.delete(subscriber)
    await db.commit()

    return {"message": f"Subscriber with ID {subscriber_id} deleted successfully"}


async def unsubscribe_by_email(db: AsyncSession, email: str) -> Subscriber:
    """
    Unsubscribe a subscriber by email

    Args:
        db: Database session
        email: Email of the subscriber to unsubscribe

    Returns:
        Unsubscribed subscriber object

    Raises:
        HTTPException: If subscriber not found
    """
    subscriber = await get_subscriber_by_email(db, email)

    if not subscriber:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Subscriber with email '{email}' not found")

    subscriber.unsubscribe()
    await db.commit()
    await db.refresh(subscriber)

    return subscriber
