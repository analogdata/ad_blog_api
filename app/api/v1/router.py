from fastapi import APIRouter
from app.api.v1.health.router import router as health_router
from app.api.v1.tag.router import router as tag_router

router = APIRouter()
router.include_router(health_router, prefix="/health", tags=["health"])
router.include_router(tag_router, prefix="/tag", tags=["tag"])
