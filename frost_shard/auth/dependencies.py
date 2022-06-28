from functools import lru_cache

from frost_shard.auth.models import AuthConfig
from frost_shard.auth.services import (
    AuthRoutingService,
    AuthService,
    HttpService,
    TokenService,
)


@lru_cache(maxsize=1)
def get_auth_service() -> AuthService:
    """Prepare the authentication service with it's dependencies."""
    config = AuthConfig()
    routing_service = AuthRoutingService(config)
    http_service = HttpService(config.base_auth_url)
    token_service = TokenService(config, http_service)
    return AuthService(
        routing_service=routing_service,
        token_service=token_service,
    )
