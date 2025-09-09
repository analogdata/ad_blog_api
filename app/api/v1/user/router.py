import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr

from app.db.db_init import get_session
from app.api.v1.user import service
from app.api.v1.user.schema import (
    UserProfileUpdate,
    UserResponse,
    AdminUserResponse,
    ProfileUpdateResponse,
    AdminPasswordResetRequest,
)
from app.api.v1.auth.dependencies import CurrentUser, AdminUser

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/profile",
    response_model=UserResponse,
    summary="Get current user profile",
    responses={
        200: {"description": "User profile retrieved successfully"},
        401: {"description": "Not authenticated"},
        500: {"description": "Internal server error"},
    },
)
async def get_profile(current_user: CurrentUser):
    """
    Get the profile of the currently authenticated user
    """
    return current_user


@router.put(
    "/profile",
    response_model=ProfileUpdateResponse,
    summary="Update current user profile",
    responses={
        200: {"description": "User profile updated successfully"},
        400: {"description": "Validation error"},
        401: {"description": "Not authenticated"},
        500: {"description": "Internal server error"},
    },
)
async def update_profile(
    profile_data: UserProfileUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_session),
):
    """
    Update the profile of the currently authenticated user
    """
    try:
        # Store original email to check if it was changed
        original_email = current_user.email

        updated_user = await service.update_user_profile(db, current_user.id, profile_data)

        # Check if email was changed and provide appropriate response
        if profile_data.email and profile_data.email != original_email:
            return {
                "user": updated_user,
                "message": "Profile updated successfully. You need to verify your new email address. Please check your inbox for verification instructions.",
                "email_changed": True,
                "verification_required": True,
            }

        return {"user": updated_user, "message": "Profile updated successfully", "email_changed": False}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating profile: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.get(
    "/list",
    response_model=List[AdminUserResponse],
    summary="List all users (admin only)",
    responses={
        200: {"description": "Users retrieved successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized"},
        500: {"description": "Internal server error"},
    },
)
async def list_users(
    admin_user: AdminUser,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_session),
):
    """
    List all users (admin only)
    """
    try:
        users = await service.get_users(db, skip=skip, limit=limit)
        return users
    except Exception as e:
        logger.error(f"Unexpected error listing users: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.get(
    "/{email}",
    response_model=AdminUserResponse,
    summary="Get user by email (admin only)",
    responses={
        200: {"description": "User retrieved successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized"},
        404: {"description": "User not found"},
        500: {"description": "Internal server error"},
    },
)
async def get_user_by_email(
    email: EmailStr,
    admin_user: AdminUser,
    db: AsyncSession = Depends(get_session),
):
    """
    Get a user by email (admin only)
    """
    try:
        user = await service.get_user_by_email(db, email)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with email {email} not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting user by email: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user (admin only)",
    responses={
        204: {"description": "User deleted successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized"},
        404: {"description": "User not found"},
        500: {"description": "Internal server error"},
    },
)
async def delete_user(
    user_id: int,
    admin_user: AdminUser,
    db: AsyncSession = Depends(get_session),
):
    """
    Delete a user (admin only)
    """
    try:
        success = await service.delete_user(db, user_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {user_id} not found")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error deleting user: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.post(
    "/{user_id}/reset-password",
    status_code=status.HTTP_200_OK,
    summary="Reset user password (admin only)",
    responses={
        200: {"description": "Password reset successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized"},
        404: {"description": "User not found"},
        500: {"description": "Internal server error"},
    },
)
async def admin_reset_password(
    user_id: int,
    reset_data: AdminPasswordResetRequest,
    admin_user: AdminUser,
    db: AsyncSession = Depends(get_session),
):
    """
    Reset a user's password (admin only)

    Returns the new password. If no custom password is provided, a random password will be generated.
    """
    try:
        new_password = await service.admin_reset_password(db, user_id, reset_data.password)
        if not new_password:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {user_id} not found")

        # Indicate whether the password was custom or generated
        password_type = "custom" if reset_data.password else "generated"
        return {"message": "Password reset successfully", "new_password": new_password, "password_type": password_type}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error resetting password: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")
