from functools import lru_cache

import jwt
from fastapi import Depends, Request, security
from structlog import get_logger

from frost_shard.auth import exceptions
from frost_shard.auth.models import AuthConfig, RequestUserModel
from frost_shard.auth.services import (
    AuthRoutingService,
    AuthService,
    HttpService,
    TokenService,
)
from frost_shard.settings import settings

logger = get_logger(__name__)

bearer = security.HTTPBearer()


async def get_access_token(
    request: Request,
) -> security.HTTPAuthorizationCredentials:
    """Take the jwt token from either cookie or header and decode it."""
    # Try to take the token from the cookie first
    if cookie_token := request.cookies.get(settings.TOKEN_FIELD_NAME):
        return security.HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=cookie_token,
        )
    # Try to take it from the header using regular FastAPI bearer
    if header_token := await bearer(request):
        return header_token
    # Raise if both fail
    raise exceptions.AuthenticationError("Missing token")


@lru_cache(maxsize=1)
def get_auth_service() -> AuthService:
    """Prepare the authentication service with it's dependencies."""
    config = AuthConfig()
    routing_service = AuthRoutingService(config)
    http_service = HttpService(config.base_auth_url)
    token_service = TokenService(config, http_service)
    # TODO: Maybe split it to 2 separate dependencies
    return AuthService(
        routing_service=routing_service,
        token_service=token_service,
    )


async def get_request_user(
    token: security.HTTPAuthorizationCredentials = Depends(get_access_token),
    auth_service: AuthService = Depends(get_auth_service),
) -> RequestUserModel:
    """Decode the jwt token and build a user object from it's payload."""
    try:
        decoded_token = await auth_service.decode_token(token.credentials)
    except jwt.exceptions.PyJWTError:
        raise exceptions.AuthenticationError("Invalid token (failed to decode)")
    # TODO: Move those under just custom claim
    email = decoded_token.get(f"{settings.CUSTOM_CLAIM}/email")
    roles = decoded_token.get(f"{settings.CUSTOM_CLAIM}/roles")

    if not email or not roles:
        logger.error(
            "Token is missing required fields",
            decoded_token=decoded_token,
        )
        raise exceptions.AuthenticationError(
            "Invalid token (missing required claims)",
        )

    return RequestUserModel(email=email, roles=roles)
