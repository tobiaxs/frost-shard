from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ratelimit import RateLimitMiddleware, Rule, types
from ratelimit.backends.simple import MemoryBackend

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


def add_rate_limiter(app: FastAPI) -> None:
    """Add rate limiter middleware to limit the number of requests."""

    async def auth_func(scope: types.Scope) -> tuple[str, str]:
        """Recognize user by either the token or the IP address.

        Args:
            scope (Scope): request information.

        Returns:
            tuple[str, str]: token or IP and a group.
        """
        for header, value in scope["headers"]:
            if header == "authorization":
                return value, "default"
        return scope["client"], "default"

    app.add_middleware(
        RateLimitMiddleware,
        authenticate=auth_func,
        backend=MemoryBackend(),
        config={
            # User can access resources only once per 'RATE_LIMIT' seconds
            r"^/*": [  # noqa: WPS360
                Rule(second=settings.RATE_LIMIT, group="default"),
            ],
        },
    )


def init_sentry(app: FastAPI) -> None:  # pragma: no cover
    """Initialize Sentry middleware and add it to the app."""
    import sentry_sdk
    from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
    )
    app.add_middleware(SentryAsgiMiddleware)


def init_prometheus_metrics(app: FastAPI) -> None:  # pragma: no cover
    """Add Prometheus metrics middleware and expose metrics endpoint."""
    from starlette_exporter import PrometheusMiddleware, handle_metrics

    app.add_middleware(PrometheusMiddleware, app_name=settings.TITLE)
    app.add_route(f"{settings.API_PREFIX}/metrics", handle_metrics)


def bootstrap(app: FastAPI) -> None:
    """Initialize all the additional components of the application."""
    add_cors(app)
    add_rate_limiter(app)

    if not settings.DEBUG:  # pragma: no cover
        init_sentry(app)
        init_prometheus_metrics(app)
