from pydantic import BaseModel, Field, HttpUrl

from frost_shard.settings import settings


class AccessTokenCookie(BaseModel):
    """JWT access token cookie."""

    value: str
    key: str = settings.TOKEN_FIELD_NAME
    max_age: int = 604800  # One week
    httponly: bool = True
    secure: bool = not settings.DEBUG
    samesite: str = "strict"

    class Config:
        frozen = True


class AuthConfig(BaseModel):
    """Authentication configuration."""

    app_domain: str = settings.DOMAIN
    auth0_domain: str = settings.AUTH0_DOMAIN
    client_id: str = settings.CLIENT_ID
    client_secret: str = settings.CLIENT_SECRET
    audience: str = settings.AUDIENCE
    algorithms: list[str] = Field(default_factory=lambda: settings.ALGORITHMS)
    token_field_name: str = settings.TOKEN_FIELD_NAME

    @property
    def base_auth0_url(self) -> HttpUrl:
        """Get the base URL for the Auth0 API.

        Returns:
            HttpUrl: Base URL for the Auth0 API.
        """
        return HttpUrl(f"https://{self.auth0_domain}/", scheme="https")

    @property
    def base_app_url(self) -> HttpUrl:
        """Get the base URL for the app.

        Returns:
            HttpUrl: Base URL.
        """
        return HttpUrl(
            f"https://{self.app_domain}:8000"
            if settings.DEBUG
            else f"http://{self.app_domain}",
            scheme="https",
        )

    class Config:
        frozen = True
