"""M006: execution tables — state estimates, blockers, re-entry, policy, traces.

This closes Loop A: evidence -> inference -> policy -> outcome.
The execution schema records what the system infers about the operator's
state, what is blocking motion, what policy was selected, and what
actually happened afterward.

Matches: Utopia Formal Architecture DB etc.md section 11.

NOTE: policy_decisions.problem_id is nullable with no FK constraint.
The reasoning schema (reasoning.problems) does not exist yet.
A future migration will add the FK when reasoning tables are created.

Revision ID: 006
Revises: 005
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- state_estimates ---
    op.create_table(
        "state_estimates",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("thread_id", sa.Uuid(), sa.ForeignKey("vector_ctrl.threads.id"), nullable=True),
        sa.Column(
            "state_kind",
            sa.Enum(
                "recover", "preserve", "orient", "clarify", "reenter",
                "execute", "deep_work", "close_loop", "review", "drift",
                name="state_kind", schema="core", create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("confidence", sa.Numeric(5, 4), nullable=False),
        sa.Column("contributing_factors", JSONB(), nullable=False, server_default="[]"),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="execution",
    )
    op.create_index(
        "ix_execution_state_estimates_operator_generated",
        "state_estimates", ["operator_id", sa.text("generated_at DESC")],
        schema="execution",
    )
    op.create_index(
        "ix_execution_state_estimates_thread_id",
        "state_estimates", ["thread_id"],
        schema="execution",
    )

    # --- blocker_estimates ---
    op.create_table(
        "blocker_estimates",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("thread_id", sa.Uuid(), sa.ForeignKey("vector_ctrl.threads.id"), nullable=True),
        sa.Column(
            "blocker_kind",
            sa.Enum(
                "ambiguity", "scope_overload", "physiological_depletion",
                "emotional_threat", "context_fracture", "vector_conflict",
                "environmental_friction", "stimulation_hijack", "narrative_distortion",
                "completion_aversion", "problem_misclassification", "decision_fog",
                name="blocker_kind", schema="core", create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("confidence", sa.Numeric(5, 4), nullable=False),
        sa.Column("supporting_evidence", JSONB(), nullable=False, server_default="[]"),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="execution",
    )
    op.create_index(
        "ix_execution_blocker_estimates_operator_generated",
        "blocker_estimates", ["operator_id", sa.text("generated_at DESC")],
        schema="execution",
    )
    op.create_index(
        "ix_execution_blocker_estimates_thread_id",
        "blocker_estimates", ["thread_id"],
        schema="execution",
    )

    # --- reentry_artifacts ---
    op.create_table(
        "reentry_artifacts",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("thread_id", sa.Uuid(), sa.ForeignKey("vector_ctrl.threads.id"), nullable=False),
        sa.Column("last_completed_step", sa.Text(), nullable=True),
        sa.Column("unresolved_edge", sa.Text(), nullable=True),
        sa.Column("next_smallest_move", sa.Text(), nullable=True),
        sa.Column("trap_to_avoid", sa.Text(), nullable=True),
        sa.Column("relevant_context", JSONB(), nullable=False, server_default="{}"),
        sa.Column("freshness_score", sa.Numeric(6, 3), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("superseded_by", sa.Uuid(), nullable=True),
        schema="execution",
    )
    # Self-referential FK added after table exists
    op.create_foreign_key(
        "fk_reentry_artifacts_superseded_by",
        "reentry_artifacts", "reentry_artifacts",
        ["superseded_by"], ["id"],
        source_schema="execution", referent_schema="execution",
    )
    op.create_index(
        "ix_execution_reentry_artifacts_thread_created",
        "reentry_artifacts", ["thread_id", sa.text("created_at DESC")],
        schema="execution",
    )
    op.create_index(
        "ix_execution_reentry_artifacts_operator_id",
        "reentry_artifacts", ["operator_id"],
        schema="execution",
    )

    # --- policy_decisions (Schrödinger output) ---
    # NOTE: problem_id has no FK — reasoning.problems does not exist yet.
    # A future migration will add: ALTER TABLE ... ADD CONSTRAINT ...
    op.create_table(
        "policy_decisions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("thread_id", sa.Uuid(), sa.ForeignKey("vector_ctrl.threads.id"), nullable=True),
        sa.Column("problem_id", sa.Uuid(), nullable=True),  # deferred FK to reasoning.problems
        sa.Column("state_estimate_id", sa.Uuid(), sa.ForeignKey("execution.state_estimates.id"), nullable=True),
        sa.Column("blocker_estimate_id", sa.Uuid(), sa.ForeignKey("execution.blocker_estimates.id"), nullable=True),
        sa.Column(
            "mode",
            sa.Enum(
                "recover", "preserve", "orient", "reenter", "clarify",
                "ask", "execute", "close_loop", "review",
                name="intervention_kind", schema="core", create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "intervention_kind",
            sa.Enum(
                "recover", "preserve", "orient", "reenter", "clarify",
                "ask", "execute", "close_loop", "review",
                name="intervention_kind", schema="core", create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "action_depth",
            sa.Enum(
                "tiny", "narrow", "moderate", "deep",
                name="action_depth", schema="core", create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("next_move", sa.Text(), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Numeric(5, 4), nullable=True),
        sa.Column("caution_flags", JSONB(), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="execution",
    )
    op.create_index(
        "ix_execution_policy_decisions_operator_created",
        "policy_decisions", ["operator_id", sa.text("created_at DESC")],
        schema="execution",
    )
    op.create_index(
        "ix_execution_policy_decisions_thread_id",
        "policy_decisions", ["thread_id"],
        schema="execution",
    )

    # --- traces ---
    op.create_table(
        "traces",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("thread_id", sa.Uuid(), sa.ForeignKey("vector_ctrl.threads.id"), nullable=True),
        sa.Column("policy_decision_id", sa.Uuid(), sa.ForeignKey("execution.policy_decisions.id"), nullable=True),
        sa.Column(
            "trace_kind",
            sa.Enum(
                "action", "question", "preserve", "recovery", "closure",
                name="trace_kind", schema="core", create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("action_taken", sa.Text(), nullable=True),
        sa.Column("outcome", sa.Text(), nullable=True),
        sa.Column("truth_revealed", sa.Text(), nullable=True),
        sa.Column("next_edge", sa.Text(), nullable=True),
        sa.Column("completion_score", sa.Numeric(6, 3), nullable=True),
        sa.Column("subjective_after", JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="execution",
    )
    op.create_index(
        "ix_execution_traces_operator_created",
        "traces", ["operator_id", sa.text("created_at DESC")],
        schema="execution",
    )
    op.create_index(
        "ix_execution_traces_thread_created",
        "traces", ["thread_id", sa.text("created_at DESC")],
        schema="execution",
    )
    op.create_index(
        "ix_execution_traces_policy_decision_id",
        "traces", ["policy_decision_id"],
        schema="execution",
    )


def downgrade() -> None:
    op.drop_index("ix_execution_traces_policy_decision_id", table_name="traces", schema="execution")
    op.drop_index("ix_execution_traces_thread_created", table_name="traces", schema="execution")
    op.drop_index("ix_execution_traces_operator_created", table_name="traces", schema="execution")
    op.drop_table("traces", schema="execution")

    op.drop_index("ix_execution_policy_decisions_thread_id", table_name="policy_decisions", schema="execution")
    op.drop_index("ix_execution_policy_decisions_operator_created", table_name="policy_decisions", schema="execution")
    op.drop_table("policy_decisions", schema="execution")

    op.drop_index("ix_execution_reentry_artifacts_operator_id", table_name="reentry_artifacts", schema="execution")
    op.drop_index("ix_execution_reentry_artifacts_thread_created", table_name="reentry_artifacts", schema="execution")
    op.drop_constraint("fk_reentry_artifacts_superseded_by", "reentry_artifacts", schema="execution")
    op.drop_table("reentry_artifacts", schema="execution")

    op.drop_index("ix_execution_blocker_estimates_thread_id", table_name="blocker_estimates", schema="execution")
    op.drop_index("ix_execution_blocker_estimates_operator_generated", table_name="blocker_estimates", schema="execution")
    op.drop_table("blocker_estimates", schema="execution")

    op.drop_index("ix_execution_state_estimates_thread_id", table_name="state_estimates", schema="execution")
    op.drop_index("ix_execution_state_estimates_operator_generated", table_name="state_estimates", schema="execution")
    op.drop_table("state_estimates", schema="execution")
