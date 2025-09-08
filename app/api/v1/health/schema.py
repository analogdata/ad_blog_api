from pydantic import BaseModel
from typing import Optional


class HTTPError(BaseModel):
    detail: str
    status_code: int
    error_type: Optional[str] = None


class StatusResponse(BaseModel):
    status: str = "ok"


class Health(BaseModel):
    ping: str
    status: str = "ok"
    environment: str
    testing: bool
    database_url: str
    debug: bool
