from pydantic import BaseModel, EmailStr


class FileCreateModel(BaseModel):
    """Data model for the file creation."""

    email: EmailStr
