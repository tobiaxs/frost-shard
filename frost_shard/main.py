from fastapi import FastAPI, responses
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
        docs_url=f"{settings.API_PREFIX}/api/docs",
    )


async def redirect_to_docs():
    """Redirect root requests to the docs."""
    return responses.RedirectResponse(f"{settings.API_PREFIX}/api/docs")


app = create_application()

bootstrap(app)

app.add_api_route("/", redirect_to_docs, include_in_schema=False)

app.include_router(internal_router, prefix=settings.API_PREFIX)
app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(v1_router, prefix=settings.API_PREFIX)
