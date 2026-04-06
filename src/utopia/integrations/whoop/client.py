"""WHOOP API client — httpx-based async client for the WHOOP Developer API.

Fetches physiological data (cycles, sleeps, recoveries, workouts, body
measurements) and returns raw dicts. The PhysiologyService is responsible
for mapping these payloads to ORM objects.

All paginated endpoints are auto-iterated until no next_token is returned.

References:
  https://developer.whoop.com/api/
  Base URL: https://api.prod.whoop.com/developer
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

BASE_URL = "https://api.prod.whoop.com/developer"


class WhoopAPIError(Exception):
    """Raised when the WHOOP API returns a non-2xx response."""

    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"WHOOP API {status_code}: {detail}")


class WhoopClient:
    """Async HTTP client for the WHOOP Developer API (v1).

    Requires a valid OAuth access token obtained via the WHOOP OAuth flow
    (stored in integration.oauth_connections).

    Usage::

        async with WhoopClient(access_token="...") as client:
            cycles = await client.fetch_cycles(start="2025-01-01T00:00:00.000Z")
            sleeps = await client.fetch_sleeps()
    """

    def __init__(
        self,
        access_token: str,
        *,
        base_url: str = BASE_URL,
        timeout: float = 30.0,
    ) -> None:
        self._access_token = access_token
        self._base_url = base_url
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            },
            timeout=timeout,
        )

    async def __aenter__(self) -> WhoopClient:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.close()

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> dict:
        """Perform a GET request and return the JSON response."""
        response = await self._client.get(path, params=params)
        if response.status_code >= 400:
            detail = response.text[:500]
            raise WhoopAPIError(response.status_code, detail)
        return response.json()

    async def _get_paginated(
        self,
        path: str,
        *,
        start: str | None = None,
        end: str | None = None,
        limit: int = 25,
    ) -> list[dict]:
        """Fetch all pages from a paginated WHOOP endpoint.

        WHOOP paginated endpoints return::

            {
              "records": [...],
              "next_token": "..." | null
            }

        We iterate until next_token is absent or null.
        """
        all_records: list[dict] = []
        next_token: str | None = None

        while True:
            params: dict[str, Any] = {"limit": limit}
            if start is not None:
                params["start"] = start
            if end is not None:
                params["end"] = end
            if next_token is not None:
                params["nextToken"] = next_token

            data = await self._get(path, params=params)
            records = data.get("records", [])
            all_records.extend(records)

            next_token = data.get("next_token")
            if not next_token:
                break

            logger.debug(
                "Fetched %d records from %s, continuing with next_token",
                len(records),
                path,
            )

        logger.info("Fetched %d total records from %s", len(all_records), path)
        return all_records

    # ------------------------------------------------------------------
    # Public API methods
    # ------------------------------------------------------------------

    async def fetch_cycles(
        self,
        *,
        start: str | None = None,
        end: str | None = None,
    ) -> list[dict]:
        """Fetch physiological cycles from the WHOOP API.

        Args:
            start: ISO 8601 datetime string for the start of the range.
            end: ISO 8601 datetime string for the end of the range.

        Returns:
            List of cycle dicts with keys like:
            id, user_id, start, end, timezone_offset, score_state, score
            (score contains strain, kilojoule, average_heart_rate, max_heart_rate).
        """
        return await self._get_paginated(
            "/v1/cycle", start=start, end=end
        )

    async def fetch_sleeps(
        self,
        *,
        start: str | None = None,
        end: str | None = None,
    ) -> list[dict]:
        """Fetch sleep records from the WHOOP API.

        Args:
            start: ISO 8601 datetime string for the start of the range.
            end: ISO 8601 datetime string for the end of the range.

        Returns:
            List of sleep dicts with keys like:
            id, user_id, start, end, score_state, score
            (score contains sleep_performance_percentage, stage_summary,
            sleep_needed, respiratory_rate, etc.).
        """
        return await self._get_paginated(
            "/v1/activity/sleep", start=start, end=end
        )

    async def fetch_recoveries(
        self,
        *,
        start: str | None = None,
        end: str | None = None,
    ) -> list[dict]:
        """Fetch recovery scores from the WHOOP API.

        Args:
            start: ISO 8601 datetime string for the start of the range.
            end: ISO 8601 datetime string for the end of the range.

        Returns:
            List of recovery dicts with keys like:
            cycle_id, sleep_id, user_id, created_at, updated_at,
            score_state, score (contains recovery_score, resting_heart_rate,
            hrv_rmssd_milli, spo2_percentage, skin_temp_celsius,
            user_calibrating).
        """
        return await self._get_paginated(
            "/v1/recovery/cycle", start=start, end=end
        )

    async def fetch_workouts(
        self,
        *,
        start: str | None = None,
        end: str | None = None,
    ) -> list[dict]:
        """Fetch workout records from the WHOOP API.

        Args:
            start: ISO 8601 datetime string for the start of the range.
            end: ISO 8601 datetime string for the end of the range.

        Returns:
            List of workout dicts with keys like:
            id, user_id, start, end, sport_id, score_state, score
            (score contains strain, average_heart_rate, max_heart_rate,
            kilojoule, percent_recorded, zone_duration, etc.).
        """
        return await self._get_paginated(
            "/v1/activity/workout", start=start, end=end
        )

    async def fetch_body_measurement(self) -> dict:
        """Fetch the latest body measurement from the WHOOP API.

        Returns:
            Dict with keys like:
            height_meter, weight_kilogram, max_heart_rate.
        """
        return await self._get("/v1/user/measurement/body")

    async def fetch_profile(self) -> dict:
        """Fetch the authenticated user's profile.

        Returns:
            Dict with keys like: user_id, first_name, last_name, email.
        """
        return await self._get("/v1/user/profile/basic")
