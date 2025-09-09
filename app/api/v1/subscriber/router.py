import logging
from fastapi import APIRouter, Depends, Query, Path, status, HTTPException, Security
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional

from app.db.db_init import get_session
from app.api.v1.subscriber import service
from app.api.v1.subscriber.schema import (
    SubscriberCreate,
    SubscriberUpdate,
    SubscriberResponse,
    SubscriberListResponse,
    SubscriberVerify,
)
from app.api.v1.auth.dependencies import get_admin_user
from app.db.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/",
    response_model=SubscriberListResponse,
    summary="Get all subscribers",
    responses={
        200: {"description": "List of subscribers retrieved successfully"},
        500: {"description": "Internal server error"},
    },
)
async def get_subscribers(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search term for subscriber email"),
    db: AsyncSession = Depends(get_session),
    admin_user: User = Security(get_admin_user),
):
    """Get all subscribers with optional pagination and search (admin only)"""
    try:
        subscribers, total = await service.get_subscribers(db=db, skip=skip, limit=limit, search=search)
        return SubscriberListResponse(items=subscribers, total=total)
    except SQLAlchemyError as e:
        logger.error(f"Database error when fetching subscribers: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error when fetching subscribers: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.post(
    "/",
    response_model=SubscriberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Subscribe with email",
    responses={
        201: {"description": "Subscription created successfully"},
        409: {"description": "Email already subscribed"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"},
    },
)
async def create_subscriber(
    subscriber_data: SubscriberCreate,
    db: AsyncSession = Depends(get_session),
):
    """Subscribe with email address

    This endpoint allows users to subscribe to the newsletter with their email.
    A verification email will be sent to confirm the subscription.
    """
    try:
        subscriber = await service.create_subscriber(db=db, subscriber_data=subscriber_data)
        return subscriber
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error when creating subscriber: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error when creating subscriber: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.post(
    "/verify",
    response_model=SubscriberResponse,
    summary="Verify subscription",
    responses={
        200: {"description": "Subscription verified successfully"},
        404: {"description": "Invalid verification token"},
        500: {"description": "Internal server error"},
    },
)
async def verify_subscriber(
    verification_data: SubscriberVerify,
    db: AsyncSession = Depends(get_session),
):
    """Verify a subscription using the verification token

    This endpoint verifies a subscriber's email using the token sent to their email.
    """
    try:
        subscriber = await service.verify_subscriber(db=db, token=verification_data.token)
        return subscriber
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error when verifying subscriber: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error when verifying subscriber: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.get(
    "/{subscriber_id}",
    response_model=SubscriberResponse,
    summary="Get subscriber by ID (admin only)",
    responses={
        200: {"description": "Subscriber retrieved successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized"},
        404: {"description": "Subscriber not found"},
        500: {"description": "Internal server error"},
    },
)
async def get_subscriber_by_id(
    subscriber_id: int = Path(..., ge=1),
    db: AsyncSession = Depends(get_session),
    admin_user: User = Security(get_admin_user),
):
    """Get a specific subscriber by ID (admin only)"""
    try:
        subscriber = await service.get_subscriber_by_id(db=db, subscriber_id=subscriber_id)
        if not subscriber:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Subscriber with ID {subscriber_id} not found"
            )
        return subscriber
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error when fetching subscriber ID {subscriber_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error when fetching subscriber ID {subscriber_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.patch(
    "/{subscriber_id}",
    response_model=SubscriberResponse,
    summary="Update subscriber (admin only)",
    responses={
        200: {"description": "Subscriber updated successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized"},
        404: {"description": "Subscriber not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"},
    },
)
async def update_subscriber(
    subscriber_data: SubscriberUpdate,
    subscriber_id: int = Path(..., ge=1),
    db: AsyncSession = Depends(get_session),
    admin_user: User = Security(get_admin_user),
):
    """Update a subscriber (admin only)"""
    try:
        subscriber = await service.update_subscriber(
            db=db, subscriber_id=subscriber_id, subscriber_data=subscriber_data
        )
        return subscriber
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error when updating subscriber ID {subscriber_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error when updating subscriber ID {subscriber_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.delete(
    "/{subscriber_id}",
    summary="Delete subscriber (admin only)",
    responses={
        200: {"description": "Subscriber deleted successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized"},
        404: {"description": "Subscriber not found"},
        500: {"description": "Internal server error"},
    },
)
async def delete_subscriber(
    subscriber_id: int = Path(..., ge=1),
    db: AsyncSession = Depends(get_session),
    admin_user: User = Security(get_admin_user),
):
    """Delete a subscriber (admin only)"""
    try:
        result = await service.delete_subscriber(db=db, subscriber_id=subscriber_id)
        return result
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error when deleting subscriber ID {subscriber_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error when deleting subscriber ID {subscriber_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.post(
    "/unsubscribe",
    response_model=SubscriberResponse,
    summary="Unsubscribe by email",
    responses={
        200: {"description": "Unsubscribed successfully"},
        404: {"description": "Email not found in subscribers"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"},
    },
)
async def unsubscribe(
    subscriber_data: SubscriberCreate,
    db: AsyncSession = Depends(get_session),
):
    """Unsubscribe using email address

    This endpoint allows users to unsubscribe from the newsletter using their email.
    """
    try:
        subscriber = await service.unsubscribe_by_email(db=db, email=subscriber_data.email)
        return subscriber
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error when unsubscribing email {subscriber_data.email}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error when unsubscribing email {subscriber_data.email}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")
