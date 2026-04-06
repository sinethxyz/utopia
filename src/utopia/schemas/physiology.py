"""Pydantic schemas for the Physiology subsystem.

Request schemas (Create) and response schemas (Read) for WHOOP integration
tables and derived physiological features.
"""

import datetime
import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# WHOOP Connections
# ---------------------------------------------------------------------------

class WhoopConnectionCreate(BaseModel):
    operator_id: uuid.UUID
    oauth_connection_id: uuid.UUID
    scope_granted: list[str] = Field(default_factory=list)
    last_sync_at: datetime.datetime | None = None


class WhoopConnectionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    operator_id: uuid.UUID
    oauth_connection_id: uuid.UUID
    scope_granted: list[str]
    last_sync_at: datetime.datetime | None
    created_at: datetime.datetime
    updated_at: datetime.datetime


# ---------------------------------------------------------------------------
# WHOOP Body Measurements
# ---------------------------------------------------------------------------

class WhoopBodyMeasurementCreate(BaseModel):
    operator_id: uuid.UUID
    measured_at: datetime.datetime
    height_cm: int | None = None
    weight_kg: int | None = None
    max_heart_rate: int | None = None
    source_payload: dict | None = None


class WhoopBodyMeasurementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    operator_id: uuid.UUID
    measured_at: datetime.datetime
    height_cm: int | None
    weight_kg: int | None
    max_heart_rate: int | None
    source_payload: dict | None
    created_at: datetime.datetime


# ---------------------------------------------------------------------------
# WHOOP Cycles
# ---------------------------------------------------------------------------

class WhoopCycleCreate(BaseModel):
    operator_id: uuid.UUID
    provider_cycle_id: int
    whoop_user_id: int | None = None
    cycle_start: datetime.datetime | None = None
    cycle_end: datetime.datetime | None = None
    timezone_offset: str | None = None
    score_state: str | None = None
    strain: Decimal | None = None
    kilojoule: Decimal | None = None
    average_heart_rate: int | None = None
    max_heart_rate: int | None = None
    source_payload: dict | None = None


class WhoopCycleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    operator_id: uuid.UUID
    provider_cycle_id: int
    whoop_user_id: int | None
    cycle_start: datetime.datetime | None
    cycle_end: datetime.datetime | None
    timezone_offset: str | None
    score_state: str | None
    strain: Decimal | None
    kilojoule: Decimal | None
    average_heart_rate: int | None
    max_heart_rate: int | None
    source_payload: dict | None
    created_at: datetime.datetime
    updated_at: datetime.datetime


# ---------------------------------------------------------------------------
# WHOOP Sleeps
# ---------------------------------------------------------------------------

class WhoopSleepCreate(BaseModel):
    operator_id: uuid.UUID
    provider_sleep_id: uuid.UUID
    provider_cycle_id: int | None = None
    sleep_start: datetime.datetime | None = None
    sleep_end: datetime.datetime | None = None
    sleep_performance_pct: Decimal | None = None
    total_in_bed_ms: int | None = None
    total_asleep_ms: int | None = None
    slow_wave_ms: int | None = None
    rem_ms: int | None = None
    light_ms: int | None = None
    awake_ms: int | None = None
    source_payload: dict | None = None


class WhoopSleepRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    operator_id: uuid.UUID
    provider_sleep_id: uuid.UUID
    provider_cycle_id: int | None
    sleep_start: datetime.datetime | None
    sleep_end: datetime.datetime | None
    sleep_performance_pct: Decimal | None
    total_in_bed_ms: int | None
    total_asleep_ms: int | None
    slow_wave_ms: int | None
    rem_ms: int | None
    light_ms: int | None
    awake_ms: int | None
    source_payload: dict | None
    created_at: datetime.datetime
    updated_at: datetime.datetime


# ---------------------------------------------------------------------------
# WHOOP Recoveries
# ---------------------------------------------------------------------------

class WhoopRecoveryCreate(BaseModel):
    operator_id: uuid.UUID
    provider_cycle_id: int
    provider_sleep_id: uuid.UUID
    whoop_user_id: int | None = None
    recorded_at: datetime.datetime
    updated_at_source: datetime.datetime | None = None
    score_state: str
    recovery_score: int | None = None
    resting_heart_rate: int | None = None
    hrv_rmssd_milli: Decimal | None = None
    spo2_percentage: Decimal | None = None
    skin_temp_celsius: Decimal | None = None
    user_calibrating: bool | None = None
    source_payload: dict | None = None


class WhoopRecoveryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    operator_id: uuid.UUID
    provider_cycle_id: int
    provider_sleep_id: uuid.UUID
    whoop_user_id: int | None
    recorded_at: datetime.datetime
    updated_at_source: datetime.datetime | None
    score_state: str
    recovery_score: int | None
    resting_heart_rate: int | None
    hrv_rmssd_milli: Decimal | None
    spo2_percentage: Decimal | None
    skin_temp_celsius: Decimal | None
    user_calibrating: bool | None
    source_payload: dict | None
    created_at: datetime.datetime


# ---------------------------------------------------------------------------
# WHOOP Workouts
# ---------------------------------------------------------------------------

class WhoopWorkoutCreate(BaseModel):
    operator_id: uuid.UUID
    provider_workout_id: uuid.UUID
    workout_type: str | None = None
    workout_start: datetime.datetime | None = None
    workout_end: datetime.datetime | None = None
    strain: Decimal | None = None
    average_heart_rate: int | None = None
    max_heart_rate: int | None = None
    source_payload: dict | None = None


class WhoopWorkoutRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    operator_id: uuid.UUID
    provider_workout_id: uuid.UUID
    workout_type: str | None
    workout_start: datetime.datetime | None
    workout_end: datetime.datetime | None
    strain: Decimal | None
    average_heart_rate: int | None
    max_heart_rate: int | None
    source_payload: dict | None
    created_at: datetime.datetime
    updated_at: datetime.datetime


# ---------------------------------------------------------------------------
# Physiology Features
# ---------------------------------------------------------------------------

class PhysiologyFeatureCreate(BaseModel):
    operator_id: uuid.UUID
    feature_date: datetime.date
    feature_name: str
    feature_value: Decimal | None = None
    feature_json: dict | None = None
    confidence: Decimal | None = None
    computed_at: datetime.datetime | None = None


class PhysiologyFeatureRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    operator_id: uuid.UUID
    feature_date: datetime.date
    feature_name: str
    feature_value: Decimal | None
    feature_json: dict | None
    confidence: Decimal | None
    computed_at: datetime.datetime | None


# ---------------------------------------------------------------------------
# Biomarker Panels
# ---------------------------------------------------------------------------

class BiomarkerPanelCreate(BaseModel):
    operator_id: uuid.UUID
    panel_date: datetime.date
    provider: str
    panel_type: str
    summary: dict
    source_payload: dict | None = None


class BiomarkerPanelRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    operator_id: uuid.UUID
    panel_date: datetime.date
    provider: str
    panel_type: str
    summary: dict
    source_payload: dict | None
    created_at: datetime.datetime
