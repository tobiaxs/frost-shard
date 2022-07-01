from fastapi import Request, responses, status

from frost_shard.auth import exceptions


def handle_authentication_error(
    _: Request,
    exc: exceptions.AuthenticationError,
) -> responses.Response:
    """Return a JSON response about the authentication error.

    Use the exception message as the response content.
    """
    return responses.JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": str(exc)},
    )


def handle_permission_error(*_) -> responses.JSONResponse:
    """Return a JSON response about the permission error."""
    return responses.JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": "User is not allowed to perform this action"},
    )


EXCEPTION_HANDLERS = frozenset(
    {
        exceptions.AuthenticationError: handle_authentication_error,
        exceptions.PermissionsError: handle_permission_error,
    }.items(),
)
