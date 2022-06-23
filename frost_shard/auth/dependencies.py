from functools import lru_cache

from frost_shard.auth.models import AuthConfig
from frost_shard.auth.services import (
    Auth0Service,
    AuthService,
    HttpService,
    TokenService,
)


@lru_cache(maxsize=1)
def get_auth0_service() -> Auth0Service:
    """Prepare the Auth0 service with it's dependencies."""
    config = AuthConfig()
    auth_service = AuthService(config)
    http_service = HttpService(config.base_auth0_url)
    token_service = TokenService(config, http_service)
    return Auth0Service(auth_service=auth_service, token_service=token_service)
