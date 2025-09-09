import logging
import random
import string
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status

from app.db.models.user import User
from app.api.v1.user.schema import UserProfileUpdate

logger = logging.getLogger(__name__)


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
    """
    Get a list of users with pagination

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of User objects
    """
    try:
        result = await db.execute(select(User).offset(skip).limit(limit))
        return result.scalars().all()
    except SQLAlchemyError as e:
        logger.error(f"Database error when fetching users: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """
    Get a user by email

    Args:
        db: Database session
        email: User email

    Returns:
        User object or None if not found
    """
    try:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalars().first()
    except SQLAlchemyError as e:
        logger.error(f"Database error when fetching user by email {email}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")


async def update_user_profile(db: AsyncSession, user_id: int, profile_data: UserProfileUpdate) -> User:
    """
    Update user profile information

    Args:
        db: Database session
        user_id: User ID
        profile_data: User profile update data

    Returns:
        Updated User object

    Raises:
        HTTPException: If user not found, email already exists, or passwords don't match
    """
    try:
        # Get user
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {user_id} not found")

        # Check if email is being updated and if it's already in use
        if profile_data.email and profile_data.email != user.email:
            email_check = await db.execute(select(User).where(User.email == profile_data.email))
            existing_user = email_check.scalars().first()

            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"User with email '{profile_data.email}' already exists",
                )

            # Update email and reset verification status
            user.email = profile_data.email
            user.is_verified = False
            user.generate_verification_token()

        # Check if password is being updated
        if profile_data.password:
            if not profile_data.confirm_password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Confirm password is required when changing password",
                )

            if profile_data.password != profile_data.confirm_password:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")

            # Update password
            user.password = User.hash_password(profile_data.password)

        # Update other fields if provided
        if profile_data.first_name is not None:
            user.first_name = profile_data.first_name
        if profile_data.last_name is not None:
            user.last_name = profile_data.last_name
        if profile_data.profile_image is not None:
            user.profile_image = profile_data.profile_image

        await db.commit()
        await db.refresh(user)

        return user

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error when updating user profile: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
    except Exception as e:
        await db.rollback()
        logger.error(f"Unexpected error when updating user profile: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


async def delete_user(db: AsyncSession, user_id: int) -> bool:
    """
    Delete a user

    Args:
        db: Database session
        user_id: User ID

    Returns:
        True if user was deleted, False if user not found
    """
    try:
        # Check if user exists
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()

        if not user:
            return False

        # Delete user
        await db.delete(user)
        await db.commit()

        return True

    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error when deleting user ID {user_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")


def generate_random_password(length: int = 12) -> str:
    """
    Generate a random secure password

    Args:
        length: Length of the password

    Returns:
        Random password string
    """
    # Include at least one of each: uppercase, lowercase, digit, special char
    uppercase = random.choice(string.ascii_uppercase)
    lowercase = random.choice(string.ascii_lowercase)
    digit = random.choice(string.digits)
    special = random.choice("!@#$%^&*()-_=+")

    # Fill the rest with random chars
    remaining = "".join(
        random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits + "!@#$%^&*()-_=+", k=length - 4)
    )

    # Combine all parts and shuffle
    all_chars = uppercase + lowercase + digit + special + remaining
    password_list = list(all_chars)
    random.shuffle(password_list)

    return "".join(password_list)


async def admin_reset_password(db: AsyncSession, user_id: int, custom_password: Optional[str] = None) -> Optional[str]:
    """
    Reset a user's password (admin function)

    Args:
        db: Database session
        user_id: User ID
        custom_password: Optional custom password to set. If None, a random password will be generated.

    Returns:
        New password if successful, None if user not found
    """
    try:
        # Check if user exists
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()

        if not user:
            return None

        # Use custom password if provided, otherwise generate a random one
        new_password = custom_password if custom_password else generate_random_password()

        # Update user password
        user.password = User.hash_password(new_password)

        await db.commit()

        return new_password

    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error when resetting password for user ID {user_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
