from pydantic import BaseSettings


class Settings(BaseSettings):
    """Basic settings for the application."""

    # Application
    TITLE: str = "Frost Shard"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "Fully anonymous and detached file storage"
    DEBUG: bool = False

    # API
    DOMAIN: str = "127.0.0.1"
    CORS_ALLOW_ORIGINS: list[str] = []
    # TODO: Add API prefix

    # Database
    DATABASE_URL: str = ""
    DATABASE_NAME: str = ""

    # Cryptography
    SECRET_KEY: str = ""

    # Auth0
    AUTH0_DOMAIN: str = ""
    AUDIENCE: str = ""
    ISSUER: str = ""
    ALGORITHMS: list[str] = []
    CLIENT_ID: str = ""
    CLIENT_SECRET: str = ""
    TOKEN_FIELD_NAME: str = "access_token"


settings = Settings()
