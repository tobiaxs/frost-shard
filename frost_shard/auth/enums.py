import enum


class UserPermission(str, enum.Enum):
    """Permission of the user."""

    READ_FILES = "read:files"
    READ_GLOBAL_FILES = "read:global_files"
    CREATE_FILES = "create:files"


class UserRole(str, enum.Enum):
    """Role of the user."""

    REGULAR = "regular"
    ADMIN = "admin"
