import logging
from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from app.api.router import router as api_router
from app.db.db_init import engine
from app.core.config import get_settings

from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("app")
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting application in {settings.environment} environment")
    try:
        logger.info("Attempting to connect to database (async)...")
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        logger.info("Database connection successful (async)")
        yield
    except SQLAlchemyError as e:
        error_msg = f"Database connection failed: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg) from e
    except Exception as e:
        error_msg = f"Unexpected error during startup: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg) from e
    finally:
        logger.info("Disposing database connections (async)")
        await engine.dispose()
        logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Analog Data Blog APIs",
        description="""APIs for managing Blog""",
        version="0.0.1",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )
    app.include_router(api_router, prefix="/api")
    return app


app = create_app()


@app.get("/")
async def root():
    return {"message": "Welcome to Analog Data Blog APIs"}
