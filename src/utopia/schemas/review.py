"""Pydantic schemas for the Review & Calibration layer.

Request schemas (Create) and response schemas (Read) for all 5 review
entity types: closures, review sessions, rule promotions, pattern
updates, and calibration records.
"""

import datetime
import uuid
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from utopia.enums import ClosureType, ReviewScope


# ---------------------------------------------------------------------------
# Closures
# ---------------------------------------------------------------------------

class ClosureCreate(BaseModel):
    operator_id: uuid.UUID
    thread_id: uuid.UUID | None = None
    mission_id: uuid.UUID | None = None
    closure_type: ClosureType
    outcome_summary: str | None = None
    lessons_learned: list[Any] = Field(default_factory=list)
    truth_revealed: str | None = None
    final_trace_id: uuid.UUID | None = None
    success_score: Decimal | None = None


class ClosureRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    operator_id: uuid.UUID
    thread_id: uuid.UUID | None
    mission_id: uuid.UUID | None
    closure_type: ClosureType
    outcome_summary: str | None
    lessons_learned: list[Any]
    truth_revealed: str | None
    final_trace_id: uuid.UUID | None
    success_score: Decimal | None
    created_at: datetime.datetime


# ---------------------------------------------------------------------------
# Review Sessions
# ---------------------------------------------------------------------------

class ReviewSessionCreate(BaseModel):
    operator_id: uuid.UUID
    review_scope: ReviewScope
    window_start: datetime.datetime
    window_end: datetime.datetime
    summary: str | None = None
    insights: list[Any] = Field(default_factory=list)
    trace_ids_reviewed: list[Any] = Field(default_factory=list)
    patterns_identified: list[Any] = Field(default_factory=list)


class ReviewSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    operator_id: uuid.UUID
    review_scope: ReviewScope
    window_start: datetime.datetime
    window_end: datetime.datetime
    summary: str | None
    insights: list[Any]
    trace_ids_reviewed: list[Any]
    patterns_identified: list[Any]
    created_at: datetime.datetime


# ---------------------------------------------------------------------------
# Rule Promotions
# ---------------------------------------------------------------------------

class RulePromotionCreate(BaseModel):
    operator_id: uuid.UUID
    review_session_id: uuid.UUID
    rule_id: uuid.UUID
    evidence_summary: str | None = None
    supporting_trace_ids: list[Any] = Field(default_factory=list)
    confidence: Decimal | None = None


class RulePromotionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    operator_id: uuid.UUID
    review_session_id: uuid.UUID
    rule_id: uuid.UUID
    evidence_summary: str | None
    supporting_trace_ids: list[Any]
    confidence: Decimal | None
    created_at: datetime.datetime


# ---------------------------------------------------------------------------
# Pattern Updates
# ---------------------------------------------------------------------------

class PatternUpdateCreate(BaseModel):
    operator_id: uuid.UUID
    review_session_id: uuid.UUID
    pattern_id: uuid.UUID
    update_kind: str
    evidence_summary: str | None = None
    supporting_trace_ids: list[Any] = Field(default_factory=list)
    confidence_before: Decimal | None = None
    confidence_after: Decimal | None = None


class PatternUpdateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    operator_id: uuid.UUID
    review_session_id: uuid.UUID
    pattern_id: uuid.UUID
    update_kind: str
    evidence_summary: str | None
    supporting_trace_ids: list[Any]
    confidence_before: Decimal | None
    confidence_after: Decimal | None
    created_at: datetime.datetime


# ---------------------------------------------------------------------------
# Calibration Records
# ---------------------------------------------------------------------------

class CalibrationRecordCreate(BaseModel):
    operator_id: uuid.UUID
    review_session_id: uuid.UUID | None = None
    estimate_kind: str
    estimate_id: uuid.UUID
    trace_id: uuid.UUID | None = None
    predicted_value: dict[str, Any] = Field(default_factory=dict)
    actual_value: dict[str, Any] = Field(default_factory=dict)
    accuracy_score: Decimal | None = None
    drift_direction: str | None = None
    notes: str | None = None


class CalibrationRecordRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    operator_id: uuid.UUID
    review_session_id: uuid.UUID | None
    estimate_kind: str
    estimate_id: uuid.UUID
    trace_id: uuid.UUID | None
    predicted_value: dict[str, Any]
    actual_value: dict[str, Any]
    accuracy_score: Decimal | None
    drift_direction: str | None
    notes: str | None
    created_at: datetime.datetime
