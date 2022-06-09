from pydantic import BaseSettings


class Settings(BaseSettings):
    """Basic settings for the application."""

    # Application
    TITLE: str = "Frost Shard"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "Fully anonymous and detached file storage"
    DEBUG: bool = False

    # API
    CORS_ALLOW_ORIGINS: list[str] = []

    # Database
    DATABASE_URL: str = ""
    DATABASE_NAME: str = ""


settings = Settings()
