"""Embedding ORM model — vector storage for semantic retrieval.

A single polymorphic table stores embeddings for any entity in
the system. entity_kind + entity_id identify the source entity,
content_hash enables skip-if-unchanged logic, and the pgvector
column supports HNSW-indexed nearest-neighbor search.
"""

import datetime
import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, ForeignKey, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from utopia.config import settings
from utopia.db import Base

EMBEDDING_DIM = settings.embedding_dimensions


class Embedding(Base):
    """A vector embedding for any entity in the system."""

    __tablename__ = "embeddings"
    __table_args__ = {"schema": "vector"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("core.operators.id"), nullable=False
    )
    entity_kind: Mapped[str] = mapped_column(Text, nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    content_text: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list] = mapped_column(Vector(EMBEDDING_DIM), nullable=False)
    model_name: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
