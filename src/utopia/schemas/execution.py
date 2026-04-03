"""Pydantic schemas for the Execution layer.

Request and response schemas for the evidence -> inference -> policy -> outcome chain:
state estimates, blocker estimates, re-entry artifacts, policy decisions, traces.
"""

import datetime
import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from utopia.enums import (
    ActionDepth,
    BlockerKind,
    InterventionKind,
    StateKind,
    TraceKind,
)


# ---------------------------------------------------------------------------
# State Estimates
# ---------------------------------------------------------------------------

class StateEstimateCreate(BaseModel):
    """Record what operating condition the operator is in.

    Can be produced by the State Estimator (AI Fabric) or manually.
    contributing_factors should list the evidence that led to this estimate,
    e.g. [{"source": "checkin", "signal": "energy", "value": 25},
          {"source": "whoop", "signal": "recovery", "value": 38}]
    """

    operator_id: uuid.UUID
    thread_id: uuid.UUID | None = None
    state_kind: StateKind
    confidence: Decimal = Field(ge=0, le=1)
    contributing_factors: list = Field(default_factory=list)


class StateEstimateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    operator_id: uuid.UUID
    thread_id: uuid.UUID | None
    state_kind: StateKind
    confidence: Decimal
    contributing_factors: list
    generated_at: datetime.datetime


# ---------------------------------------------------------------------------
# Blocker Estimates
# ---------------------------------------------------------------------------

class BlockerEstimateCreate(BaseModel):
    """Record why motion is failing.

    Every blocker kind implies a different intervention:
    ambiguity -> shrink problem / define next edge
    depletion -> reduce depth / preserve continuity
    context fracture -> generate re-entry artifact
    vector conflict -> escalate to Vector Arbiter

    supporting_evidence should list the evidence that supports
    this blocker hypothesis.
    """

    operator_id: uuid.UUID
    thread_id: uuid.UUID | None = None
    blocker_kind: BlockerKind
    confidence: Decimal = Field(ge=0, le=1)
    supporting_evidence: list = Field(default_factory=list)


class BlockerEstimateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    operator_id: uuid.UUID
    thread_id: uuid.UUID | None
    blocker_kind: BlockerKind
    confidence: Decimal
    supporting_evidence: list
    generated_at: datetime.datetime


# ---------------------------------------------------------------------------
# Re-entry Artifacts
# ---------------------------------------------------------------------------

class ReentryArtifactCreate(BaseModel):
    """Create a re-entry artifact — a bridge for future thread reactivation.

    This is one of the most valuable objects in the system.
    It contains everything needed to resume a thread without paying
    a massive context reconstruction tax.
    """

    operator_id: uuid.UUID
    thread_id: uuid.UUID
    last_completed_step: str | None = None
    unresolved_edge: str | None = None
    next_smallest_move: str | None = None
    trap_to_avoid: str | None = None
    relevant_context: dict = Field(default_factory=dict)
    freshness_score: Decimal | None = None


class ReentryArtifactRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    operator_id: uuid.UUID
    thread_id: uuid.UUID
    last_completed_step: str | None
    unresolved_edge: str | None
    next_smallest_move: str | None
    trap_to_avoid: str | None
    relevant_context: dict
    freshness_score: Decimal | None
    created_at: datetime.datetime
    superseded_by: uuid.UUID | None


# ---------------------------------------------------------------------------
# Policy Decisions
# ---------------------------------------------------------------------------

class PolicyDecisionCreate(BaseModel):
    """Record a Schrödinger output — the smallest correct move.

    This is the core output of Loop A. It links back to the state
    and blocker estimates that produced it, preserving the full
    evidence -> inference -> policy chain.

    The move may be: recover, preserve, orient, re-enter, clarify,
    ask one question, execute, close loop, review.
    """

    operator_id: uuid.UUID
    thread_id: uuid.UUID | None = None
    problem_id: uuid.UUID | None = None
    state_estimate_id: uuid.UUID | None = None
    blocker_estimate_id: uuid.UUID | None = None
    mode: InterventionKind
    intervention_kind: InterventionKind
    action_depth: ActionDepth
    next_move: str
    rationale: str | None = None
    confidence: Decimal | None = Field(None, ge=0, le=1)
    caution_flags: list = Field(default_factory=list)


class PolicyDecisionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    operator_id: uuid.UUID
    thread_id: uuid.UUID | None
    problem_id: uuid.UUID | None
    state_estimate_id: uuid.UUID | None
    blocker_estimate_id: uuid.UUID | None
    mode: InterventionKind
    intervention_kind: InterventionKind
    action_depth: ActionDepth
    next_move: str
    rationale: str | None
    confidence: Decimal | None
    caution_flags: list
    created_at: datetime.datetime


# ---------------------------------------------------------------------------
# Traces
# ---------------------------------------------------------------------------

class TraceCreate(BaseModel):
    """Record a compressed post-action trace.

    Not a diary. Training data for Aether and the Personal Execution Model.
    Records what happened after the move was taken.

    truth_revealed: what was learned that was not known before.
    next_edge: what the next resumption point is.
    subjective_after: operator's state after the action, for calibration.
    """

    operator_id: uuid.UUID
    thread_id: uuid.UUID | None = None
    policy_decision_id: uuid.UUID | None = None
    trace_kind: TraceKind
    action_taken: str | None = None
    outcome: str | None = None
    truth_revealed: str | None = None
    next_edge: str | None = None
    completion_score: Decimal | None = None
    subjective_after: dict = Field(default_factory=dict)


class TraceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    operator_id: uuid.UUID
    thread_id: uuid.UUID | None
    policy_decision_id: uuid.UUID | None
    trace_kind: TraceKind
    action_taken: str | None
    outcome: str | None
    truth_revealed: str | None
    next_edge: str | None
    completion_score: Decimal | None
    subjective_after: dict
    created_at: datetime.datetime
