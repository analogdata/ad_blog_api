from fastapi import APIRouter
from app.api.v1.health.router import router as health_router
from app.api.v1.tag.router import router as tag_router
from app.api.v1.auth.router import router as auth_router
from app.api.v1.user.router import router as user_router
from app.api.v1.category.router import router as category_router
from app.api.v1.author.router import router as author_router

router = APIRouter()
router.include_router(health_router, prefix="/health", tags=["health"])
router.include_router(tag_router, prefix="/tag", tags=["tag"])
router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(user_router, prefix="/user", tags=["user"])
router.include_router(category_router, prefix="/category", tags=["category"])
router.include_router(author_router, prefix="/author", tags=["author"])
