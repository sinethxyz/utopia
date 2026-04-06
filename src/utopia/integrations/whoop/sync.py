"""WHOOP sync orchestrator.

Coordinates fetching data from the WHOOP API, mapping responses to
Create schemas, and persisting through the PhysiologyService.

Usage::

    async with WhoopClient(access_token="...") as client:
        result = await sync_whoop_data(client, operator_id, svc)
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field

from utopia.integrations.whoop.client import WhoopClient
from utopia.integrations.whoop.mapper import (
    map_body_measurement,
    map_cycle,
    map_recovery,
    map_sleep,
    map_workout,
)
from utopia.services.physiology_service import PhysiologyService

logger = logging.getLogger(__name__)


@dataclass
class SyncResult:
    """Summary of a WHOOP sync operation."""

    cycles_synced: int = 0
    sleeps_synced: int = 0
    recoveries_synced: int = 0
    workouts_synced: int = 0
    body_measurement_synced: bool = False
    errors: list[str] = field(default_factory=list)


async def sync_whoop_data(
    client: WhoopClient,
    operator_id: uuid.UUID,
    svc: PhysiologyService,
    *,
    start: str | None = None,
    end: str | None = None,
) -> SyncResult:
    """Fetch all WHOOP data and persist through PhysiologyService.

    Args:
        client: Authenticated WhoopClient instance.
        operator_id: The operator to associate the data with.
        svc: PhysiologyService for persistence.
        start: Optional ISO 8601 start datetime for data range.
        end: Optional ISO 8601 end datetime for data range.

    Returns:
        SyncResult with counts and any errors encountered.
    """
    result = SyncResult()

    # --- Cycles ---
    try:
        raw_cycles = await client.fetch_cycles(start=start, end=end)
        for raw in raw_cycles:
            data = map_cycle(operator_id, raw)
            await svc.upsert_cycle(data)
            result.cycles_synced += 1
    except Exception as exc:
        msg = f"Failed to sync cycles: {exc}"
        logger.error(msg)
        result.errors.append(msg)

    # --- Sleeps ---
    try:
        raw_sleeps = await client.fetch_sleeps(start=start, end=end)
        for raw in raw_sleeps:
            data = map_sleep(operator_id, raw)
            await svc.upsert_sleep(data)
            result.sleeps_synced += 1
    except Exception as exc:
        msg = f"Failed to sync sleeps: {exc}"
        logger.error(msg)
        result.errors.append(msg)

    # --- Recoveries ---
    try:
        raw_recoveries = await client.fetch_recoveries(start=start, end=end)
        for raw in raw_recoveries:
            data = map_recovery(operator_id, raw)
            await svc.upsert_recovery(data)
            result.recoveries_synced += 1
    except Exception as exc:
        msg = f"Failed to sync recoveries: {exc}"
        logger.error(msg)
        result.errors.append(msg)

    # --- Workouts ---
    try:
        raw_workouts = await client.fetch_workouts(start=start, end=end)
        for raw in raw_workouts:
            data = map_workout(operator_id, raw)
            await svc.upsert_workout(data)
            result.workouts_synced += 1
    except Exception as exc:
        msg = f"Failed to sync workouts: {exc}"
        logger.error(msg)
        result.errors.append(msg)

    # --- Body Measurement ---
    try:
        raw_body = await client.fetch_body_measurement()
        data = map_body_measurement(operator_id, raw_body)
        await svc.record_body_measurement(data)
        result.body_measurement_synced = True
    except Exception as exc:
        msg = f"Failed to sync body measurement: {exc}"
        logger.error(msg)
        result.errors.append(msg)

    # Commit all changes
    await svc.commit()

    logger.info(
        "WHOOP sync complete: %d cycles, %d sleeps, %d recoveries, "
        "%d workouts, body=%s, errors=%d",
        result.cycles_synced,
        result.sleeps_synced,
        result.recoveries_synced,
        result.workouts_synced,
        result.body_measurement_synced,
        len(result.errors),
    )

    return result
