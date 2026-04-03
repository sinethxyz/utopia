"""Pydantic schemas for the Vector control plane.

Request schemas (Create/Update) and response schemas (Read) for
life arcs, seasons, missions, and threads.

These are API-boundary objects — they do not leak ORM internals.
"""

import datetime
import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from utopia.enums import (
    ConstraintHardness,
    MissionKind,
    SeasonStatus,
    Status,
    ThreadKind,
    ThreadStatus,
)


# ---------------------------------------------------------------------------
# Life Arcs
# ---------------------------------------------------------------------------

class LifeArcCreate(BaseModel):
    """Create a new life arc — the longest-horizon directional object."""

    operator_id: uuid.UUID
    title: str
    description: str | None = None
    status: Status = Status.active
    horizon_start: datetime.date | None = None
    horizon_end: datetime.date | None = None
    success_definition: str | None = None
    anti_goals: list[str] = Field(default_factory=list)


class LifeArcRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    operator_id: uuid.UUID
    title: str
    description: str | None
    status: Status
    horizon_start: datetime.date | None
    horizon_end: datetime.date | None
    success_definition: str | None
    anti_goals: list[str]
    created_at: datetime.datetime
    updated_at: datetime.datetime


# ---------------------------------------------------------------------------
# Seasons
# ---------------------------------------------------------------------------

class SeasonCreate(BaseModel):
    """Create a season — a bounded phase of strategic focus."""

    operator_id: uuid.UUID
    life_arc_id: uuid.UUID | None = None
    title: str
    thesis: str | None = None
    start_date: datetime.date
    end_date: datetime.date | None = None
    priority_stack: list = Field(default_factory=list)
    status: SeasonStatus = SeasonStatus.planned


class SeasonRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    operator_id: uuid.UUID
    life_arc_id: uuid.UUID | None
    title: str
    thesis: str | None
    start_date: datetime.date
    end_date: datetime.date | None
    priority_stack: list
    status: SeasonStatus
    created_at: datetime.datetime
    updated_at: datetime.datetime


# ---------------------------------------------------------------------------
# Missions
# ---------------------------------------------------------------------------

class MissionCreate(BaseModel):
    """Create a mission — a strategically meaningful objective.

    Missions are not tasks. They carry explicit definitions of
    success, failure, and drift. These definitions are what let
    the Vector Arbiter detect misalignment downstream.
    """

    operator_id: uuid.UUID
    season_id: uuid.UUID | None = None
    title: str
    description: str | None = None
    mission_kind: MissionKind
    priority_score: Decimal | None = None
    status: Status = Status.active
    success_definition: str | None = None
    failure_definition: str | None = None
    drift_definition: str | None = None


class MissionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    operator_id: uuid.UUID
    season_id: uuid.UUID | None
    title: str
    description: str | None
    mission_kind: MissionKind
    priority_score: Decimal | None
    status: Status
    success_definition: str | None
    failure_definition: str | None
    drift_definition: str | None
    created_at: datetime.datetime
    updated_at: datetime.datetime


# ---------------------------------------------------------------------------
# Threads
# ---------------------------------------------------------------------------

class ThreadCreate(BaseModel):
    """Create a thread — a live line of work within a mission.

    Threads carry operational metadata for the execution layer:
    complexity, ambiguity, and re-entry risk scores. They also
    hold next_edge_summary — the smallest resumption hint.
    """

    operator_id: uuid.UUID
    mission_id: uuid.UUID
    parent_thread_id: uuid.UUID | None = None
    title: str
    description: str | None = None
    thread_kind: ThreadKind
    status: ThreadStatus = ThreadStatus.active
    complexity_score: Decimal | None = None
    ambiguity_score: Decimal | None = None
    reentry_risk_score: Decimal | None = None
    next_edge_summary: str | None = None


class ThreadRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    operator_id: uuid.UUID
    mission_id: uuid.UUID
    parent_thread_id: uuid.UUID | None
    title: str
    description: str | None
    thread_kind: ThreadKind
    status: ThreadStatus
    complexity_score: Decimal | None
    ambiguity_score: Decimal | None
    reentry_risk_score: Decimal | None
    last_meaningful_touch_at: datetime.datetime | None
    next_edge_summary: str | None
    created_at: datetime.datetime
    updated_at: datetime.datetime


# ---------------------------------------------------------------------------
# Thread Constraints
# ---------------------------------------------------------------------------

class ThreadConstraintCreate(BaseModel):
    thread_id: uuid.UUID
    constraint_type: str
    description: str
    hardness: ConstraintHardness


class ThreadConstraintRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    thread_id: uuid.UUID
    constraint_type: str
    description: str
    hardness: ConstraintHardness
    created_at: datetime.datetime


# ---------------------------------------------------------------------------
# Anti-Goals
# ---------------------------------------------------------------------------

class AntiGoalCreate(BaseModel):
    """Create an anti-goal scoped to any level of the directional hierarchy."""

    operator_id: uuid.UUID
    scope_type: str = Field(
        description="Which directional level: life_arc, season, mission, or thread"
    )
    scope_id: uuid.UUID
    description: str


class AntiGoalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    operator_id: uuid.UUID
    scope_type: str
    scope_id: uuid.UUID
    description: str
    created_at: datetime.datetime
