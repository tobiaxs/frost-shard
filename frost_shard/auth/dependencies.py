from functools import lru_cache
from typing import Callable, Iterable

import jwt
from fastapi import Depends, Request, security
from structlog import get_logger

from frost_shard.auth import enums, exceptions, models, services
from frost_shard.settings import settings
from frost_shard.utils.services import HttpService

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
def get_auth_service() -> services.AuthService:
    """Prepare the authentication service with it's dependencies."""
    config = models.AuthConfig()
    routing_service = services.AuthRoutingService(config)
    http_service = HttpService(config.base_auth_url)
    token_service = services.TokenService(config, http_service)
    # TODO: Maybe split it to 2 separate dependencies
    return services.AuthService(
        routing_service=routing_service,
        token_service=token_service,
    )


async def get_request_user(
    token: security.HTTPAuthorizationCredentials = Depends(get_access_token),
    auth_service: services.AuthService = Depends(get_auth_service),
) -> models.RequestUserModel:
    """Decode the jwt token and build a user object from it's payload."""
    try:
        decoded_token = await auth_service.decode_token(token.credentials)
    except jwt.exceptions.PyJWTError:
        raise exceptions.AuthenticationError("Invalid token (failed to decode)")

    custom_claims = decoded_token[settings.CUSTOM_CLAIM]
    email = custom_claims.get("email")
    roles = custom_claims.get("roles")

    if email is None or roles is None:
        logger.error(
            "Token is missing required fields",
            decoded_token=decoded_token,
        )
        raise exceptions.AuthenticationError(
            "Invalid token (missing required claims)",
        )

    return models.RequestUserModel(
        email=email,
        permissions=set(decoded_token.get("permissions", set())),
        roles=set(roles),
    )


def has_permissions(
    permissions: Iterable[enums.UserPermission],
) -> Callable[[models.RequestUserModel], None]:
    """Prepare a function for checking given permissions."""

    def _has_permissions(
        user: models.RequestUserModel = Depends(get_request_user),
    ) -> None:
        """Check if user is having proper set of permissions."""
        required_permissions = set(permissions)
        if not required_permissions.issubset(user.permissions):
            raise exceptions.PermissionsError()

    return _has_permissions
