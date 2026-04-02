"""M002: core.operators and core.devices.

Root identity tables. Every other table in the system references
core.operators via operator_id.

Matches: Utopia Formal Architecture DB etc.md section 5.

Revision ID: 002
Revises: 001
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "operators",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("display_name", sa.Text(), nullable=False),
        sa.Column("timezone", sa.Text(), nullable=False),
        sa.Column("locale", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="core",
    )

    op.create_table(
        "devices",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("device_name", sa.Text(), nullable=False),
        sa.Column("device_type", sa.Text(), nullable=False),
        sa.Column("public_key_fingerprint", sa.Text(), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="core",
    )

    # Index for device lookups by operator
    op.create_index("ix_core_devices_operator_id", "devices", ["operator_id"], schema="core")


def downgrade() -> None:
    op.drop_index("ix_core_devices_operator_id", table_name="devices", schema="core")
    op.drop_table("devices", schema="core")
    op.drop_table("operators", schema="core")
