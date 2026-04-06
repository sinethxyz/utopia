"""M010: review tables — the system's immune layer.

Review & Calibration captures thread/mission closures, runs periodic
review sessions, promotes insights to Aether rules, updates patterns
from reviewed evidence, and calibrates estimate accuracy over time.

The ``review`` PostgreSQL schema was not included in M001, so this
migration creates it before building the five tables.

Matches: Utopia Formal Architecture DB etc.md Review & Calibration section.

Revision ID: 010
Revises: 009
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "010"
down_revision: Union[str, None] = "009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- create the review schema ---
    op.execute("CREATE SCHEMA IF NOT EXISTS review")

    # --- closures ---
    op.create_table(
        "closures",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("thread_id", sa.Uuid(), sa.ForeignKey("vector_ctrl.threads.id"), nullable=True),
        sa.Column("mission_id", sa.Uuid(), sa.ForeignKey("vector_ctrl.missions.id"), nullable=True),
        sa.Column("closure_type", sa.Enum("complete", "archive", "pause", "merge", name="closure_type", schema="core", create_type=False), nullable=False),
        sa.Column("outcome_summary", sa.Text(), nullable=True),
        sa.Column("lessons_learned", JSONB(), nullable=False, server_default="[]"),
        sa.Column("truth_revealed", sa.Text(), nullable=True),
        sa.Column("final_trace_id", sa.Uuid(), sa.ForeignKey("execution.traces.id"), nullable=True),
        sa.Column("success_score", sa.Numeric(6, 3), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="review",
    )
    op.create_index(
        "ix_review_closures_operator_created",
        "closures", ["operator_id", sa.text("created_at DESC")],
        schema="review",
    )
    op.create_index(
        "ix_review_closures_thread_id",
        "closures", ["thread_id"],
        schema="review",
    )
    op.create_index(
        "ix_review_closures_mission_id",
        "closures", ["mission_id"],
        schema="review",
    )

    # --- review_sessions ---
    op.create_table(
        "review_sessions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("review_scope", sa.Enum("micro", "daily", "weekly", "monthly", name="review_scope", schema="core", create_type=False), nullable=False),
        sa.Column("window_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("window_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("insights", JSONB(), nullable=False, server_default="[]"),
        sa.Column("trace_ids_reviewed", JSONB(), nullable=False, server_default="[]"),
        sa.Column("patterns_identified", JSONB(), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="review",
    )
    op.create_index(
        "ix_review_sessions_operator_created",
        "review_sessions", ["operator_id", sa.text("created_at DESC")],
        schema="review",
    )
    op.create_index(
        "ix_review_sessions_scope",
        "review_sessions", ["review_scope"],
        schema="review",
    )

    # --- rule_promotions ---
    op.create_table(
        "rule_promotions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("review_session_id", sa.Uuid(), sa.ForeignKey("review.review_sessions.id"), nullable=False),
        sa.Column("rule_id", sa.Uuid(), sa.ForeignKey("aether.rules.id"), nullable=False),
        sa.Column("evidence_summary", sa.Text(), nullable=True),
        sa.Column("supporting_trace_ids", JSONB(), nullable=False, server_default="[]"),
        sa.Column("confidence", sa.Numeric(5, 4), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="review",
    )
    op.create_index(
        "ix_review_rule_promotions_session_id",
        "rule_promotions", ["review_session_id"],
        schema="review",
    )
    op.create_index(
        "ix_review_rule_promotions_rule_id",
        "rule_promotions", ["rule_id"],
        schema="review",
    )

    # --- pattern_updates ---
    op.create_table(
        "pattern_updates",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("review_session_id", sa.Uuid(), sa.ForeignKey("review.review_sessions.id"), nullable=False),
        sa.Column("pattern_id", sa.Uuid(), sa.ForeignKey("aether.patterns.id"), nullable=False),
        sa.Column("update_kind", sa.Text(), nullable=False),
        sa.Column("evidence_summary", sa.Text(), nullable=True),
        sa.Column("supporting_trace_ids", JSONB(), nullable=False, server_default="[]"),
        sa.Column("confidence_before", sa.Numeric(5, 4), nullable=True),
        sa.Column("confidence_after", sa.Numeric(5, 4), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="review",
    )
    op.create_index(
        "ix_review_pattern_updates_session_id",
        "pattern_updates", ["review_session_id"],
        schema="review",
    )
    op.create_index(
        "ix_review_pattern_updates_pattern_id",
        "pattern_updates", ["pattern_id"],
        schema="review",
    )

    # --- calibration_records ---
    op.create_table(
        "calibration_records",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("review_session_id", sa.Uuid(), sa.ForeignKey("review.review_sessions.id"), nullable=True),
        sa.Column("estimate_kind", sa.Text(), nullable=False),
        sa.Column("estimate_id", sa.Uuid(), nullable=False),
        sa.Column("trace_id", sa.Uuid(), sa.ForeignKey("execution.traces.id"), nullable=True),
        sa.Column("predicted_value", JSONB(), nullable=False, server_default="{}"),
        sa.Column("actual_value", JSONB(), nullable=False, server_default="{}"),
        sa.Column("accuracy_score", sa.Numeric(5, 4), nullable=True),
        sa.Column("drift_direction", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="review",
    )
    op.create_index(
        "ix_review_calibration_records_operator_created",
        "calibration_records", ["operator_id", sa.text("created_at DESC")],
        schema="review",
    )
    op.create_index(
        "ix_review_calibration_records_estimate",
        "calibration_records", ["estimate_kind", "estimate_id"],
        schema="review",
    )
    op.create_index(
        "ix_review_calibration_records_session_id",
        "calibration_records", ["review_session_id"],
        schema="review",
    )


def downgrade() -> None:
    op.drop_index("ix_review_calibration_records_session_id", table_name="calibration_records", schema="review")
    op.drop_index("ix_review_calibration_records_estimate", table_name="calibration_records", schema="review")
    op.drop_index("ix_review_calibration_records_operator_created", table_name="calibration_records", schema="review")
    op.drop_table("calibration_records", schema="review")

    op.drop_index("ix_review_pattern_updates_pattern_id", table_name="pattern_updates", schema="review")
    op.drop_index("ix_review_pattern_updates_session_id", table_name="pattern_updates", schema="review")
    op.drop_table("pattern_updates", schema="review")

    op.drop_index("ix_review_rule_promotions_rule_id", table_name="rule_promotions", schema="review")
    op.drop_index("ix_review_rule_promotions_session_id", table_name="rule_promotions", schema="review")
    op.drop_table("rule_promotions", schema="review")

    op.drop_index("ix_review_sessions_scope", table_name="review_sessions", schema="review")
    op.drop_index("ix_review_sessions_operator_created", table_name="review_sessions", schema="review")
    op.drop_table("review_sessions", schema="review")

    op.drop_index("ix_review_closures_mission_id", table_name="closures", schema="review")
    op.drop_index("ix_review_closures_thread_id", table_name="closures", schema="review")
    op.drop_index("ix_review_closures_operator_created", table_name="closures", schema="review")
    op.drop_table("closures", schema="review")

    op.execute("DROP SCHEMA IF EXISTS review")
