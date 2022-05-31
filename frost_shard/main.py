from fastapi import FastAPI
from structlog import get_logger

from frost_shard.settings import settings

logger = get_logger(__name__)


def create_application() -> FastAPI:
    """Create the FastAPI application."""
    logger.info("Creating app")
    return FastAPI(
        title=settings.TITLE,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        docs_url="/api/docs",
    )


app = create_application()
