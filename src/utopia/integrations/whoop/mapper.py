"""WHOOP API response mappers.

Converts raw WHOOP API JSON payloads into Pydantic Create schemas
that the PhysiologyService accepts. Each mapper is a pure function
that extracts and transforms fields from the WHOOP response format.

The source_payload field always preserves the full raw response
for debugging and future re-processing.
"""

from __future__ import annotations

import datetime
import uuid
from decimal import Decimal

from utopia.schemas.physiology import (
    WhoopBodyMeasurementCreate,
    WhoopCycleCreate,
    WhoopRecoveryCreate,
    WhoopSleepCreate,
    WhoopWorkoutCreate,
)


def map_cycle(operator_id: uuid.UUID, raw: dict) -> WhoopCycleCreate:
    """Map a WHOOP cycle API response to a WhoopCycleCreate schema."""
    score = raw.get("score") or {}
    return WhoopCycleCreate(
        operator_id=operator_id,
        provider_cycle_id=raw["id"],
        whoop_user_id=raw.get("user_id"),
        cycle_start=_parse_dt(raw.get("start")),
        cycle_end=_parse_dt(raw.get("end")),
        timezone_offset=raw.get("timezone_offset"),
        score_state=raw.get("score_state"),
        strain=_to_decimal(score.get("strain")),
        kilojoule=_to_decimal(score.get("kilojoule")),
        average_heart_rate=score.get("average_heart_rate"),
        max_heart_rate=score.get("max_heart_rate"),
        source_payload=raw,
    )


def map_sleep(operator_id: uuid.UUID, raw: dict) -> WhoopSleepCreate:
    """Map a WHOOP sleep API response to a WhoopSleepCreate schema."""
    score = raw.get("score") or {}
    stage_summary = score.get("stage_summary") or {}
    return WhoopSleepCreate(
        operator_id=operator_id,
        provider_sleep_id=uuid.UUID(str(raw["id"])),
        provider_cycle_id=raw.get("cycle_id"),
        sleep_start=_parse_dt(raw.get("start")),
        sleep_end=_parse_dt(raw.get("end")),
        sleep_performance_pct=_to_decimal(score.get("sleep_performance_percentage")),
        total_in_bed_ms=stage_summary.get("total_in_bed_time_milli"),
        total_asleep_ms=stage_summary.get("total_light_sleep_time_milli", 0)
        + stage_summary.get("total_slow_wave_sleep_time_milli", 0)
        + stage_summary.get("total_rem_sleep_time_milli", 0)
        if stage_summary
        else None,
        slow_wave_ms=stage_summary.get("total_slow_wave_sleep_time_milli"),
        rem_ms=stage_summary.get("total_rem_sleep_time_milli"),
        light_ms=stage_summary.get("total_light_sleep_time_milli"),
        awake_ms=stage_summary.get("total_awake_time_milli"),
        source_payload=raw,
    )


def map_recovery(operator_id: uuid.UUID, raw: dict) -> WhoopRecoveryCreate:
    """Map a WHOOP recovery API response to a WhoopRecoveryCreate schema."""
    score = raw.get("score") or {}
    return WhoopRecoveryCreate(
        operator_id=operator_id,
        provider_cycle_id=raw["cycle_id"],
        provider_sleep_id=uuid.UUID(str(raw["sleep_id"])),
        whoop_user_id=raw.get("user_id"),
        recorded_at=_parse_dt(raw.get("created_at")) or datetime.datetime.now(tz=datetime.timezone.utc),
        updated_at_source=_parse_dt(raw.get("updated_at")),
        score_state=raw.get("score_state", "PENDING_SCORE"),
        recovery_score=score.get("recovery_score"),
        resting_heart_rate=score.get("resting_heart_rate"),
        hrv_rmssd_milli=_to_decimal(score.get("hrv_rmssd_milli")),
        spo2_percentage=_to_decimal(score.get("spo2_percentage")),
        skin_temp_celsius=_to_decimal(score.get("skin_temp_celsius")),
        user_calibrating=score.get("user_calibrating"),
        source_payload=raw,
    )


def map_workout(operator_id: uuid.UUID, raw: dict) -> WhoopWorkoutCreate:
    """Map a WHOOP workout API response to a WhoopWorkoutCreate schema."""
    score = raw.get("score") or {}
    return WhoopWorkoutCreate(
        operator_id=operator_id,
        provider_workout_id=uuid.UUID(str(raw["id"])),
        workout_type=str(raw.get("sport_id")) if raw.get("sport_id") else None,
        workout_start=_parse_dt(raw.get("start")),
        workout_end=_parse_dt(raw.get("end")),
        strain=_to_decimal(score.get("strain")),
        average_heart_rate=score.get("average_heart_rate"),
        max_heart_rate=score.get("max_heart_rate"),
        source_payload=raw,
    )


def map_body_measurement(
    operator_id: uuid.UUID, raw: dict
) -> WhoopBodyMeasurementCreate:
    """Map a WHOOP body measurement API response to a Create schema."""
    height_m = raw.get("height_meter")
    weight_kg = raw.get("weight_kilogram")
    return WhoopBodyMeasurementCreate(
        operator_id=operator_id,
        measured_at=datetime.datetime.now(tz=datetime.timezone.utc),
        height_cm=round(height_m * 100) if height_m else None,
        weight_kg=round(weight_kg) if weight_kg else None,
        max_heart_rate=raw.get("max_heart_rate"),
        source_payload=raw,
    )


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _parse_dt(value: str | None) -> datetime.datetime | None:
    """Parse an ISO 8601 datetime string from the WHOOP API."""
    if value is None:
        return None
    # WHOOP uses ISO 8601 format with Z or +00:00
    return datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))


def _to_decimal(value: float | int | None) -> Decimal | None:
    """Convert a numeric value to Decimal, or None."""
    if value is None:
        return None
    return Decimal(str(value))
