import logging

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.db_init import get_session
from app.api.v1.auth import service
from app.api.v1.auth.schema import (
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    RefreshToken,
    PasswordReset,
    PasswordResetConfirm,
    EmailVerification,
)
from app.api.v1.auth.security import verify_refresh_token, create_tokens

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    responses={
        201: {"description": "User registered successfully"},
        400: {"description": "Validation error"},
        409: {"description": "User with this email already exists"},
        500: {"description": "Internal server error"},
    },
)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_session)):
    """
    Register a new user with email and password
    """
    try:
        user = await service.register_user(db, user_data)
        return user
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error during registration: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.post(
    "/login",
    response_model=Token,
    summary="Login to get access token",
    responses={
        200: {"description": "Login successful"},
        401: {"description": "Authentication failed"},
        500: {"description": "Internal server error"},
    },
)
async def login(login_data: UserLogin, db: AsyncSession = Depends(get_session)):
    """
    Authenticate user and return JWT tokens
    """
    try:
        tokens = await service.login_user(db, login_data)
        return tokens
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.post(
    "/refresh",
    response_model=Token,
    summary="Refresh access token",
    responses={
        200: {"description": "Token refreshed successfully"},
        401: {"description": "Invalid refresh token"},
        500: {"description": "Internal server error"},
    },
)
async def refresh_token(refresh_data: RefreshToken, db: AsyncSession = Depends(get_session)):
    """
    Get a new access token using a refresh token
    """
    try:
        # Verify refresh token
        token_data = verify_refresh_token(refresh_data.refresh_token)

        # Get user from database
        user = await service.get_user_by_id(db, int(token_data.sub))

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User is inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if user is verified
        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email not verified. Please verify your email before using this service.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Generate new tokens
        tokens = create_tokens(user.id, user.email, user.role)
        return tokens

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error during token refresh: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.post(
    "/verify-email",
    summary="Verify email address",
    responses={
        200: {"description": "Email verified successfully"},
        400: {"description": "Invalid verification token"},
        500: {"description": "Internal server error"},
    },
)
async def verify_email(verification_data: EmailVerification, db: AsyncSession = Depends(get_session)):
    """
    Verify user email with verification token
    """
    try:
        success = await service.verify_email(db, verification_data.token)

        if not success:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification token")

        return {"message": "Email verified successfully"}

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error during email verification: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.post(
    "/forgot-password",
    summary="Request password reset",
    responses={
        200: {"description": "Password reset email sent"},
        500: {"description": "Internal server error"},
    },
)
async def forgot_password(reset_data: PasswordReset, db: AsyncSession = Depends(get_session)):
    """
    Request password reset for a user
    """
    try:
        success, _ = await service.request_password_reset(db, reset_data.email)

        # Always return success to prevent email enumeration
        return {"message": "If your email is registered, you will receive a password reset link"}

    except Exception as e:
        logger.error(f"Unexpected error during password reset request: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.post(
    "/reset-password",
    summary="Reset password with token",
    responses={
        200: {"description": "Password reset successful"},
        400: {"description": "Invalid reset token or passwords don't match"},
        500: {"description": "Internal server error"},
    },
)
async def reset_password(reset_data: PasswordResetConfirm, db: AsyncSession = Depends(get_session)):
    """
    Reset user password with verification token
    """
    try:
        # Check if passwords match
        if reset_data.password != reset_data.confirm_password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")

        success = await service.reset_password(db, reset_data.token, reset_data.password)

        if not success:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reset token")

        return {"message": "Password reset successful"}

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error during password reset: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.post(
    "/logout",
    summary="Logout user",
    responses={
        200: {"description": "Logout successful"},
    },
)
async def logout(response: Response):
    """
    Logout user (client-side implementation)

    Note: JWT tokens are stateless, so this endpoint doesn't invalidate tokens.
    The client should discard the tokens and clear cookies.
    """
    # Clear any cookies if using cookie-based auth
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")

    return {"message": "Logout successful"}
