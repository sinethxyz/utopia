"""vector_ctrl ORM models — the directional control plane.

Vector is not task storage. It preserves direction:
life arc > season > mission > thread hierarchy,
plus thread constraints and anti-goals.

Matches: Utopia Formal Architecture DB etc.md section 6.
"""

import datetime
import decimal
import uuid

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Numeric, Text, text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from utopia.db import Base
from utopia.enums import (
    ConstraintHardness,
    MissionKind,
    SeasonStatus,
    Status,
    ThreadKind,
    ThreadStatus,
)


class LifeArc(Base):
    """Top-level directional framing.

    A life arc is the longest-horizon directional object.
    It answers: what trajectory is the operator on, and what defines
    success or failure at that scale?
    """

    __tablename__ = "life_arcs"
    __table_args__ = {"schema": "vector_ctrl"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("core.operators.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[Status] = mapped_column(
        Enum(Status, name="status", schema="core", create_type=False),
        nullable=False,
    )
    horizon_start: Mapped[datetime.date | None] = mapped_column(Date, nullable=True)
    horizon_end: Mapped[datetime.date | None] = mapped_column(Date, nullable=True)
    success_definition: Mapped[str | None] = mapped_column(Text, nullable=True)
    anti_goals: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, server_default="{}"
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    seasons: Mapped[list["Season"]] = relationship(back_populates="life_arc")


class Season(Base):
    """A bounded phase of focus within a life arc.

    Seasons have a thesis (why this focus now), a priority stack,
    and defined start/end dates. They are not sprints — they are
    strategic focus periods.
    """

    __tablename__ = "seasons"
    __table_args__ = {"schema": "vector_ctrl"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("core.operators.id"), nullable=False
    )
    life_arc_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("vector_ctrl.life_arcs.id"), nullable=True
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    thesis: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    end_date: Mapped[datetime.date | None] = mapped_column(Date, nullable=True)
    priority_stack: Mapped[list] = mapped_column(
        JSONB, nullable=False, server_default="[]"
    )
    status: Mapped[SeasonStatus] = mapped_column(
        Enum(SeasonStatus, name="season_status", schema="core", create_type=False),
        nullable=False,
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    life_arc: Mapped[LifeArc | None] = relationship(back_populates="seasons")
    missions: Mapped[list["Mission"]] = relationship(back_populates="season")


class Mission(Base):
    """A strategically meaningful objective within a season.

    Missions have explicit success, failure, and drift definitions.
    This is not a task — it is a directional commitment with defined
    boundaries for what counts as progress, failure, or drift.
    """

    __tablename__ = "missions"
    __table_args__ = {"schema": "vector_ctrl"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("core.operators.id"), nullable=False
    )
    season_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("vector_ctrl.seasons.id"), nullable=True
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    mission_kind: Mapped[MissionKind] = mapped_column(
        Enum(MissionKind, name="mission_kind", schema="core", create_type=False),
        nullable=False,
    )
    priority_score: Mapped[decimal.Decimal | None] = mapped_column(
        Numeric(6, 3), nullable=True
    )
    status: Mapped[Status] = mapped_column(
        Enum(Status, name="status", schema="core", create_type=False),
        nullable=False,
    )
    success_definition: Mapped[str | None] = mapped_column(Text, nullable=True)
    failure_definition: Mapped[str | None] = mapped_column(Text, nullable=True)
    drift_definition: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    season: Mapped[Season | None] = relationship(back_populates="missions")
    threads: Mapped[list["Thread"]] = relationship(
        back_populates="mission", foreign_keys="Thread.mission_id"
    )


class Thread(Base):
    """A live line of work within a mission.

    Threads carry operational metadata that the execution layer uses:
    complexity, ambiguity, re-entry risk scores, the next edge summary,
    and last meaningful touch. Threads can nest via parent_thread_id.
    """

    __tablename__ = "threads"
    __table_args__ = {"schema": "vector_ctrl"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("core.operators.id"), nullable=False
    )
    mission_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("vector_ctrl.missions.id"), nullable=False
    )
    parent_thread_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("vector_ctrl.threads.id"), nullable=True
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    thread_kind: Mapped[ThreadKind] = mapped_column(
        Enum(ThreadKind, name="thread_kind", schema="core", create_type=False),
        nullable=False,
    )
    status: Mapped[ThreadStatus] = mapped_column(
        Enum(ThreadStatus, name="thread_status", schema="core", create_type=False),
        nullable=False,
    )
    complexity_score: Mapped[decimal.Decimal | None] = mapped_column(
        Numeric(6, 3), nullable=True
    )
    ambiguity_score: Mapped[decimal.Decimal | None] = mapped_column(
        Numeric(6, 3), nullable=True
    )
    reentry_risk_score: Mapped[decimal.Decimal | None] = mapped_column(
        Numeric(6, 3), nullable=True
    )
    last_meaningful_touch_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    next_edge_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    mission: Mapped[Mission] = relationship(back_populates="threads")
    parent_thread: Mapped["Thread | None"] = relationship(
        remote_side=[id], foreign_keys=[parent_thread_id]
    )
    constraints: Mapped[list["ThreadConstraint"]] = relationship(back_populates="thread")


class ThreadConstraint(Base):
    """An explicit constraint on a thread.

    Constraint types: time, dependency, budget, skill, legal.
    Hardness: hard, soft, assumed.
    """

    __tablename__ = "thread_constraints"
    __table_args__ = {"schema": "vector_ctrl"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    thread_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("vector_ctrl.threads.id"), nullable=False
    )
    constraint_type: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    hardness: Mapped[ConstraintHardness] = mapped_column(
        Enum(ConstraintHardness, name="constraint_hardness", schema="core", create_type=False),
        nullable=False,
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    thread: Mapped[Thread] = relationship(back_populates="constraints")


class AntiGoal(Base):
    """What must not happen — scoped to any level of the directional hierarchy.

    Anti-goals are not nice-to-haves. They are hard boundaries
    that Vector uses to detect drift and block misaligned action.
    """

    __tablename__ = "anti_goals"
    __table_args__ = {"schema": "vector_ctrl"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("core.operators.id"), nullable=False
    )
    scope_type: Mapped[str] = mapped_column(Text, nullable=False)
    scope_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
