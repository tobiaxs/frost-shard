from fastapi import APIRouter, Depends, Query, responses, status

from frost_shard.auth.dependencies import get_auth0_service
from frost_shard.auth.services import Auth0Service

router = APIRouter(tags=["auth"], prefix="/api/auth")


@router.get(
    "/login",
    status_code=status.HTTP_302_FOUND,
)
def redirect_to_auth0(
    auth0_service: Auth0Service = Depends(get_auth0_service),
) -> responses.RedirectResponse:
    """Prepare the redirect to the Auth0 login page.

    Args:
        auth0_service (Auth0Service): Auth0 service.

    Returns:
        RedirectResponse: Redirect to the Auth0 login page.
    """
    return auth0_service.login()


@router.get(
    "/callback",
    status_code=status.HTTP_302_FOUND,
)
async def callback_from_auth0(
    code: str = Query(),
    auth0_service: Auth0Service = Depends(get_auth0_service),
) -> responses.RedirectResponse:
    """Handle the callback from the Auth0 login page.

    Args:
        code (str): Authorization code.
        auth0_service (Auth0Service): Auth0 service.

    Returns:
        RedirectResponse: Redirect to the application.
    """
    return await auth0_service.callback(code)


@router.get(
    "/logout",
    status_code=status.HTTP_302_FOUND,
)
def logout(
    auth0_service: Auth0Service = Depends(get_auth0_service),
) -> responses.RedirectResponse:
    """Perform the logout operation and clear the cookie.

    Args:
        auth0_service (Auth0Service): Auth0 service.

    Returns:
        RedirectResponse: Redirect to the Auth0 logout page.
    """
    return auth0_service.logout()
