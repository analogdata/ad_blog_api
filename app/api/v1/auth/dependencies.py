from typing import Optional, Annotated
import logging

from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.db_init import get_session
from app.db.models.user import User, UserRole
from app.api.v1.auth.security import verify_access_token
from app.api.v1.auth import service

logger = logging.getLogger(__name__)

# OAuth2 scheme for token extraction from request
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    scopes={
        "admin": "Full access to all resources",
        "author": "Access to author resources",
    },
)


async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_session),
) -> User:
    """
    Dependency to get the current authenticated user

    Args:
        security_scopes: Security scopes required for the endpoint
        token: JWT token from request
        db: Database session

    Returns:
        User object

    Raises:
        HTTPException: If authentication fails
    """
    # Set authenticate value based on scopes
    authenticate_value = f'Bearer scope="{security_scopes.scope_str}"' if security_scopes.scopes else "Bearer"

    # Verify token and get token data
    try:
        token_data = verify_access_token(token)
    except HTTPException as e:
        e.headers = {"WWW-Authenticate": authenticate_value}
        raise

    # Get user from database
    user = await service.get_user_by_id(db, int(token_data.sub))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": authenticate_value},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": authenticate_value},
        )

    # Check if user is verified
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please verify your email before accessing this resource.",
            headers={"WWW-Authenticate": authenticate_value},
        )

    # Check if user has required scopes
    if security_scopes.scopes:
        # Admin role has access to all scopes
        if user.role == UserRole.ADMIN:
            return user

        # Check if user role is in required scopes
        if user.role.value not in security_scopes.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions. Required: {security_scopes.scope_str}",
                headers={"WWW-Authenticate": authenticate_value},
            )

    return user


# Typed dependencies for different user roles
CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_admin_user(user: Annotated[User, Security(get_current_user, scopes=["admin"])]) -> User:
    """
    Dependency to get the current admin user

    Args:
        user: User from get_current_user dependency with admin scope

    Returns:
        User object with admin role
    """
    return user


async def get_author_user(user: Annotated[User, Security(get_current_user, scopes=["author", "admin"])]) -> User:
    """
    Dependency to get the current author user

    Args:
        user: User from get_current_user dependency with author or admin scope

    Returns:
        User object with author or admin role
    """
    return user


# Typed dependencies for different user roles
AdminUser = Annotated[User, Depends(get_admin_user)]
AuthorUser = Annotated[User, Depends(get_author_user)]


async def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_session),
) -> Optional[User]:
    """
    Dependency to get the current user if authenticated, or None if not

    Args:
        token: JWT token from request (optional)
        db: Database session

    Returns:
        User object or None
    """
    if not token:
        return None

    try:
        token_data = verify_access_token(token)
        user = await service.get_user_by_id(db, int(token_data.sub))
        # Only return the user if they are both active and verified
        return user if user and user.is_active and user.is_verified else None
    except (HTTPException, ValueError, TypeError) as e:
        # Log the error if needed
        logger.error(f"Error getting optional user: {e}")
        return None


# Typed dependency for optional user
OptionalUser = Annotated[Optional[User], Depends(get_optional_user)]
