"""WHOOP API client stub.

Placeholder for the WHOOP v2 API integration. Methods raise NotImplementedError
until the live OAuth + HTTP implementation is added.

The PhysiologyService accepts structured data objects — this client is
responsible for fetching raw payloads from the WHOOP API and mapping
them to the appropriate Create schemas.
"""


class WhoopClient:
    """HTTP client for the WHOOP v2 API.

    Requires a valid OAuth access token obtained via the WHOOP OAuth flow
    (stored in integration.oauth_connections).
    """

    def __init__(self, access_token: str) -> None:
        self._access_token = access_token

    async def fetch_cycles(self, *, start: str | None = None, end: str | None = None) -> list[dict]:
        """Fetch physiological cycles from the WHOOP API."""
        raise NotImplementedError("WHOOP API client not yet implemented")

    async def fetch_sleeps(self, *, start: str | None = None, end: str | None = None) -> list[dict]:
        """Fetch sleep records from the WHOOP API."""
        raise NotImplementedError("WHOOP API client not yet implemented")

    async def fetch_recoveries(self, *, start: str | None = None, end: str | None = None) -> list[dict]:
        """Fetch recovery scores from the WHOOP API."""
        raise NotImplementedError("WHOOP API client not yet implemented")

    async def fetch_workouts(self, *, start: str | None = None, end: str | None = None) -> list[dict]:
        """Fetch workout records from the WHOOP API."""
        raise NotImplementedError("WHOOP API client not yet implemented")

    async def fetch_body_measurement(self) -> dict:
        """Fetch body measurement data from the WHOOP API."""
        raise NotImplementedError("WHOOP API client not yet implemented")
