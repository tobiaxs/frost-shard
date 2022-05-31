from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from frost_shard.settings import settings


def add_cors(app: FastAPI) -> None:
    """Add CORS middleware."""
    origins = ["*"] if settings.DEBUG else settings.CORS_ALLOW_ORIGINS

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def bootstrap(app: FastAPI) -> None:
    """Initialize all the additional components of the application."""
    add_cors(app)
