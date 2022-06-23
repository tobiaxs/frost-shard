from fastapi import FastAPI
from structlog import get_logger

from frost_shard.auth.api import router as auth_router
from frost_shard.bootstrap import bootstrap
from frost_shard.internal.api import router as internal_router
from frost_shard.settings import settings
from frost_shard.v1.api import router as v1_router

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

bootstrap(app)

app.include_router(internal_router)
app.include_router(auth_router)
app.include_router(v1_router)
