"""M009: reasoning tables — problem structurer and decision artifacts.

The Reasoning layer is the Problem Room. It captures the full arc of a
decision: raw prompt → structured problem → interrogations → decision brief
→ option paths → contradiction reports.

This migration also activates the deferred FK:
  execution.policy_decisions.problem_id -> reasoning.problems.id
That column was added in M006 as a nullable UUID with no FK constraint.

Matches: Utopia Formal Architecture DB etc.md section 14.

Revision ID: 009
Revises: 008
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, JSONB

revision: str = "009"
down_revision: Union[str, None] = "008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- problems ---
    op.create_table(
        "problems",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("raw_prompt", sa.Text(), nullable=False),
        sa.Column("problem_kind", sa.Text(), nullable=True),
        sa.Column("urgency_score", sa.Numeric(6, 3), nullable=True),
        sa.Column("stakes_score", sa.Numeric(6, 3), nullable=True),
        sa.Column("uncertainty_score", sa.Numeric(6, 3), nullable=True),
        sa.Column("state_at_creation", sa.Text(), nullable=True),
        sa.Column("thread_id", sa.Uuid(), sa.ForeignKey("vector_ctrl.threads.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="reasoning",
    )
    op.create_index(
        "ix_reasoning_problems_operator_created",
        "problems", ["operator_id", sa.text("created_at DESC")],
        schema="reasoning",
    )
    op.create_index(
        "ix_reasoning_problems_thread_id",
        "problems", ["thread_id"],
        schema="reasoning",
    )

    # --- problem_structures ---
    op.create_table(
        "problem_structures",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("problem_id", sa.Uuid(), sa.ForeignKey("reasoning.problems.id"), nullable=False),
        sa.Column("objective", sa.Text(), nullable=True),
        sa.Column("stakes", sa.Text(), nullable=True),
        sa.Column("actors", JSONB(), nullable=False, server_default="[]"),
        sa.Column("incentives", JSONB(), nullable=False, server_default="[]"),
        sa.Column("constraints", JSONB(), nullable=False, server_default="[]"),
        sa.Column("assumptions", JSONB(), nullable=False, server_default="[]"),
        sa.Column("unknowns", JSONB(), nullable=False, server_default="[]"),
        sa.Column("irreversibilities", JSONB(), nullable=False, server_default="[]"),
        sa.Column("bottlenecks", JSONB(), nullable=False, server_default="[]"),
        sa.Column("observable_facts", JSONB(), nullable=False, server_default="[]"),
        sa.Column("narrative_layer", JSONB(), nullable=False, server_default="[]"),
        sa.Column("distortion_candidates", JSONB(), nullable=False, server_default="[]"),
        sa.Column("confidence", sa.Numeric(5, 4), nullable=True),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="reasoning",
    )
    op.create_index(
        "ix_reasoning_problem_structures_problem_id",
        "problem_structures", ["problem_id"],
        schema="reasoning",
    )

    # --- interrogations ---
    op.create_table(
        "interrogations",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("problem_id", sa.Uuid(), sa.ForeignKey("reasoning.problems.id"), nullable=False),
        sa.Column("interrogation_kind", sa.Text(), nullable=False),
        sa.Column("questions", JSONB(), nullable=False),
        sa.Column("rationale", JSONB(), nullable=True),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="reasoning",
    )
    op.create_index(
        "ix_reasoning_interrogations_problem_id",
        "interrogations", ["problem_id"],
        schema="reasoning",
    )

    # --- decision_briefs ---
    op.create_table(
        "decision_briefs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("problem_id", sa.Uuid(), sa.ForeignKey("reasoning.problems.id"), nullable=False),
        sa.Column("classification", sa.Text(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("key_unknowns", JSONB(), nullable=False, server_default="[]"),
        sa.Column("blind_spots", JSONB(), nullable=False, server_default="[]"),
        sa.Column("risks", JSONB(), nullable=False, server_default="[]"),
        sa.Column("relevant_lens_pack_ids", ARRAY(sa.Uuid()), nullable=False, server_default="{}"),
        sa.Column("recommendation_summary", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Numeric(5, 4), nullable=True),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="reasoning",
    )
    op.create_index(
        "ix_reasoning_decision_briefs_problem_id",
        "decision_briefs", ["problem_id"],
        schema="reasoning",
    )

    # --- option_paths ---
    op.create_table(
        "option_paths",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("decision_brief_id", sa.Uuid(), sa.ForeignKey("reasoning.decision_briefs.id"), nullable=False),
        sa.Column("option_label", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("expected_upside", sa.Text(), nullable=True),
        sa.Column("expected_downside", sa.Text(), nullable=True),
        sa.Column("reversibility", sa.Text(), nullable=True),
        sa.Column("risk_score", sa.Numeric(6, 3), nullable=True),
        sa.Column("recommendation_rank", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="reasoning",
    )
    op.create_index(
        "ix_reasoning_option_paths_brief_id",
        "option_paths", ["decision_brief_id"],
        schema="reasoning",
    )

    # --- contradiction_reports ---
    op.create_table(
        "contradiction_reports",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("problem_id", sa.Uuid(), sa.ForeignKey("reasoning.problems.id"), nullable=True),
        sa.Column("contradiction_kind", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("evidence", JSONB(), nullable=False, server_default="[]"),
        sa.Column("severity", sa.Numeric(6, 3), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="reasoning",
    )
    op.create_index(
        "ix_reasoning_contradiction_reports_operator_created",
        "contradiction_reports", ["operator_id", sa.text("created_at DESC")],
        schema="reasoning",
    )
    op.create_index(
        "ix_reasoning_contradiction_reports_problem_id",
        "contradiction_reports", ["problem_id"],
        schema="reasoning",
    )

    # --- Activate deferred FK: execution.policy_decisions.problem_id ---
    # This FK was intentionally deferred in M006 because reasoning.problems
    # did not exist yet. Now that reasoning.problems is created, we activate it.
    op.create_foreign_key(
        "fk_policy_decisions_problem_id",
        "policy_decisions", "problems",
        ["problem_id"], ["id"],
        source_schema="execution",
        referent_schema="reasoning",
    )


def downgrade() -> None:
    # Drop deferred FK first
    op.drop_constraint(
        "fk_policy_decisions_problem_id",
        "policy_decisions",
        schema="execution",
        type_="foreignkey",
    )

    op.drop_index("ix_reasoning_contradiction_reports_problem_id", table_name="contradiction_reports", schema="reasoning")
    op.drop_index("ix_reasoning_contradiction_reports_operator_created", table_name="contradiction_reports", schema="reasoning")
    op.drop_table("contradiction_reports", schema="reasoning")

    op.drop_index("ix_reasoning_option_paths_brief_id", table_name="option_paths", schema="reasoning")
    op.drop_table("option_paths", schema="reasoning")

    op.drop_index("ix_reasoning_decision_briefs_problem_id", table_name="decision_briefs", schema="reasoning")
    op.drop_table("decision_briefs", schema="reasoning")

    op.drop_index("ix_reasoning_interrogations_problem_id", table_name="interrogations", schema="reasoning")
    op.drop_table("interrogations", schema="reasoning")

    op.drop_index("ix_reasoning_problem_structures_problem_id", table_name="problem_structures", schema="reasoning")
    op.drop_table("problem_structures", schema="reasoning")

    op.drop_index("ix_reasoning_problems_thread_id", table_name="problems", schema="reasoning")
    op.drop_index("ix_reasoning_problems_operator_created", table_name="problems", schema="reasoning")
    op.drop_table("problems", schema="reasoning")
