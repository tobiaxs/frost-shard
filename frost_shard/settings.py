from pydantic import BaseSettings


class Settings(BaseSettings):
    """Basic settings for the application."""

    # Application
    TITLE: str = "Frost Shard"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "Fully anonymous and detached file storage"
    DEBUG: bool = False
    ENVIRONMENT: str = "local"

    # API
    DOMAIN: str = "127.0.0.1"
    CORS_ALLOW_ORIGINS: list[str] = []
    API_PREFIX: str = "/fs"
    RATE_LIMIT: int = 30

    # Database
    DATABASE_URL: str = ""
    DATABASE_NAME: str = ""

    # Cryptography
    SECRET_KEY: str = ""

    # Auth
    AUTH_DOMAIN: str = ""
    AUDIENCE: str = ""
    ISSUER: str = ""
    ALGORITHMS: list[str] = []
    CLIENT_ID: str = ""
    CLIENT_SECRET: str = ""
    TOKEN_FIELD_NAME: str = "access_token"
    CUSTOM_CLAIM: str = ""

    # Integrations
    SENTRY_DSN: str = ""

    # AWS
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = ""
    AWS_S3_BUCKET_NAME: str = ""


settings = Settings()
