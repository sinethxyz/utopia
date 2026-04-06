"""M011: system audit tables — AI orchestration and audit trail.

The System layer records every AI model invocation, retrieval run,
and significant system event. It provides the audit trail needed to
debug reasoning chains, replay decisions, and monitor costs.

The ``system`` schema already exists from M001.

Matches: Utopia Formal Architecture DB etc.md System Audit section.

Revision ID: 011
Revises: 010
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "011"
down_revision: Union[str, None] = "010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- model_providers ---
    op.create_table(
        "model_providers",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("provider_kind", sa.Text(), nullable=False),
        sa.Column("api_base_url", sa.Text(), nullable=True),
        sa.Column("default_model", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("config", JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="system",
    )
    op.create_index(
        "ix_system_model_providers_name",
        "model_providers", ["name"],
        unique=True,
        schema="system",
    )

    # --- model_runs ---
    op.create_table(
        "model_runs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("provider_id", sa.Uuid(), sa.ForeignKey("system.model_providers.id"), nullable=False),
        sa.Column("model_name", sa.Text(), nullable=False),
        sa.Column("module_name", sa.Text(), nullable=False),
        sa.Column("prompt_tokens", sa.Integer(), nullable=True),
        sa.Column("completion_tokens", sa.Integer(), nullable=True),
        sa.Column("total_tokens", sa.Integer(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("input_summary", JSONB(), nullable=False, server_default="{}"),
        sa.Column("output_summary", JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="system",
    )
    op.create_index(
        "ix_system_model_runs_operator_created",
        "model_runs", ["operator_id", sa.text("created_at DESC")],
        schema="system",
    )
    op.create_index(
        "ix_system_model_runs_provider_id",
        "model_runs", ["provider_id"],
        schema="system",
    )
    op.create_index(
        "ix_system_model_runs_module_name",
        "model_runs", ["module_name"],
        schema="system",
    )

    # --- retrieval_runs ---
    op.create_table(
        "retrieval_runs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("model_run_id", sa.Uuid(), sa.ForeignKey("system.model_runs.id"), nullable=True),
        sa.Column("collection", sa.Text(), nullable=False),
        sa.Column("query_text", sa.Text(), nullable=True),
        sa.Column("query_vector_dim", sa.Integer(), nullable=True),
        sa.Column("top_k", sa.Integer(), nullable=False),
        sa.Column("results_returned", sa.Integer(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("filter_criteria", JSONB(), nullable=False, server_default="{}"),
        sa.Column("result_ids", JSONB(), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="system",
    )
    op.create_index(
        "ix_system_retrieval_runs_operator_created",
        "retrieval_runs", ["operator_id", sa.text("created_at DESC")],
        schema="system",
    )
    op.create_index(
        "ix_system_retrieval_runs_model_run_id",
        "retrieval_runs", ["model_run_id"],
        schema="system",
    )

    # --- event_log ---
    op.create_table(
        "event_log",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=True),
        sa.Column("event_type", sa.Text(), nullable=False),
        sa.Column("source", sa.Text(), nullable=False),
        sa.Column("severity", sa.Text(), nullable=False, server_default="info"),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("payload", JSONB(), nullable=False, server_default="{}"),
        sa.Column("related_entity_kind", sa.Text(), nullable=True),
        sa.Column("related_entity_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="system",
    )
    op.create_index(
        "ix_system_event_log_created",
        "event_log", [sa.text("created_at DESC")],
        schema="system",
    )
    op.create_index(
        "ix_system_event_log_type",
        "event_log", ["event_type"],
        schema="system",
    )
    op.create_index(
        "ix_system_event_log_severity",
        "event_log", ["severity"],
        schema="system",
    )
    op.create_index(
        "ix_system_event_log_related",
        "event_log", ["related_entity_kind", "related_entity_id"],
        schema="system",
    )

    # --- outbox_events ---
    op.create_table(
        "outbox_events",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=True),
        sa.Column("event_type", sa.Text(), nullable=False),
        sa.Column("destination", sa.Text(), nullable=False),
        sa.Column("payload", JSONB(), nullable=False, server_default="{}"),
        sa.Column("status", sa.Enum("pending", "processed", "failed", name="processing_status", schema="core", create_type=False), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        schema="system",
    )
    op.create_index(
        "ix_system_outbox_events_status",
        "outbox_events", ["status"],
        schema="system",
    )
    op.create_index(
        "ix_system_outbox_events_created",
        "outbox_events", [sa.text("created_at DESC")],
        schema="system",
    )


def downgrade() -> None:
    op.drop_index("ix_system_outbox_events_created", table_name="outbox_events", schema="system")
    op.drop_index("ix_system_outbox_events_status", table_name="outbox_events", schema="system")
    op.drop_table("outbox_events", schema="system")

    op.drop_index("ix_system_event_log_related", table_name="event_log", schema="system")
    op.drop_index("ix_system_event_log_severity", table_name="event_log", schema="system")
    op.drop_index("ix_system_event_log_type", table_name="event_log", schema="system")
    op.drop_index("ix_system_event_log_created", table_name="event_log", schema="system")
    op.drop_table("event_log", schema="system")

    op.drop_index("ix_system_retrieval_runs_model_run_id", table_name="retrieval_runs", schema="system")
    op.drop_index("ix_system_retrieval_runs_operator_created", table_name="retrieval_runs", schema="system")
    op.drop_table("retrieval_runs", schema="system")

    op.drop_index("ix_system_model_runs_module_name", table_name="model_runs", schema="system")
    op.drop_index("ix_system_model_runs_provider_id", table_name="model_runs", schema="system")
    op.drop_index("ix_system_model_runs_operator_created", table_name="model_runs", schema="system")
    op.drop_table("model_runs", schema="system")

    op.drop_index("ix_system_model_providers_name", table_name="model_providers", schema="system")
    op.drop_table("model_providers", schema="system")
