import backoff
from httpx import AsyncClient, ConnectError, Response
from pydantic import HttpUrl


class HttpService:
    """Simple HTTP client for making safe requests to the API."""

    def __init__(
        self,
        base_url: HttpUrl,
        client: AsyncClient | None = None,
    ) -> None:
        if not client:
            client = AsyncClient(
                base_url=base_url,
                headers=self.default_headers,
            )
        self.client = client

    @backoff.on_exception(
        backoff.expo,
        ConnectError,
        max_tries=3,
        max_time=60,
    )
    async def request(self, method: str, url: str, **options) -> Response:
        """Make a request to the API.

        Args:
            method (str): HTTP method to use.
            url (str): Path to be joined with the base URL.

        Returns:
            Response: Response from the API.
        """
        response = await self.client.request(method, url, **options)
        response.raise_for_status()
        return response

    @property
    def default_headers(self) -> dict:
        """Get default headers to use for requests.

        Returns:
            dict: Headers.
        """
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
