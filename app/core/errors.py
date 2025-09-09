from typing import Any, Dict, Optional
from fastapi import HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from pydantic import ValidationError


class BaseAPIException(HTTPException):
    """Base class for all API exceptions"""

    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[Dict[str, str]] = None,
        code: Optional[str] = None,
    ):
        self.code = code
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class NotFoundException(BaseAPIException):
    """Exception raised when a resource is not found"""

    def __init__(
        self,
        detail: str = "Resource not found",
        headers: Optional[Dict[str, str]] = None,
        code: Optional[str] = "not_found",
    ):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            headers=headers,
            code=code,
        )


class ConflictException(BaseAPIException):
    """Exception raised when there is a conflict with existing resources"""

    def __init__(
        self,
        detail: str = "Resource conflict",
        headers: Optional[Dict[str, str]] = None,
        code: Optional[str] = "conflict",
    ):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            headers=headers,
            code=code,
        )


class BadRequestException(BaseAPIException):
    """Exception raised for invalid request parameters"""

    def __init__(
        self,
        detail: str = "Invalid request",
        headers: Optional[Dict[str, str]] = None,
        code: Optional[str] = "bad_request",
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            headers=headers,
            code=code,
        )


class UnauthorizedException(BaseAPIException):
    """Exception raised when authentication is required"""

    def __init__(
        self,
        detail: str = "Authentication required",
        headers: Optional[Dict[str, str]] = None,
        code: Optional[str] = "unauthorized",
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers=headers,
            code=code,
        )


class ForbiddenException(BaseAPIException):
    """Exception raised when user doesn't have permission"""

    def __init__(
        self,
        detail: str = "Permission denied",
        headers: Optional[Dict[str, str]] = None,
        code: Optional[str] = "forbidden",
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            headers=headers,
            code=code,
        )


class InternalServerErrorException(BaseAPIException):
    """Exception raised for internal server errors"""

    def __init__(
        self,
        detail: str = "Internal server error",
        headers: Optional[Dict[str, str]] = None,
        code: Optional[str] = "internal_error",
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            headers=headers,
            code=code,
        )


# Error response models
class ErrorDetail(Dict[str, Any]):
    """Error detail model"""

    pass


class ErrorResponse(Dict[str, Any]):
    """Standard error response format"""

    pass


# Exception handlers
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handler for HTTPException"""
    headers = getattr(exc, "headers", None)

    error_response = ErrorResponse(
        error=ErrorDetail(
            code=getattr(exc, "code", "http_error"),
            message=exc.detail,
            status_code=exc.status_code,
        )
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response,
        headers=headers,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handler for RequestValidationError"""
    errors = []
    for error in exc.errors():
        error_detail = {
            "loc": error["loc"],
            "msg": error["msg"],
            "type": error["type"],
        }
        errors.append(error_detail)

    error_response = ErrorResponse(
        error=ErrorDetail(
            code="validation_error",
            message="Validation error",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            errors=errors,
        )
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response,
    )


async def pydantic_validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handler for Pydantic ValidationError"""
    errors = []
    for error in exc.errors():
        error_detail = {
            "loc": error["loc"],
            "msg": error["msg"],
            "type": error["type"],
        }
        errors.append(error_detail)

    error_response = ErrorResponse(
        error=ErrorDetail(
            code="validation_error",
            message="Validation error",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            errors=errors,
        )
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response,
    )


async def python_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handler for unhandled exceptions"""
    error_response = ErrorResponse(
        error=ErrorDetail(
            code="internal_error",
            message="An unexpected error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response,
    )
