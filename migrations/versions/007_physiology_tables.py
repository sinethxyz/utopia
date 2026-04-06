"""M007: physiology tables — WHOOP integration and derived physiological features.

WHOOP is a first-class body-state subsystem. Its data enriches state estimation
with physiological priors: recovery score, HRV, strain, sleep quality, and
derived features (capacity_envelope, fragility_risk, depth_ceiling) feed the
State Estimator and Blocker Classifier.

Matches: Utopia Formal Architecture DB etc.md section 12.

Revision ID: 007
Revises: 006
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, JSONB

revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- whoop_connections ---
    op.create_table(
        "whoop_connections",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column(
            "oauth_connection_id",
            sa.Uuid(),
            sa.ForeignKey("integration.oauth_connections.id"),
            nullable=False,
        ),
        sa.Column("scope_granted", ARRAY(sa.Text()), nullable=False, server_default="{}"),
        sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="physiology",
    )
    op.create_index(
        "ix_physiology_whoop_connections_operator_id",
        "whoop_connections", ["operator_id"],
        schema="physiology",
    )

    # --- whoop_body_measurements ---
    op.create_table(
        "whoop_body_measurements",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("measured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("height_cm", sa.Integer(), nullable=True),
        sa.Column("weight_kg", sa.Integer(), nullable=True),
        sa.Column("max_heart_rate", sa.Integer(), nullable=True),
        sa.Column("source_payload", JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="physiology",
    )
    op.create_index(
        "ix_physiology_whoop_body_measurements_operator_created",
        "whoop_body_measurements", ["operator_id", sa.text("created_at DESC")],
        schema="physiology",
    )

    # --- whoop_cycles ---
    op.create_table(
        "whoop_cycles",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("provider_cycle_id", sa.BigInteger(), nullable=False),
        sa.Column("whoop_user_id", sa.BigInteger(), nullable=True),
        sa.Column("cycle_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cycle_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("timezone_offset", sa.Text(), nullable=True),
        sa.Column("score_state", sa.Text(), nullable=True),
        sa.Column("strain", sa.Numeric(8, 4), nullable=True),
        sa.Column("kilojoule", sa.Numeric(12, 3), nullable=True),
        sa.Column("average_heart_rate", sa.Integer(), nullable=True),
        sa.Column("max_heart_rate", sa.Integer(), nullable=True),
        sa.Column("source_payload", JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("provider_cycle_id", name="uq_whoop_cycles_provider_cycle_id"),
        schema="physiology",
    )
    op.create_index(
        "ix_physiology_whoop_cycles_operator_created",
        "whoop_cycles", ["operator_id", sa.text("created_at DESC")],
        schema="physiology",
    )

    # --- whoop_sleeps ---
    op.create_table(
        "whoop_sleeps",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("provider_sleep_id", sa.Uuid(), nullable=False),
        sa.Column("provider_cycle_id", sa.BigInteger(), nullable=True),
        sa.Column("sleep_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sleep_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sleep_performance_pct", sa.Numeric(5, 2), nullable=True),
        sa.Column("total_in_bed_ms", sa.BigInteger(), nullable=True),
        sa.Column("total_asleep_ms", sa.BigInteger(), nullable=True),
        sa.Column("slow_wave_ms", sa.BigInteger(), nullable=True),
        sa.Column("rem_ms", sa.BigInteger(), nullable=True),
        sa.Column("light_ms", sa.BigInteger(), nullable=True),
        sa.Column("awake_ms", sa.BigInteger(), nullable=True),
        sa.Column("source_payload", JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("provider_sleep_id", name="uq_whoop_sleeps_provider_sleep_id"),
        schema="physiology",
    )
    op.create_index(
        "ix_physiology_whoop_sleeps_operator_created",
        "whoop_sleeps", ["operator_id", sa.text("created_at DESC")],
        schema="physiology",
    )

    # --- whoop_recoveries ---
    op.create_table(
        "whoop_recoveries",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("provider_cycle_id", sa.BigInteger(), nullable=False),
        sa.Column("provider_sleep_id", sa.Uuid(), nullable=False),
        sa.Column("whoop_user_id", sa.BigInteger(), nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at_source", sa.DateTime(timezone=True), nullable=True),
        sa.Column("score_state", sa.Text(), nullable=False),
        sa.Column("recovery_score", sa.SmallInteger(), nullable=True),
        sa.Column("resting_heart_rate", sa.Integer(), nullable=True),
        sa.Column("hrv_rmssd_milli", sa.Numeric(12, 6), nullable=True),
        sa.Column("spo2_percentage", sa.Numeric(6, 3), nullable=True),
        sa.Column("skin_temp_celsius", sa.Numeric(6, 3), nullable=True),
        sa.Column("user_calibrating", sa.Boolean(), nullable=True),
        sa.Column("source_payload", JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint(
            "operator_id", "provider_cycle_id", "provider_sleep_id",
            name="uq_whoop_recoveries_operator_cycle_sleep",
        ),
        schema="physiology",
    )
    op.create_index(
        "ix_physiology_whoop_recoveries_operator_recorded",
        "whoop_recoveries", ["operator_id", sa.text("recorded_at DESC")],
        schema="physiology",
    )

    # --- whoop_workouts ---
    op.create_table(
        "whoop_workouts",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("provider_workout_id", sa.Uuid(), nullable=False),
        sa.Column("workout_type", sa.Text(), nullable=True),
        sa.Column("workout_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("workout_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("strain", sa.Numeric(8, 4), nullable=True),
        sa.Column("average_heart_rate", sa.Integer(), nullable=True),
        sa.Column("max_heart_rate", sa.Integer(), nullable=True),
        sa.Column("source_payload", JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("provider_workout_id", name="uq_whoop_workouts_provider_workout_id"),
        schema="physiology",
    )
    op.create_index(
        "ix_physiology_whoop_workouts_operator_created",
        "whoop_workouts", ["operator_id", sa.text("created_at DESC")],
        schema="physiology",
    )

    # --- physiology_features ---
    op.create_table(
        "physiology_features",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("feature_date", sa.Date(), nullable=False),
        sa.Column("feature_name", sa.Text(), nullable=False),
        sa.Column("feature_value", sa.Numeric(), nullable=True),
        sa.Column("feature_json", JSONB(), nullable=True),
        sa.Column("confidence", sa.Numeric(5, 4), nullable=True),
        sa.Column("computed_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint(
            "operator_id", "feature_date", "feature_name",
            name="uq_physiology_features_operator_date_name",
        ),
        schema="physiology",
    )
    op.create_index(
        "ix_physiology_features_operator_date",
        "physiology_features", ["operator_id", "feature_date"],
        schema="physiology",
    )

    # --- biomarker_panels ---
    op.create_table(
        "biomarker_panels",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("panel_date", sa.Date(), nullable=False),
        sa.Column("provider", sa.Text(), nullable=False),
        sa.Column("panel_type", sa.Text(), nullable=False),
        sa.Column("summary", JSONB(), nullable=False),
        sa.Column("source_payload", JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="physiology",
    )
    op.create_index(
        "ix_physiology_biomarker_panels_operator_created",
        "biomarker_panels", ["operator_id", sa.text("created_at DESC")],
        schema="physiology",
    )


def downgrade() -> None:
    op.drop_index("ix_physiology_biomarker_panels_operator_created", table_name="biomarker_panels", schema="physiology")
    op.drop_table("biomarker_panels", schema="physiology")

    op.drop_index("ix_physiology_features_operator_date", table_name="physiology_features", schema="physiology")
    op.drop_table("physiology_features", schema="physiology")

    op.drop_index("ix_physiology_whoop_workouts_operator_created", table_name="whoop_workouts", schema="physiology")
    op.drop_table("whoop_workouts", schema="physiology")

    op.drop_index("ix_physiology_whoop_recoveries_operator_recorded", table_name="whoop_recoveries", schema="physiology")
    op.drop_table("whoop_recoveries", schema="physiology")

    op.drop_index("ix_physiology_whoop_sleeps_operator_created", table_name="whoop_sleeps", schema="physiology")
    op.drop_table("whoop_sleeps", schema="physiology")

    op.drop_index("ix_physiology_whoop_cycles_operator_created", table_name="whoop_cycles", schema="physiology")
    op.drop_table("whoop_cycles", schema="physiology")

    op.drop_index("ix_physiology_whoop_body_measurements_operator_created", table_name="whoop_body_measurements", schema="physiology")
    op.drop_table("whoop_body_measurements", schema="physiology")

    op.drop_index("ix_physiology_whoop_connections_operator_id", table_name="whoop_connections", schema="physiology")
    op.drop_table("whoop_connections", schema="physiology")
