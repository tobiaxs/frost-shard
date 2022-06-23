from datetime import datetime, timedelta
from urllib.parse import urlencode, urljoin

import jwt
from fastapi import responses, status
from jwt.algorithms import RSAAlgorithm
from pydantic import HttpUrl

from frost_shard.auth.models import AccessTokenCookie, AuthConfig
from frost_shard.utils.services import HttpService


class TokenService:
    """Service class for handling JWT tokens."""

    JWK_REFRESH_RATE: int = 30

    def __init__(self, config: AuthConfig, http_service: HttpService) -> None:
        self.config = config
        self.http_service = http_service

        self.jwks: list[dict] = []
        self.jwk_refresh_time = datetime.now()

    async def decode_jwt_token(self, token: str) -> dict:
        """Decode a JWT token.

        Args:
            token (str): Token to decode.

        Raises:
            InvalidTokenError: If the token is invalid.

        Returns:
            dict: Decoded data from the token.
        """
        unverified_header = jwt.get_unverified_header(token)
        await self._fetch_jwks()
        jwk = self._get_jwk(unverified_header["kid"])
        if jwk is None:
            raise jwt.InvalidTokenError()

        public_key = RSAAlgorithm.from_jwk(jwk)

        return jwt.decode(
            token,
            public_key,  # type: ignore
            issuer=self.config.base_auth0_url,
            audience=self.config.audience,
            algorithms=self.config.algorithms,
        )

    async def get_jwt_token(self, code: str) -> str:
        """Get a JWT token from the Auth0 API.

        Args:
            code (str): Authorization code.

        Returns:
            str: Received JWT token.
        """
        data = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "audience": self.config.audience,
            "redirect_uri": self.config.base_app_url,
            "grant_type": "authorization_code",
            "code": code,
        }
        response = await self.http_service.request(
            "POST",
            "/oauth/token",
            json=data,
        )
        return response.json()["access_token"]

    async def _fetch_jwks(self) -> None:
        """Fetch the JWKs from the Auth0 API.

        To save some time, the keys are fetched once per 'JWK_REFRESH_RATE'.
        """
        if self.jwk_refresh_time <= datetime.now():
            response = await self.http_service.request(
                "GET",
                "/.well-known/jwks.json",
            )
            self.jwks = response.json()["keys"]
            self.jwk_refresh_time = datetime.now() + timedelta(
                seconds=self.JWK_REFRESH_RATE,
            )

    def _get_jwk(self, kid: str) -> dict | None:
        """Get the JWK for a given key ID.

        Args:
            kid (str): Key ID.

        Returns:
            dict | None: JWK for the key ID.
        """
        return next(
            (key for key in self.jwks if key["kid"] == kid),
            None,
        )


class AuthService:
    """Service class for handling authentication processes."""

    def __init__(self, config: AuthConfig) -> None:
        self.config = config

    def get_authorize_url(self) -> HttpUrl:
        """Get the URL for the Auth0 authorization flow.

        Returns:
            HttpUrl: Authorize URL.
        """
        redirect_url = urljoin(self.config.base_app_url, "/api/auth/callback")
        params = urlencode(
            {
                "client_id": self.config.client_id,
                "redirect_uri": redirect_url,
                "response_type": "code",
                "audience": self.config.audience,
            },
        )
        auth0_authorize_url = urljoin(
            self.config.base_auth0_url,
            f"/authorize?{params}",
        )
        return HttpUrl(auth0_authorize_url, scheme="https")

    def get_logout_url(self) -> HttpUrl:
        """Get the URL for the Auth0 logout flow.

        Returns:
            HttpUrl: Logout URL.
        """
        params = urlencode(
            {
                "returnTo": self.config.base_app_url,
                "client_id": self.config.client_id,
            },
        )
        auth0_logout_url = urljoin(
            self.config.base_auth0_url,
            f"/logout?{params}",
        )
        return HttpUrl(auth0_logout_url, scheme="https")


class Auth0Service:
    """Orchestrator for all the authentication operations using Auth0."""

    def __init__(
        self,
        *,
        auth_service: AuthService,
        token_service: TokenService,
    ) -> None:
        self.auth_service = auth_service
        self.token_service = token_service

    def login(self) -> responses.RedirectResponse:
        """Prepare the redirect to the Auth0 login page."""
        authorize_url = self.auth_service.get_authorize_url()
        return responses.RedirectResponse(
            authorize_url,
            status_code=status.HTTP_302_FOUND,
        )

    async def callback(self, code: str) -> responses.RedirectResponse:
        """Handle the callback from the Auth0 login page and set the cookie."""
        token = await self.token_service.get_jwt_token(code)
        response = responses.RedirectResponse(
            "/",
            status_code=status.HTTP_302_FOUND,
        )
        token_cookie = AccessTokenCookie(value=token)
        response.set_cookie(**token_cookie.dict())
        return response

    def logout(self) -> responses.RedirectResponse:
        """Prepare redirect to the Auth0 logout page and clear the cookie."""
        logout_url = self.auth_service.get_logout_url()
        response = responses.RedirectResponse(
            logout_url,
            status_code=status.HTTP_302_FOUND,
        )
        response.delete_cookie(self.auth_service.config.token_field_name)
        return response

    async def decode_token(self, token: str) -> dict:
        """Decode a JWT token."""
        return await self.token_service.decode_jwt_token(token)
