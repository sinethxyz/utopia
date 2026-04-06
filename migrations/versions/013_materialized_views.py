"""M013: materialized views — current state, active focus, thread priority.

Creates three materialized views that provide fast access to commonly
queried aggregated state. These views are refreshed periodically or
after significant state changes.

- mv_current_state: Latest state estimate, blocker, and policy per operator
- mv_active_focus: Active season, mission, and top threads per operator
- mv_thread_priority: Thread priority ranking based on decay, urgency, and reentry risk

Revision ID: 013
Revises: 012
"""
from typing import Sequence, Union

from alembic import op

revision: str = "013"
down_revision: Union[str, None] = "012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- mv_current_state ---
    # Combines the latest state estimate, blocker estimate, and policy
    # decision for each operator into a single row.
    op.execute("""
        CREATE MATERIALIZED VIEW execution.mv_current_state AS
        SELECT
            o.id AS operator_id,
            o.display_name,
            se.id AS state_estimate_id,
            se.state_kind,
            se.confidence AS state_confidence,
            se.generated_at AS state_generated_at,
            be.id AS blocker_estimate_id,
            be.blocker_kind,
            be.confidence AS blocker_confidence,
            pd.id AS policy_decision_id,
            pd.intervention_kind,
            pd.action_depth,
            pd.next_move,
            pd.created_at AS policy_created_at
        FROM core.operators o
        LEFT JOIN LATERAL (
            SELECT * FROM execution.state_estimates
            WHERE operator_id = o.id
            ORDER BY generated_at DESC LIMIT 1
        ) se ON true
        LEFT JOIN LATERAL (
            SELECT * FROM execution.blocker_estimates
            WHERE operator_id = o.id
            ORDER BY generated_at DESC LIMIT 1
        ) be ON true
        LEFT JOIN LATERAL (
            SELECT * FROM execution.policy_decisions
            WHERE operator_id = o.id
            ORDER BY created_at DESC LIMIT 1
        ) pd ON true
    """)
    op.execute(
        "CREATE UNIQUE INDEX ix_mv_current_state_operator "
        "ON execution.mv_current_state (operator_id)"
    )

    # --- mv_active_focus ---
    # Shows the active season, its top-priority mission, and the active
    # thread within that mission for each operator.
    op.execute("""
        CREATE MATERIALIZED VIEW vector_ctrl.mv_active_focus AS
        SELECT
            o.id AS operator_id,
            s.id AS season_id,
            s.title AS season_title,
            s.thesis AS season_thesis,
            s.start_date AS season_start,
            s.end_date AS season_end,
            m.id AS mission_id,
            m.title AS mission_title,
            m.mission_kind,
            m.priority_score AS mission_priority,
            t.id AS thread_id,
            t.title AS thread_title,
            t.thread_kind,
            t.status AS thread_status,
            t.last_meaningful_touch_at,
            t.next_edge_summary
        FROM core.operators o
        LEFT JOIN LATERAL (
            SELECT * FROM vector_ctrl.seasons
            WHERE operator_id = o.id AND status = 'active'
            ORDER BY start_date DESC LIMIT 1
        ) s ON true
        LEFT JOIN LATERAL (
            SELECT * FROM vector_ctrl.missions
            WHERE operator_id = o.id
              AND season_id = s.id
              AND status = 'active'
            ORDER BY priority_score DESC NULLS LAST LIMIT 1
        ) m ON s.id IS NOT NULL
        LEFT JOIN LATERAL (
            SELECT * FROM vector_ctrl.threads
            WHERE operator_id = o.id
              AND mission_id = m.id
              AND status = 'active'
            ORDER BY last_meaningful_touch_at DESC NULLS LAST LIMIT 1
        ) t ON m.id IS NOT NULL
    """)
    op.execute(
        "CREATE UNIQUE INDEX ix_mv_active_focus_operator "
        "ON vector_ctrl.mv_active_focus (operator_id)"
    )

    # --- mv_thread_priority ---
    # Ranks all active threads by a composite priority score that accounts
    # for mission priority, thread decay (hours since last touch), reentry
    # risk, ambiguity, and complexity.
    op.execute("""
        CREATE MATERIALIZED VIEW vector_ctrl.mv_thread_priority AS
        SELECT
            t.id AS thread_id,
            t.operator_id,
            t.mission_id,
            t.title AS thread_title,
            t.thread_kind,
            t.status AS thread_status,
            t.complexity_score,
            t.ambiguity_score,
            t.reentry_risk_score,
            t.last_meaningful_touch_at,
            t.next_edge_summary,
            m.title AS mission_title,
            m.priority_score AS mission_priority,
            EXTRACT(EPOCH FROM (now() - t.last_meaningful_touch_at)) / 3600.0
                AS hours_since_touch,
            COALESCE(m.priority_score, 0) * 10
                + COALESCE(t.reentry_risk_score, 0) * 5
                + LEAST(
                    EXTRACT(EPOCH FROM (now() - COALESCE(t.last_meaningful_touch_at, t.created_at))) / 3600.0,
                    168
                  )
                - COALESCE(t.ambiguity_score, 0) * 3
                AS priority_rank
        FROM vector_ctrl.threads t
        JOIN vector_ctrl.missions m ON t.mission_id = m.id
        WHERE t.status = 'active'
        ORDER BY priority_rank DESC
    """)
    op.execute(
        "CREATE UNIQUE INDEX ix_mv_thread_priority_thread "
        "ON vector_ctrl.mv_thread_priority (thread_id)"
    )
    op.execute(
        "CREATE INDEX ix_mv_thread_priority_operator "
        "ON vector_ctrl.mv_thread_priority (operator_id, priority_rank DESC)"
    )


def downgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW IF EXISTS vector_ctrl.mv_thread_priority CASCADE")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS vector_ctrl.mv_active_focus CASCADE")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS execution.mv_current_state CASCADE")
