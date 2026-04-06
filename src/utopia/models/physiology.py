"""physiology ORM models — WHOOP integration and derived physiological features.

WHOOP data is a first-class subsystem. These tables capture raw provider
payloads (cycles, sleeps, recoveries, workouts) plus derived features
(capacity_envelope, fragility_risk, depth_ceiling) that feed the
State Estimator and Blocker Classifier.

Matches: Utopia Formal Architecture DB etc.md section 12.
"""

import datetime
import decimal
import uuid

from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, Integer, Numeric, SmallInteger, Text, text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from utopia.db import Base


class WhoopConnection(Base):
    """OAuth linkage between an operator and their WHOOP account."""

    __tablename__ = "whoop_connections"
    __table_args__ = {"schema": "physiology"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("core.operators.id"), nullable=False
    )
    oauth_connection_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("integration.oauth_connections.id"), nullable=False
    )
    scope_granted: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, server_default="{}"
    )
    last_sync_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )


class WhoopBodyMeasurement(Base):
    """Physical measurements reported by the WHOOP API."""

    __tablename__ = "whoop_body_measurements"
    __table_args__ = {"schema": "physiology"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("core.operators.id"), nullable=False
    )
    measured_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    height_cm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    weight_kg: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_heart_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )


class WhoopCycle(Base):
    """A WHOOP physiological cycle (24-hour window)."""

    __tablename__ = "whoop_cycles"
    __table_args__ = {"schema": "physiology"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("core.operators.id"), nullable=False
    )
    provider_cycle_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    whoop_user_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    cycle_start: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    cycle_end: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    timezone_offset: Mapped[str | None] = mapped_column(Text, nullable=True)
    score_state: Mapped[str | None] = mapped_column(Text, nullable=True)
    strain: Mapped[decimal.Decimal | None] = mapped_column(Numeric(8, 4), nullable=True)
    kilojoule: Mapped[decimal.Decimal | None] = mapped_column(Numeric(12, 3), nullable=True)
    average_heart_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_heart_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )


class WhoopSleep(Base):
    """A WHOOP sleep record with stage breakdown."""

    __tablename__ = "whoop_sleeps"
    __table_args__ = {"schema": "physiology"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("core.operators.id"), nullable=False
    )
    provider_sleep_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    provider_cycle_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    sleep_start: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    sleep_end: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    sleep_performance_pct: Mapped[decimal.Decimal | None] = mapped_column(
        Numeric(5, 2), nullable=True
    )
    total_in_bed_ms: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    total_asleep_ms: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    slow_wave_ms: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    rem_ms: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    light_ms: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    awake_ms: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    source_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )


class WhoopRecovery(Base):
    """Daily readiness score derived from sleep and HRV."""

    __tablename__ = "whoop_recoveries"
    __table_args__ = {"schema": "physiology"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("core.operators.id"), nullable=False
    )
    provider_cycle_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    provider_sleep_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    whoop_user_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    recorded_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    updated_at_source: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    score_state: Mapped[str] = mapped_column(Text, nullable=False)
    recovery_score: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    resting_heart_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    hrv_rmssd_milli: Mapped[decimal.Decimal | None] = mapped_column(
        Numeric(12, 6), nullable=True
    )
    spo2_percentage: Mapped[decimal.Decimal | None] = mapped_column(
        Numeric(6, 3), nullable=True
    )
    skin_temp_celsius: Mapped[decimal.Decimal | None] = mapped_column(
        Numeric(6, 3), nullable=True
    )
    user_calibrating: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    source_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )


class WhoopWorkout(Base):
    """A recorded workout session with strain scoring."""

    __tablename__ = "whoop_workouts"
    __table_args__ = {"schema": "physiology"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("core.operators.id"), nullable=False
    )
    provider_workout_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    workout_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    workout_start: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    workout_end: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    strain: Mapped[decimal.Decimal | None] = mapped_column(Numeric(8, 4), nullable=True)
    average_heart_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_heart_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )


class PhysiologyFeature(Base):
    """A derived physiological feature for a given operator and date.

    Feature names include: capacity_envelope, fragility_risk,
    sleep_debt_slope, recovery_trend_3d, recovery_volatility_7d,
    strain_carryover, sleep_regularity_score, depth_ceiling_score,
    depletion_prior, recovery_mismatch_score.
    """

    __tablename__ = "physiology_features"
    __table_args__ = {"schema": "physiology"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("core.operators.id"), nullable=False
    )
    feature_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    feature_name: Mapped[str] = mapped_column(Text, nullable=False)
    feature_value: Mapped[decimal.Decimal | None] = mapped_column(Numeric, nullable=True)
    feature_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    confidence: Mapped[decimal.Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    computed_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class BiomarkerPanel(Base):
    """A laboratory biomarker panel result."""

    __tablename__ = "biomarker_panels"
    __table_args__ = {"schema": "physiology"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("core.operators.id"), nullable=False
    )
    panel_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    provider: Mapped[str] = mapped_column(Text, nullable=False)
    panel_type: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[dict] = mapped_column(JSONB, nullable=False)
    source_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
