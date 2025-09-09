from datetime import datetime, timezone
from typing import Dict, Any

from jose import jwt, JWTError
from fastapi import HTTPException, status
from pydantic import ValidationError

from app.core.config import settings
from app.api.v1.auth.schema import TokenData, TokenType, UserRole


def create_access_token(user_id: int, email: str, role: UserRole) -> str:
    """
    Create a JWT access token for the user

    Args:
        user_id: User ID
        email: User email
        role: User role

    Returns:
        JWT access token as string
    """
    expire = datetime.now(timezone.utc) + settings.ACCESS_TOKEN_EXPIRE_DELTA
    issued_at = datetime.now(timezone.utc)

    to_encode = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "type": TokenType.ACCESS,
        "exp": expire,
        "iat": issued_at,
    }

    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(user_id: int, email: str, role: UserRole) -> str:
    """
    Create a JWT refresh token for the user

    Args:
        user_id: User ID
        email: User email
        role: User role

    Returns:
        JWT refresh token as string
    """
    expire = datetime.now(timezone.utc) + settings.REFRESH_TOKEN_EXPIRE_DELTA
    issued_at = datetime.now(timezone.utc)

    to_encode = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "type": TokenType.REFRESH,
        "exp": expire,
        "iat": issued_at,
    }

    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_tokens(user_id: int, email: str, role: UserRole) -> Dict[str, Any]:
    """
    Create both access and refresh tokens for a user

    Args:
        user_id: User ID
        email: User email
        role: User role

    Returns:
        Dictionary containing access_token, refresh_token, token_type and expires_in
    """
    access_token = create_access_token(user_id, email, role)
    refresh_token = create_refresh_token(user_id, email, role)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.jwt_access_token_expire_minutes * 60,  # Convert to seconds
    }


def decode_token(token: str) -> TokenData:
    """
    Decode and validate a JWT token

    Args:
        token: JWT token string

    Returns:
        TokenData object with decoded payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])

        # Convert datetime strings to datetime objects
        if isinstance(payload.get("exp"), (int, float)):
            payload["exp"] = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        if isinstance(payload.get("iat"), (int, float)):
            payload["iat"] = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)

        token_data = TokenData(**payload)
        return token_data

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_access_token(token: str) -> TokenData:
    """
    Verify that a token is a valid access token

    Args:
        token: JWT token string

    Returns:
        TokenData object with decoded payload

    Raises:
        HTTPException: If token is invalid, expired, or not an access token
    """
    token_data = decode_token(token)

    # Check if token is an access token
    if token_data.type != TokenType.ACCESS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token_data


def verify_refresh_token(token: str) -> TokenData:
    """
    Verify that a token is a valid refresh token

    Args:
        token: JWT token string

    Returns:
        TokenData object with decoded payload

    Raises:
        HTTPException: If token is invalid, expired, or not a refresh token
    """
    token_data = decode_token(token)

    # Check if token is a refresh token
    if token_data.type != TokenType.REFRESH:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token_data
