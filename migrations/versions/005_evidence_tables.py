"""M005: evidence tables — the live sensing layer.

Evidence captures subjective, behavioral, and contextual truth
about the operator's present moment. Derived features store
computed signals from raw evidence.

Matches: Utopia Formal Architecture DB etc.md section 7.

Revision ID: 005
Revises: 004
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- subjective_checkins ---
    op.create_table(
        "subjective_checkins",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("thread_id", sa.Uuid(), sa.ForeignKey("vector_ctrl.threads.id"), nullable=True),
        sa.Column("energy", sa.SmallInteger(), nullable=True),
        sa.Column("clarity", sa.SmallInteger(), nullable=True),
        sa.Column("resistance", sa.SmallInteger(), nullable=True),
        sa.Column("overwhelm", sa.SmallInteger(), nullable=True),
        sa.Column("emotional_load", sa.SmallInteger(), nullable=True),
        sa.Column("perceived_urgency", sa.SmallInteger(), nullable=True),
        sa.Column("free_text", sa.Text(), nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("energy IS NULL OR (energy BETWEEN 0 AND 100)", name="ck_checkin_energy"),
        sa.CheckConstraint("clarity IS NULL OR (clarity BETWEEN 0 AND 100)", name="ck_checkin_clarity"),
        sa.CheckConstraint("resistance IS NULL OR (resistance BETWEEN 0 AND 100)", name="ck_checkin_resistance"),
        sa.CheckConstraint("overwhelm IS NULL OR (overwhelm BETWEEN 0 AND 100)", name="ck_checkin_overwhelm"),
        sa.CheckConstraint("emotional_load IS NULL OR (emotional_load BETWEEN 0 AND 100)", name="ck_checkin_emotional_load"),
        sa.CheckConstraint("perceived_urgency IS NULL OR (perceived_urgency BETWEEN 0 AND 100)", name="ck_checkin_perceived_urgency"),
        schema="evidence",
    )
    op.create_index(
        "ix_evidence_subjective_checkins_operator_recorded",
        "subjective_checkins", ["operator_id", sa.text("recorded_at DESC")],
        schema="evidence",
    )
    op.create_index(
        "ix_evidence_subjective_checkins_thread_id",
        "subjective_checkins", ["thread_id"],
        schema="evidence",
    )

    # --- behavior_events ---
    op.create_table(
        "behavior_events",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("thread_id", sa.Uuid(), sa.ForeignKey("vector_ctrl.threads.id"), nullable=True),
        sa.Column("event_type", sa.Text(), nullable=False),
        sa.Column("event_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("duration_ms", sa.BigInteger(), nullable=True),
        sa.Column("metadata", JSONB(), nullable=False, server_default="{}"),
        schema="evidence",
    )
    op.create_index(
        "ix_evidence_behavior_events_operator_event_at",
        "behavior_events", ["operator_id", sa.text("event_at DESC")],
        schema="evidence",
    )
    op.create_index(
        "ix_evidence_behavior_events_thread_id",
        "behavior_events", ["thread_id"],
        schema="evidence",
    )
    op.create_index(
        "ix_evidence_behavior_events_event_type",
        "behavior_events", ["event_type", sa.text("event_at DESC")],
        schema="evidence",
    )

    # --- context_snapshots ---
    op.create_table(
        "context_snapshots",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("thread_id", sa.Uuid(), sa.ForeignKey("vector_ctrl.threads.id"), nullable=True),
        sa.Column("local_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("environment_label", sa.Text(), nullable=True),
        sa.Column("interruption_count", sa.Integer(), nullable=True),
        sa.Column("obligation_load", sa.SmallInteger(), nullable=True),
        sa.Column("available_minutes", sa.Integer(), nullable=True),
        sa.Column("active_window", sa.Text(), nullable=True),
        sa.Column("metadata", JSONB(), nullable=False, server_default="{}"),
        schema="evidence",
    )
    op.create_index(
        "ix_evidence_context_snapshots_operator_local_time",
        "context_snapshots", ["operator_id", sa.text("local_time DESC")],
        schema="evidence",
    )

    # --- derived_features ---
    op.create_table(
        "derived_features",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("thread_id", sa.Uuid(), sa.ForeignKey("vector_ctrl.threads.id"), nullable=True),
        sa.Column("feature_name", sa.Text(), nullable=False),
        sa.Column("feature_value", sa.Numeric(), nullable=True),
        sa.Column("feature_json", JSONB(), nullable=True),
        sa.Column("feature_window", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Numeric(5, 4), nullable=True),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="evidence",
    )
    op.create_index(
        "ix_evidence_derived_features_operator_observed",
        "derived_features", ["operator_id", sa.text("observed_at DESC")],
        schema="evidence",
    )
    op.create_index(
        "ix_evidence_derived_features_name_window",
        "derived_features", ["feature_name", "feature_window"],
        schema="evidence",
    )
    op.create_index(
        "ix_evidence_derived_features_thread_id",
        "derived_features", ["thread_id"],
        schema="evidence",
    )


def downgrade() -> None:
    op.drop_index("ix_evidence_derived_features_thread_id", table_name="derived_features", schema="evidence")
    op.drop_index("ix_evidence_derived_features_name_window", table_name="derived_features", schema="evidence")
    op.drop_index("ix_evidence_derived_features_operator_observed", table_name="derived_features", schema="evidence")
    op.drop_table("derived_features", schema="evidence")

    op.drop_index("ix_evidence_context_snapshots_operator_local_time", table_name="context_snapshots", schema="evidence")
    op.drop_table("context_snapshots", schema="evidence")

    op.drop_index("ix_evidence_behavior_events_event_type", table_name="behavior_events", schema="evidence")
    op.drop_index("ix_evidence_behavior_events_thread_id", table_name="behavior_events", schema="evidence")
    op.drop_index("ix_evidence_behavior_events_operator_event_at", table_name="behavior_events", schema="evidence")
    op.drop_table("behavior_events", schema="evidence")

    op.drop_index("ix_evidence_subjective_checkins_thread_id", table_name="subjective_checkins", schema="evidence")
    op.drop_index("ix_evidence_subjective_checkins_operator_recorded", table_name="subjective_checkins", schema="evidence")
    op.drop_table("subjective_checkins", schema="evidence")
