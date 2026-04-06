"""Review & Calibration ORM models — the system's immune layer.

Closures capture thread/mission endings. Review sessions examine traces
and patterns. Rule promotions push insights to Aether. Pattern updates
refine the system's behavioral models. Calibration records measure
estimate accuracy and drift.

Matches: Utopia Formal Architecture DB etc.md Review & Calibration section.
"""

import datetime
import decimal
import uuid

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from utopia.db import Base
from utopia.enums import ClosureType, ReviewScope


class Closure(Base):
    """End-of-life record for a thread or mission.

    When a thread or mission ends — completed, archived, paused, or
    merged — a closure captures what happened, what was learned, and
    whether it succeeded. Links back to the final trace and the
    originating thread/mission.
    """

    __tablename__ = "closures"
    __table_args__ = {"schema": "review"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("core.operators.id"), nullable=False
    )
    thread_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("vector_ctrl.threads.id"), nullable=True
    )
    mission_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("vector_ctrl.missions.id"), nullable=True
    )
    closure_type: Mapped[ClosureType] = mapped_column(
        Enum(ClosureType, name="closure_type", schema="core", create_type=False),
        nullable=False,
    )
    outcome_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    lessons_learned: Mapped[list] = mapped_column(
        JSONB, nullable=False, server_default="[]"
    )
    truth_revealed: Mapped[str | None] = mapped_column(Text, nullable=True)
    final_trace_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("execution.traces.id"), nullable=True
    )
    success_score: Mapped[decimal.Decimal | None] = mapped_column(
        Numeric(6, 3), nullable=True
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    final_trace: Mapped["Trace | None"] = relationship(  # noqa: F821
        foreign_keys=[final_trace_id]
    )


class ReviewSession(Base):
    """A periodic review event.

    The operator (or system) examines recent traces, patterns, and
    outcomes over a time window. Produces insights, identifies patterns,
    and may trigger rule promotions or pattern updates.
    """

    __tablename__ = "review_sessions"
    __table_args__ = {"schema": "review"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("core.operators.id"), nullable=False
    )
    review_scope: Mapped[ReviewScope] = mapped_column(
        Enum(ReviewScope, name="review_scope", schema="core", create_type=False),
        nullable=False,
    )
    window_start: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    window_end: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    insights: Mapped[list] = mapped_column(
        JSONB, nullable=False, server_default="[]"
    )
    trace_ids_reviewed: Mapped[list] = mapped_column(
        JSONB, nullable=False, server_default="[]"
    )
    patterns_identified: Mapped[list] = mapped_column(
        JSONB, nullable=False, server_default="[]"
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )


class RulePromotion(Base):
    """Links a review session to a promoted Rule in Aether.

    When a pattern or insight is strong enough to become a behavioral
    rule, a rule promotion records the evidence that justified the
    promotion and links to both the review session and the Aether rule.
    """

    __tablename__ = "rule_promotions"
    __table_args__ = {"schema": "review"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("core.operators.id"), nullable=False
    )
    review_session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("review.review_sessions.id"), nullable=False
    )
    rule_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("aether.rules.id"), nullable=False
    )
    evidence_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    supporting_trace_ids: Mapped[list] = mapped_column(
        JSONB, nullable=False, server_default="[]"
    )
    confidence: Mapped[decimal.Decimal | None] = mapped_column(
        Numeric(5, 4), nullable=True
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    review_session: Mapped[ReviewSession] = relationship(
        foreign_keys=[review_session_id]
    )


class PatternUpdate(Base):
    """Updates or creates patterns from reviewed evidence.

    During a review session, existing patterns may be strengthened,
    weakened, or invalidated, and new patterns may be created. Each
    update links back to the review session and the Aether pattern.
    """

    __tablename__ = "pattern_updates"
    __table_args__ = {"schema": "review"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("core.operators.id"), nullable=False
    )
    review_session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("review.review_sessions.id"), nullable=False
    )
    pattern_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("aether.patterns.id"), nullable=False
    )
    update_kind: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    supporting_trace_ids: Mapped[list] = mapped_column(
        JSONB, nullable=False, server_default="[]"
    )
    confidence_before: Mapped[decimal.Decimal | None] = mapped_column(
        Numeric(5, 4), nullable=True
    )
    confidence_after: Mapped[decimal.Decimal | None] = mapped_column(
        Numeric(5, 4), nullable=True
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    review_session: Mapped[ReviewSession] = relationship(
        foreign_keys=[review_session_id]
    )


class CalibrationRecord(Base):
    """Compares a past system estimate with what actually happened.

    estimate_kind + estimate_id form a polymorphic reference to the
    original estimate (state_estimate, blocker_estimate, or
    policy_decision). The trace records what actually occurred.
    accuracy_score and drift_direction measure calibration quality.
    """

    __tablename__ = "calibration_records"
    __table_args__ = {"schema": "review"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("core.operators.id"), nullable=False
    )
    review_session_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("review.review_sessions.id"), nullable=True
    )
    estimate_kind: Mapped[str] = mapped_column(Text, nullable=False)
    estimate_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    trace_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("execution.traces.id"), nullable=True
    )
    predicted_value: Mapped[dict] = mapped_column(
        JSONB, nullable=False, server_default="{}"
    )
    actual_value: Mapped[dict] = mapped_column(
        JSONB, nullable=False, server_default="{}"
    )
    accuracy_score: Mapped[decimal.Decimal | None] = mapped_column(
        Numeric(5, 4), nullable=True
    )
    drift_direction: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    review_session: Mapped[ReviewSession | None] = relationship(
        foreign_keys=[review_session_id]
    )
