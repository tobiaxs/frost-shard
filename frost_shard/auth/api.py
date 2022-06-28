from fastapi import APIRouter, Depends, Query, responses, status

from frost_shard.auth.dependencies import get_auth_service
from frost_shard.auth.services import AuthService

router = APIRouter(tags=["auth"], prefix="/api/auth")


@router.get(
    "/login",
    status_code=status.HTTP_302_FOUND,
)
def redirect_to_login_page(
    auth_service: AuthService = Depends(get_auth_service),
) -> responses.RedirectResponse:
    """Prepare the redirect to the login page.

    Args:
        auth_service (AuthService): Authentication service.

    Returns:
        RedirectResponse: Redirect to the login page.
    """
    return auth_service.login()


@router.get(
    "/callback",
    status_code=status.HTTP_302_FOUND,
)
async def callback_from_auth(
    code: str = Query(),
    auth_service: AuthService = Depends(get_auth_service),
) -> responses.RedirectResponse:
    """Handle the callback from the login page.

    Args:
        code (str): Authorization code.
        auth_service (AuthService): Authentication service.

    Returns:
        RedirectResponse: Redirect to the application.
    """
    return await auth_service.callback(code)


@router.get(
    "/logout",
    status_code=status.HTTP_302_FOUND,
)
def logout(
    auth_service: AuthService = Depends(get_auth_service),
) -> responses.RedirectResponse:
    """Perform the logout operation and clear the cookie.

    Args:
        auth_service (AuthService): Authentication service.

    Returns:
        RedirectResponse: Redirect to the logout page.
    """
    return auth_service.logout()
