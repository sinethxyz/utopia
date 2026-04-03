"""Execution ORM models — the action layer that closes Loop A.

This schema records the evidence -> inference -> policy -> outcome chain:
- StateEstimate: what operating condition is the operator in?
- BlockerEstimate: why is motion failing?
- ReentryArtifact: how to re-enter a thread without paying a massive context tax
- PolicyDecision: the Schrödinger output — one correct move
- Trace: compressed post-action record

Matches: Utopia Formal Architecture DB etc.md section 11.
"""

import datetime
import decimal
import uuid

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from utopia.db import Base
from utopia.enums import (
    ActionDepth,
    BlockerKind,
    InterventionKind,
    StateKind,
    TraceKind,
)


class StateEstimate(Base):
    """What operating condition is the operator most likely in right now?

    Produced by the State Estimator (AI Fabric), or manually.
    Combines subjective, behavioral, contextual, and physiological evidence.

    Output: primary state, confidence, contributing factors.
    This constrains downstream policy selection.
    """

    __tablename__ = "state_estimates"
    __table_args__ = {"schema": "execution"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("core.operators.id"), nullable=False
    )
    thread_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("vector_ctrl.threads.id"), nullable=True
    )
    state_kind: Mapped[StateKind] = mapped_column(
        Enum(StateKind, name="state_kind", schema="core", create_type=False),
        nullable=False,
    )
    confidence: Mapped[decimal.Decimal] = mapped_column(
        Numeric(5, 4), nullable=False
    )
    contributing_factors: Mapped[list] = mapped_column(
        JSONB, nullable=False, server_default="[]"
    )
    generated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )


class BlockerEstimate(Base):
    """Why is motion failing?

    Each blocker kind implies a different intervention:
    ambiguity -> shrink problem, depletion -> reduce depth,
    context fracture -> generate re-entry artifact, etc.

    Without blocker typing the system recommends the wrong thing.
    """

    __tablename__ = "blocker_estimates"
    __table_args__ = {"schema": "execution"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("core.operators.id"), nullable=False
    )
    thread_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("vector_ctrl.threads.id"), nullable=True
    )
    blocker_kind: Mapped[BlockerKind] = mapped_column(
        Enum(BlockerKind, name="blocker_kind", schema="core", create_type=False),
        nullable=False,
    )
    confidence: Mapped[decimal.Decimal] = mapped_column(
        Numeric(5, 4), nullable=False
    )
    supporting_evidence: Mapped[list] = mapped_column(
        JSONB, nullable=False, server_default="[]"
    )
    generated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )


class ReentryArtifact(Base):
    """A bridge object for future reactivation of a thread.

    One of the most valuable objects in the system. Its purpose is
    to reduce the tax of interruption. Contains: last completed step,
    unresolved edge, smallest next move, trap to avoid.

    superseded_by links to the replacement artifact when a thread
    is re-entered and a new artifact is generated.
    """

    __tablename__ = "reentry_artifacts"
    __table_args__ = {"schema": "execution"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("core.operators.id"), nullable=False
    )
    thread_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("vector_ctrl.threads.id"), nullable=False
    )
    last_completed_step: Mapped[str | None] = mapped_column(Text, nullable=True)
    unresolved_edge: Mapped[str | None] = mapped_column(Text, nullable=True)
    next_smallest_move: Mapped[str | None] = mapped_column(Text, nullable=True)
    trap_to_avoid: Mapped[str | None] = mapped_column(Text, nullable=True)
    relevant_context: Mapped[dict] = mapped_column(
        JSONB, nullable=False, server_default="{}"
    )
    freshness_score: Mapped[decimal.Decimal | None] = mapped_column(
        Numeric(6, 3), nullable=True
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    superseded_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("execution.reentry_artifacts.id"), nullable=True
    )


class PolicyDecision(Base):
    """The Schrödinger output — one correct move for the operator's real condition.

    Links back to the state estimate and blocker estimate that produced it,
    preserving the evidence -> inference -> policy chain.

    problem_id is nullable and has no FK constraint yet — the reasoning
    schema does not exist. When it does, a migration will add the FK.

    mode + intervention_kind + action_depth + next_move together define
    what Schrödinger recommends. The move may be: recover, preserve,
    orient, re-enter, clarify, ask one question, execute, close loop, review.
    """

    __tablename__ = "policy_decisions"
    __table_args__ = {"schema": "execution"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("core.operators.id"), nullable=False
    )
    thread_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("vector_ctrl.threads.id"), nullable=True
    )
    problem_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    state_estimate_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("execution.state_estimates.id"), nullable=True
    )
    blocker_estimate_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("execution.blocker_estimates.id"), nullable=True
    )
    mode: Mapped[InterventionKind] = mapped_column(
        Enum(InterventionKind, name="intervention_kind", schema="core", create_type=False),
        nullable=False,
    )
    intervention_kind: Mapped[InterventionKind] = mapped_column(
        Enum(InterventionKind, name="intervention_kind", schema="core", create_type=False),
        nullable=False,
    )
    action_depth: Mapped[ActionDepth] = mapped_column(
        Enum(ActionDepth, name="action_depth", schema="core", create_type=False),
        nullable=False,
    )
    next_move: Mapped[str] = mapped_column(Text, nullable=False)
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[decimal.Decimal | None] = mapped_column(
        Numeric(5, 4), nullable=True
    )
    caution_flags: Mapped[list] = mapped_column(
        JSONB, nullable=False, server_default="[]"
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    state_estimate: Mapped[StateEstimate | None] = relationship(
        foreign_keys=[state_estimate_id]
    )
    blocker_estimate: Mapped[BlockerEstimate | None] = relationship(
        foreign_keys=[blocker_estimate_id]
    )


class Trace(Base):
    """Compressed post-action record.

    Not a diary. Training data for Aether and the Personal Execution Model.
    Records what happened after the move: action taken, outcome, truth
    revealed, next edge, and confidence delta via subjective_after.

    Links back to the policy decision that produced the move,
    completing the evidence -> inference -> policy -> outcome chain.
    """

    __tablename__ = "traces"
    __table_args__ = {"schema": "execution"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("core.operators.id"), nullable=False
    )
    thread_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("vector_ctrl.threads.id"), nullable=True
    )
    policy_decision_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("execution.policy_decisions.id"), nullable=True
    )
    trace_kind: Mapped[TraceKind] = mapped_column(
        Enum(TraceKind, name="trace_kind", schema="core", create_type=False),
        nullable=False,
    )
    action_taken: Mapped[str | None] = mapped_column(Text, nullable=True)
    outcome: Mapped[str | None] = mapped_column(Text, nullable=True)
    truth_revealed: Mapped[str | None] = mapped_column(Text, nullable=True)
    next_edge: Mapped[str | None] = mapped_column(Text, nullable=True)
    completion_score: Mapped[decimal.Decimal | None] = mapped_column(
        Numeric(6, 3), nullable=True
    )
    subjective_after: Mapped[dict] = mapped_column(
        JSONB, nullable=False, server_default="{}"
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    policy_decision: Mapped[PolicyDecision | None] = relationship(
        foreign_keys=[policy_decision_id]
    )
