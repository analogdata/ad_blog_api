from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging

log = logging.getLogger("uvicorn.error")


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_handler(
        request: Request,
        exc: RequestValidationError,
    ):
        # Convert errors to a serializable format
        error_details = []
        for error in exc.errors():
            error_details.append(
                {
                    "loc": error.get("loc", []),
                    "msg": str(error.get("msg", "")),
                    "type": error.get("type", ""),
                }
            )

        return JSONResponse(
            status_code=422,
            content={
                "error": "validation_error",
                "details": error_details,
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_handler(
        request: Request,
        exc: StarletteHTTPException,
    ):
        # Let FastAPI keep the status code; sanitize detail if needed
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail,
            },
        )

    @app.exception_handler(IntegrityError)
    async def integrity_handler(
        request: Request,
        exc: IntegrityError,
    ):
        return JSONResponse(
            status_code=409,
            content={
                "error": "conflict",
            },
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_handler(
        request: Request,
        exc: SQLAlchemyError,
    ):
        log.exception("DB error")
        return JSONResponse(
            status_code=503,
            content={
                "error": "db_unavailable",
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_handler(
        request: Request,
        exc: Exception,
    ):
        log.exception("Unhandled error")
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_server_error",
            },
        )
