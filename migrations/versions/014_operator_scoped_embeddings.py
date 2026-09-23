"""M014: scope vector embedding identity by operator.

Revision ID: 014
Revises: 013
"""
from collections.abc import Sequence

from alembic import op

revision: str = "014"
down_revision: str | None = "013"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_index(
        "ix_vector_embeddings_entity",
        table_name="embeddings",
        schema="vector",
    )
    op.create_index(
        "ix_vector_embeddings_entity",
        "embeddings",
        ["operator_id", "entity_kind", "entity_id"],
        unique=True,
        schema="vector",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_vector_embeddings_entity",
        table_name="embeddings",
        schema="vector",
    )
    op.create_index(
        "ix_vector_embeddings_entity",
        "embeddings",
        ["entity_kind", "entity_id"],
        unique=True,
        schema="vector",
    )
