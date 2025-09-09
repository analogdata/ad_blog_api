import logging
from typing import Optional, Dict, Any, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status

from app.db.models.user import User, UserRole
from app.db.models.author import Author
from app.api.v1.auth.schema import UserCreate, UserLogin, UserUpdate
from app.api.v1.auth.security import create_tokens
from app.api.v1.author import service as author_service

logger = logging.getLogger(__name__)


async def register_user(db: AsyncSession, user_data: UserCreate) -> User:
    """
    Register a new user

    Args:
        db: Database session
        user_data: User registration data

    Returns:
        Created user object

    Raises:
        HTTPException: If email already exists or passwords don't match
    """
    # Check if passwords match
    if user_data.password != user_data.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")

    # Check if user with this email already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=f"User with email '{user_data.email}' already exists"
        )

    try:
        # Create new user
        user = User(
            email=user_data.email,
            password=user_data.password,  # Password will be hashed in User.__init__
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            role=user_data.role,
        )

        # Generate verification token
        user.generate_verification_token()

        db.add(user)
        await db.flush()  # Flush to get the user ID without committing

        # If user has AUTHOR role, create an author profile
        if user.role == UserRole.AUTHOR:
            try:
                # Generate author name from user's name
                author_name = user.get_full_name()

                # Ensure name is unique
                unique_name = await author_service.generate_unique_author_name(db, author_name)

                # Create author with basic info
                author = Author(name=unique_name)

                # Explicitly set the slug (the mixin doesn't seem to be working during creation)
                author.slug = Author.generate_slug(unique_name)

                # Add to session and flush to get ID
                db.add(author)
                await db.flush()

                # Link author to user
                user.author_id = author.id

                logger.info(f"Created author profile '{unique_name}' for user {user.email}")
            except Exception as e:
                logger.error(f"Error creating author profile for user {user.email}: {str(e)}")
                # Continue with user creation even if author creation fails
                # We can create the author profile later

        # Commit all changes
        await db.commit()
        await db.refresh(user)

        return user

    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error when registering user: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
    except Exception as e:
        await db.rollback()
        logger.error(f"Unexpected error when registering user: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


async def login_user(db: AsyncSession, login_data: UserLogin) -> Dict[str, Any]:
    """
    Authenticate a user and generate tokens

    Args:
        db: Database session
        login_data: User login credentials

    Returns:
        Dictionary with access_token, refresh_token, token_type and expires_in

    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Find user by email
        result = await db.execute(select(User).where(User.email == login_data.email))
        user = result.scalars().first()

        # Check if user exists and password is correct
        if not user or not user.verify_password(login_data.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

        # Check if user is active
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User account is disabled")

        # Check if user is verified
        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email not verified. Please verify your email before logging in.",
            )

        # Update last login timestamp
        user.update_last_login()
        await db.commit()

        # Generate tokens
        tokens = create_tokens(user.id, user.email, user.role)

        return tokens

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error during login: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
    except Exception as e:
        await db.rollback()
        logger.error(f"Unexpected error during login: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """
    Get a user by ID

    Args:
        db: Database session
        user_id: User ID

    Returns:
        User object or None if not found
    """
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()
    except SQLAlchemyError as e:
        logger.error(f"Database error when fetching user ID {user_id}: {str(e)}")
        return None


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
        return None


async def update_user(db: AsyncSession, user_id: int, user_data: UserUpdate) -> User:
    """
    Update user information

    Args:
        db: Database session
        user_id: User ID
        user_data: User update data

    Returns:
        Updated user object

    Raises:
        HTTPException: If user not found or passwords don't match
    """
    try:
        # Check if user exists
        user = await get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {user_id} not found")

        # Check if passwords match if provided
        if user_data.password is not None:
            if not user_data.confirm_password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Confirm password is required when changing password",
                )
            if user_data.password != user_data.confirm_password:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")

            # Update password
            # Manually hash the password since direct attribute assignment bypasses __init__
            user.password = User.hash_password(user_data.password)

        # Update other fields if provided
        if user_data.first_name is not None:
            user.first_name = user_data.first_name
        if user_data.last_name is not None:
            user.last_name = user_data.last_name
        if user_data.profile_image is not None:
            user.profile_image = user_data.profile_image

        await db.commit()
        await db.refresh(user)

        # Sync author data if user has an author profile
        if user.role == UserRole.AUTHOR and (
            user_data.first_name is not None or user_data.last_name is not None or user_data.profile_image is not None
        ):
            await sync_user_author_data(db, user_id)

        return user

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error when updating user ID {user_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")
    except Exception as e:
        await db.rollback()
        logger.error(f"Unexpected error when updating user ID {user_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


async def verify_email(db: AsyncSession, token: str) -> bool:
    """
    Verify user email with verification token

    Args:
        db: Database session
        token: Verification token

    Returns:
        True if verification successful, False otherwise
    """
    try:
        # Find user by verification token
        result = await db.execute(select(User).where(User.verification_token == token))
        user = result.scalars().first()

        if not user:
            return False

        # Verify user
        user.verify_user()
        await db.commit()

        return True

    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error during email verification: {str(e)}")
        return False


async def request_password_reset(db: AsyncSession, email: str) -> Tuple[bool, Optional[str]]:
    """
    Request password reset for a user

    Args:
        db: Database session
        email: User email

    Returns:
        Tuple of (success, token)
    """
    try:
        # Find user by email
        user = await get_user_by_email(db, email)

        if not user:
            # Don't reveal that the user doesn't exist
            return False, None

        # Generate verification token for password reset
        token = user.generate_verification_token()
        await db.commit()

        return True, token

    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error during password reset request: {str(e)}")
        return False, None


async def sync_user_author_data(db: AsyncSession, user_id: int) -> None:
    """
    Sync relevant data between user and author profiles

    Args:
        db: Database session
        user_id: User ID
    """
    try:
        # Get user with author
        user = await get_user_by_id(db, user_id)
        if not user or not user.author_id:
            return

        # Get author
        author = await author_service.get_author_by_id(db, user.author_id)
        if not author:
            return

        # Update author name if user name changed
        new_name = user.get_full_name()
        if author.name != new_name:
            # Check if new name is available
            unique_name = await author_service.generate_unique_author_name(db, new_name)
            author.name = unique_name
            author.slug = Author.generate_slug(unique_name)

        # Update profile image if available
        if user.profile_image and not author.profile_image:
            author.profile_image = user.profile_image

        # Commit changes
        db.add(author)
        await db.commit()
        logger.info(f"Synchronized author data for user {user_id}")

    except Exception as e:
        await db.rollback()
        logger.error(f"Error synchronizing author data for user {user_id}: {str(e)}")


async def reset_password(db: AsyncSession, token: str, password: str) -> bool:
    """
    Reset user password with verification token

    Args:
        db: Database session
        token: Verification token
        password: New password

    Returns:
        True if reset successful, False otherwise
    """
    try:
        # Find user by verification token
        result = await db.execute(select(User).where(User.verification_token == token))
        user = result.scalars().first()

        if not user:
            return False

        # Update password and clear verification token
        # Manually hash the password since direct attribute assignment bypasses __init__
        user.password = User.hash_password(password)
        user.verification_token = None

        await db.commit()

        return True

    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error during password reset: {str(e)}")
        return False
