"""M012: vector embeddings — semantic retrieval infrastructure.

Creates a polymorphic embeddings table in the ``vector`` schema that
stores pgvector embeddings for any entity in the system. Uses a
single table with entity_kind + entity_id to reference the source
entity, and an HNSW index for fast approximate nearest-neighbor search.

The ``vector`` schema already exists from M001.

Matches: Utopia Formal Architecture DB etc.md Vector Search section.

Revision ID: 012
Revises: 011
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

revision: str = "012"
down_revision: Union[str, None] = "011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

EMBEDDING_DIM = 1536


def upgrade() -> None:
    # --- embeddings ---
    op.create_table(
        "embeddings",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("entity_kind", sa.Text(), nullable=False),
        sa.Column("entity_id", sa.Uuid(), nullable=False),
        sa.Column("content_text", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(EMBEDDING_DIM), nullable=False),
        sa.Column("model_name", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="vector",
    )
    # Unique constraint: one embedding per entity
    op.create_index(
        "ix_vector_embeddings_entity",
        "embeddings", ["entity_kind", "entity_id"],
        unique=True,
        schema="vector",
    )
    op.create_index(
        "ix_vector_embeddings_operator",
        "embeddings", ["operator_id"],
        schema="vector",
    )
    # HNSW index for cosine similarity search
    op.execute(
        "CREATE INDEX ix_vector_embeddings_hnsw ON vector.embeddings "
        "USING hnsw (embedding vector_cosine_ops) "
        "WITH (m = 16, ef_construction = 64)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS vector.ix_vector_embeddings_hnsw")
    op.drop_index("ix_vector_embeddings_operator", table_name="embeddings", schema="vector")
    op.drop_index("ix_vector_embeddings_entity", table_name="embeddings", schema="vector")
    op.drop_table("embeddings", schema="vector")
