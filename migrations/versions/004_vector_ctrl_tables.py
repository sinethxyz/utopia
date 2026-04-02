"""M004: vector_ctrl tables — the directional control plane.

Vector is not task storage. It is directional governance.
Hierarchy: life_arcs -> seasons -> missions -> threads
Plus: thread_constraints, anti_goals

Matches: Utopia Formal Architecture DB etc.md section 6.

Revision ID: 004
Revises: 003
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, JSONB

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- life_arcs: top-level directional framing ---
    op.create_table(
        "life_arcs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("active", "paused", "completed", "abandoned", "archived", "dormant",
                    name="status", schema="core", create_type=False),
            nullable=False,
        ),
        sa.Column("horizon_start", sa.Date(), nullable=True),
        sa.Column("horizon_end", sa.Date(), nullable=True),
        sa.Column("success_definition", sa.Text(), nullable=True),
        sa.Column("anti_goals", ARRAY(sa.Text()), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="vector_ctrl",
    )
    op.create_index(
        "ix_vector_ctrl_life_arcs_operator_status",
        "life_arcs", ["operator_id", "status"], schema="vector_ctrl",
    )

    # --- seasons: bounded phases of focus ---
    op.create_table(
        "seasons",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("life_arc_id", sa.Uuid(), sa.ForeignKey("vector_ctrl.life_arcs.id"), nullable=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("thesis", sa.Text(), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("priority_stack", JSONB(), nullable=False, server_default="[]"),
        sa.Column(
            "status",
            sa.Enum("planned", "active", "closed",
                    name="season_status", schema="core", create_type=False),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="vector_ctrl",
    )
    op.create_index(
        "ix_vector_ctrl_seasons_operator_status",
        "seasons", ["operator_id", "status"], schema="vector_ctrl",
    )

    # --- missions: strategically meaningful objectives ---
    op.create_table(
        "missions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("season_id", sa.Uuid(), sa.ForeignKey("vector_ctrl.seasons.id"), nullable=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "mission_kind",
            sa.Enum("strategic", "technical", "personal", "recovery", "exploratory",
                    name="mission_kind", schema="core", create_type=False),
            nullable=False,
        ),
        sa.Column("priority_score", sa.Numeric(6, 3), nullable=True),
        sa.Column(
            "status",
            sa.Enum("active", "paused", "completed", "abandoned", "archived", "dormant",
                    name="status", schema="core", create_type=False),
            nullable=False,
        ),
        sa.Column("success_definition", sa.Text(), nullable=True),
        sa.Column("failure_definition", sa.Text(), nullable=True),
        sa.Column("drift_definition", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="vector_ctrl",
    )
    op.create_index(
        "ix_vector_ctrl_missions_operator_status",
        "missions", ["operator_id", "status"], schema="vector_ctrl",
    )
    op.create_index(
        "ix_vector_ctrl_missions_season_id",
        "missions", ["season_id"], schema="vector_ctrl",
    )

    # --- threads: live lines of work within missions ---
    op.create_table(
        "threads",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("mission_id", sa.Uuid(), sa.ForeignKey("vector_ctrl.missions.id"), nullable=False),
        sa.Column("parent_thread_id", sa.Uuid(), sa.ForeignKey("vector_ctrl.threads.id"), nullable=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "thread_kind",
            sa.Enum("build", "research", "decision", "admin", "recovery",
                    name="thread_kind", schema="core", create_type=False),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("active", "blocked", "paused", "closed",
                    name="thread_status", schema="core", create_type=False),
            nullable=False,
        ),
        sa.Column("complexity_score", sa.Numeric(6, 3), nullable=True),
        sa.Column("ambiguity_score", sa.Numeric(6, 3), nullable=True),
        sa.Column("reentry_risk_score", sa.Numeric(6, 3), nullable=True),
        sa.Column("last_meaningful_touch_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_edge_summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="vector_ctrl",
    )
    op.create_index(
        "ix_vector_ctrl_threads_operator_status",
        "threads", ["operator_id", "status"], schema="vector_ctrl",
    )
    op.create_index(
        "ix_vector_ctrl_threads_mission_id",
        "threads", ["mission_id"], schema="vector_ctrl",
    )
    op.create_index(
        "ix_vector_ctrl_threads_parent_thread_id",
        "threads", ["parent_thread_id"], schema="vector_ctrl",
    )

    # --- thread_constraints: explicit constraints on a thread ---
    op.create_table(
        "thread_constraints",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("thread_id", sa.Uuid(), sa.ForeignKey("vector_ctrl.threads.id"), nullable=False),
        sa.Column("constraint_type", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "hardness",
            sa.Enum("hard", "soft", "assumed",
                    name="constraint_hardness", schema="core", create_type=False),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="vector_ctrl",
    )
    op.create_index(
        "ix_vector_ctrl_thread_constraints_thread_id",
        "thread_constraints", ["thread_id"], schema="vector_ctrl",
    )

    # --- anti_goals: what must not happen ---
    op.create_table(
        "anti_goals",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("scope_type", sa.Text(), nullable=False),
        sa.Column("scope_id", sa.Uuid(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="vector_ctrl",
    )
    op.create_index(
        "ix_vector_ctrl_anti_goals_scope",
        "anti_goals", ["scope_type", "scope_id"], schema="vector_ctrl",
    )
    op.create_index(
        "ix_vector_ctrl_anti_goals_operator_id",
        "anti_goals", ["operator_id"], schema="vector_ctrl",
    )


def downgrade() -> None:
    op.drop_index("ix_vector_ctrl_anti_goals_operator_id", table_name="anti_goals", schema="vector_ctrl")
    op.drop_index("ix_vector_ctrl_anti_goals_scope", table_name="anti_goals", schema="vector_ctrl")
    op.drop_table("anti_goals", schema="vector_ctrl")

    op.drop_index("ix_vector_ctrl_thread_constraints_thread_id", table_name="thread_constraints", schema="vector_ctrl")
    op.drop_table("thread_constraints", schema="vector_ctrl")

    op.drop_index("ix_vector_ctrl_threads_parent_thread_id", table_name="threads", schema="vector_ctrl")
    op.drop_index("ix_vector_ctrl_threads_mission_id", table_name="threads", schema="vector_ctrl")
    op.drop_index("ix_vector_ctrl_threads_operator_status", table_name="threads", schema="vector_ctrl")
    op.drop_table("threads", schema="vector_ctrl")

    op.drop_index("ix_vector_ctrl_missions_season_id", table_name="missions", schema="vector_ctrl")
    op.drop_index("ix_vector_ctrl_missions_operator_status", table_name="missions", schema="vector_ctrl")
    op.drop_table("missions", schema="vector_ctrl")

    op.drop_index("ix_vector_ctrl_seasons_operator_status", table_name="seasons", schema="vector_ctrl")
    op.drop_table("seasons", schema="vector_ctrl")

    op.drop_index("ix_vector_ctrl_life_arcs_operator_status", table_name="life_arcs", schema="vector_ctrl")
    op.drop_table("life_arcs", schema="vector_ctrl")
