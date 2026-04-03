"""Pydantic schemas for the Evidence sensing layer.

Request schemas (Create) and response schemas (Read) for
subjective checkins, behavior events, context snapshots,
and derived features.
"""

import datetime
import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Subjective Checkins
# ---------------------------------------------------------------------------

class SubjectiveCheckinCreate(BaseModel):
    """Record a subjective self-report.

    All signal fields are optional 0-100 scales. A partial checkin
    is valid — even a single signal is evidence.
    """

    operator_id: uuid.UUID
    thread_id: uuid.UUID | None = None
    energy: int | None = Field(None, ge=0, le=100)
    clarity: int | None = Field(None, ge=0, le=100)
    resistance: int | None = Field(None, ge=0, le=100)
    overwhelm: int | None = Field(None, ge=0, le=100)
    emotional_load: int | None = Field(None, ge=0, le=100)
    perceived_urgency: int | None = Field(None, ge=0, le=100)
    free_text: str | None = None
    recorded_at: datetime.datetime


class SubjectiveCheckinRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    operator_id: uuid.UUID
    thread_id: uuid.UUID | None
    energy: int | None
    clarity: int | None
    resistance: int | None
    overwhelm: int | None
    emotional_load: int | None
    perceived_urgency: int | None
    free_text: str | None
    recorded_at: datetime.datetime
    created_at: datetime.datetime


# ---------------------------------------------------------------------------
# Behavior Events
# ---------------------------------------------------------------------------

class BehaviorEventCreate(BaseModel):
    """Record an observed behavioral signal.

    event_type examples: thread_opened, action_started, action_abandoned,
    action_completed, thread_switched, failed_start, open_without_action.
    """

    operator_id: uuid.UUID
    thread_id: uuid.UUID | None = None
    event_type: str
    event_at: datetime.datetime
    duration_ms: int | None = None
    metadata: dict = Field(default_factory=dict)


class BehaviorEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    operator_id: uuid.UUID
    thread_id: uuid.UUID | None
    event_type: str
    event_at: datetime.datetime
    duration_ms: int | None
    metadata: dict = Field(validation_alias="metadata_")


# ---------------------------------------------------------------------------
# Context Snapshots
# ---------------------------------------------------------------------------

class ContextSnapshotCreate(BaseModel):
    """Capture structural facts about the operator's environment."""

    operator_id: uuid.UUID
    thread_id: uuid.UUID | None = None
    local_time: datetime.datetime
    environment_label: str | None = None
    interruption_count: int | None = None
    obligation_load: int | None = None
    available_minutes: int | None = None
    active_window: str | None = Field(
        None, description="morning, afternoon, or evening"
    )
    metadata: dict = Field(default_factory=dict)


class ContextSnapshotRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    operator_id: uuid.UUID
    thread_id: uuid.UUID | None
    local_time: datetime.datetime
    environment_label: str | None
    interruption_count: int | None
    obligation_load: int | None
    available_minutes: int | None
    active_window: str | None
    metadata: dict = Field(validation_alias="metadata_")


# ---------------------------------------------------------------------------
# Derived Features
# ---------------------------------------------------------------------------

class DerivedFeatureCreate(BaseModel):
    """Store a computed feature derived from raw evidence.

    feature_window: last_2h, last_24h, last_7d, etc.
    confidence: how reliable the computation is (0-1).
    """

    operator_id: uuid.UUID
    thread_id: uuid.UUID | None = None
    feature_name: str
    feature_value: Decimal | None = None
    feature_json: dict | None = None
    feature_window: str | None = None
    confidence: Decimal | None = Field(None, ge=0, le=1)
    observed_at: datetime.datetime


class DerivedFeatureRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    operator_id: uuid.UUID
    thread_id: uuid.UUID | None
    feature_name: str
    feature_value: Decimal | None
    feature_json: dict | None
    feature_window: str | None
    confidence: Decimal | None
    observed_at: datetime.datetime
    created_at: datetime.datetime
