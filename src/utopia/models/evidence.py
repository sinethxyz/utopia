"""Evidence ORM models — the live sensing layer.

Evidence captures what is true about the operator's present moment:
- Subjective signals (self-reported energy, clarity, resistance, etc.)
- Behavioral signals (observed actions, failed starts, switching, etc.)
- Contextual signals (environment, time, interruptions, obligations)
- Derived features (computed from raw evidence for downstream policy)

Matches: Utopia Formal Architecture DB etc.md section 7.
"""

import datetime
import decimal
import uuid

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Integer, Numeric, SmallInteger, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from utopia.db import Base


class SubjectiveCheckin(Base):
    """Fast self-report of the operator's internal state.

    All signal fields are 0-100 scales. Any can be null — a partial
    checkin is still evidence. The free_text field captures anything
    the operator wants to note without forcing structure.

    These are consumed by the State Estimator and Blocker Classifier.
    """

    __tablename__ = "subjective_checkins"
    __table_args__ = (
        CheckConstraint("energy IS NULL OR (energy BETWEEN 0 AND 100)", name="ck_checkin_energy"),
        CheckConstraint("clarity IS NULL OR (clarity BETWEEN 0 AND 100)", name="ck_checkin_clarity"),
        CheckConstraint("resistance IS NULL OR (resistance BETWEEN 0 AND 100)", name="ck_checkin_resistance"),
        CheckConstraint("overwhelm IS NULL OR (overwhelm BETWEEN 0 AND 100)", name="ck_checkin_overwhelm"),
        CheckConstraint("emotional_load IS NULL OR (emotional_load BETWEEN 0 AND 100)", name="ck_checkin_emotional_load"),
        CheckConstraint("perceived_urgency IS NULL OR (perceived_urgency BETWEEN 0 AND 100)", name="ck_checkin_perceived_urgency"),
        {"schema": "evidence"},
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("core.operators.id"), nullable=False
    )
    thread_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("vector_ctrl.threads.id"), nullable=True
    )
    energy: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    clarity: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    resistance: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    overwhelm: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    emotional_load: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    perceived_urgency: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    free_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    recorded_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )


class BehaviorEvent(Base):
    """An observed behavioral signal.

    event_type examples: thread_opened, action_started, action_abandoned,
    action_completed, thread_switched, failed_start, open_without_action.

    These are append-only. The Blocker Classifier uses patterns in
    behavior events to distinguish ambiguity from depletion, completion
    aversion from context fracture, etc.
    """

    __tablename__ = "behavior_events"
    __table_args__ = {"schema": "evidence"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("core.operators.id"), nullable=False
    )
    thread_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("vector_ctrl.threads.id"), nullable=True
    )
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    event_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    duration_ms: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    metadata_: Mapped[dict] = mapped_column(
        "metadata", JSONB, nullable=False, server_default="{}"
    )


class ContextSnapshot(Base):
    """Structural facts about the operator's environment at a moment.

    Captures time, environment label, interruption count, obligation
    load, available minutes, and active window (morning/afternoon/evening).

    The State Estimator uses these to weight feasibility of action depth.
    """

    __tablename__ = "context_snapshots"
    __table_args__ = {"schema": "evidence"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("core.operators.id"), nullable=False
    )
    thread_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("vector_ctrl.threads.id"), nullable=True
    )
    local_time: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    environment_label: Mapped[str | None] = mapped_column(Text, nullable=True)
    interruption_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    obligation_load: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    available_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    active_window: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_: Mapped[dict] = mapped_column(
        "metadata", JSONB, nullable=False, server_default="{}"
    )


class DerivedFeature(Base):
    """A computed feature derived from raw evidence.

    Examples: failed_start_rate_24h, thread_decay_hours,
    drift_probability, completion_aversion_score, ambiguity_candidate_score.

    feature_window indicates the time scope: last_2h, last_24h, last_7d.
    confidence indicates how reliable the computation is.

    These are consumed by the State Estimator, Blocker Classifier,
    and Schrodinger policy engine.
    """

    __tablename__ = "derived_features"
    __table_args__ = {"schema": "evidence"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("core.operators.id"), nullable=False
    )
    thread_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("vector_ctrl.threads.id"), nullable=True
    )
    feature_name: Mapped[str] = mapped_column(Text, nullable=False)
    feature_value: Mapped[decimal.Decimal | None] = mapped_column(Numeric, nullable=True)
    feature_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    feature_window: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[decimal.Decimal | None] = mapped_column(
        Numeric(5, 4), nullable=True
    )
    observed_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
