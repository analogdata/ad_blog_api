from fastapi import APIRouter, Depends, status, HTTPException
from app.core.config import get_settings, Settings
from app.api.v1.health.schema import Health, StatusResponse, HTTPError
from app.api.v1.health.service import mask_dsn

router = APIRouter()


@router.get(
    "/status",
    response_model=StatusResponse,
    status_code=status.HTTP_200_OK,
)
def check_status():
    try:
        return StatusResponse(status="ok")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        )


@router.get(
    "/ping",
    response_model=Health,
    status_code=status.HTTP_200_OK,
    responses={
        503: {
            "description": "Service Unavailable",
            "model": HTTPError,
        }
    },
)
def ping(settings: Settings = Depends(get_settings)) -> Health:
    try:
        return Health(
            ping="pong",
            environment=settings.environment,
            testing=settings.testing,
            database_url=mask_dsn(settings.database_url),
            debug=settings.debug,
            status="ok",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        )
