"""M003: integration.oauth_connections, integration.permissions, integration.webhook_receipts.

External integration infrastructure. Required before physiology (WHOOP)
because whoop_connections references oauth_connections.

Matches: Utopia Formal Architecture DB etc.md sections 5 and 8.

Revision ID: 003
Revises: 002
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, BYTEA, JSONB

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- oauth_connections ---
    op.create_table(
        "oauth_connections",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("provider", sa.Text(), nullable=False),
        sa.Column("provider_user_id", sa.Text(), nullable=True),
        sa.Column("scopes", ARRAY(sa.Text()), nullable=False, server_default="{}"),
        sa.Column(
            "status",
            sa.Enum("active", "revoked", "expired", name="oauth_status", schema="core", create_type=False),
            nullable=False,
        ),
        sa.Column("encrypted_access_token", BYTEA(), nullable=True),
        sa.Column("encrypted_refresh_token", BYTEA(), nullable=True),
        sa.Column("token_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="integration",
    )
    op.create_index(
        "ix_integration_oauth_connections_operator_id",
        "oauth_connections", ["operator_id"], schema="integration",
    )

    # --- permissions ---
    op.create_table(
        "permissions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("provider", sa.Text(), nullable=False),
        sa.Column("permission_key", sa.Text(), nullable=False),
        sa.Column("granted", sa.Boolean(), nullable=False),
        sa.Column("granted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("details", JSONB(), nullable=False, server_default="{}"),
        schema="integration",
    )
    op.create_index(
        "ix_integration_permissions_operator_provider",
        "permissions", ["operator_id", "provider"], schema="integration",
    )

    # --- webhook_receipts ---
    op.create_table(
        "webhook_receipts",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("provider", sa.Text(), nullable=False),
        sa.Column("event_type", sa.Text(), nullable=False),
        sa.Column("provider_user_id", sa.Text(), nullable=True),
        sa.Column("provider_object_id", sa.Text(), nullable=True),
        sa.Column("trace_id", sa.Text(), nullable=True),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("signature_valid", sa.Boolean(), nullable=True),
        sa.Column("headers", JSONB(), nullable=False),
        sa.Column("raw_body", JSONB(), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "processing_status",
            sa.Enum("pending", "processed", "failed", name="processing_status", schema="core", create_type=False),
            nullable=False,
            server_default="pending",
        ),
        schema="integration",
    )
    op.create_index(
        "ix_integration_webhook_receipts_status_received",
        "webhook_receipts", ["processing_status", "received_at"], schema="integration",
    )
    op.create_index(
        "ix_integration_webhook_receipts_event_type",
        "webhook_receipts", ["event_type", "received_at"], schema="integration",
    )


def downgrade() -> None:
    op.drop_index("ix_integration_webhook_receipts_event_type", table_name="webhook_receipts", schema="integration")
    op.drop_index("ix_integration_webhook_receipts_status_received", table_name="webhook_receipts", schema="integration")
    op.drop_table("webhook_receipts", schema="integration")

    op.drop_index("ix_integration_permissions_operator_provider", table_name="permissions", schema="integration")
    op.drop_table("permissions", schema="integration")

    op.drop_index("ix_integration_oauth_connections_operator_id", table_name="oauth_connections", schema="integration")
    op.drop_table("oauth_connections", schema="integration")
