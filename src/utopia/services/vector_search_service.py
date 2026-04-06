"""VectorSearchService — embedding storage and semantic retrieval.

Generates embeddings for Aether entities, stores them in the vector
schema, and provides semantic search via pgvector HNSW index.
"""

from __future__ import annotations

import hashlib
import logging
import uuid as _uuid
from dataclasses import dataclass

from sqlalchemy import delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from uuid_utils import uuid7

from utopia.ai.providers import openai_embeddings
from utopia.config import settings
from utopia.models.embedding import Embedding

logger = logging.getLogger(__name__)

# Entity kinds that can be embedded
EMBEDDABLE_KINDS = {
    "source", "source_chunk", "extraction", "concept", "mechanism",
    "tradeoff", "failure_mode", "heuristic", "diagnostic_question",
    "protocol", "lens_pack", "case", "rule", "pattern",
}


@dataclass
class SearchResult:
    """A single semantic search result."""

    entity_kind: str
    entity_id: _uuid.UUID
    content_text: str
    similarity: float


class VectorSearchService:
    """Service for embedding storage and semantic retrieval."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def commit(self) -> None:
        await self._session.commit()

    # ------------------------------------------------------------------
    # Embedding management
    # ------------------------------------------------------------------

    async def embed_entity(
        self,
        operator_id: _uuid.UUID,
        entity_kind: str,
        entity_id: _uuid.UUID,
        content_text: str,
    ) -> Embedding:
        """Generate and store an embedding for an entity.

        If an embedding already exists and the content hasn't changed
        (same content_hash), it is returned as-is. Otherwise, a new
        embedding is generated and the old one is replaced.

        Args:
            operator_id: The operator who owns this entity.
            entity_kind: Type of entity (e.g., "concept", "rule").
            entity_id: UUID of the source entity.
            content_text: The text content to embed.

        Returns:
            The Embedding record (new or existing).
        """
        content_hash = _hash_content(content_text)

        # Check for existing embedding with same hash
        stmt = (
            select(Embedding)
            .where(Embedding.entity_kind == entity_kind)
            .where(Embedding.entity_id == entity_id)
        )
        result = await self._session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing and existing.content_hash == content_hash:
            logger.debug("Embedding unchanged for %s:%s", entity_kind, entity_id)
            return existing

        # Generate new embedding
        vector = await openai_embeddings.generate_embedding(content_text)

        if existing:
            # Update in place
            existing.content_text = content_text
            existing.content_hash = content_hash
            existing.embedding = vector
            existing.model_name = settings.embedding_model
            await self._session.flush()
            logger.info("Updated embedding for %s:%s", entity_kind, entity_id)
            return existing

        # Create new
        emb = Embedding(
            id=uuid7(),
            operator_id=operator_id,
            entity_kind=entity_kind,
            entity_id=entity_id,
            content_text=content_text,
            content_hash=content_hash,
            embedding=vector,
            model_name=settings.embedding_model,
        )
        self._session.add(emb)
        await self._session.flush()
        logger.info("Created embedding for %s:%s", entity_kind, entity_id)
        return emb

    async def embed_entities_batch(
        self,
        operator_id: _uuid.UUID,
        entities: list[dict],
    ) -> list[Embedding]:
        """Generate and store embeddings for multiple entities.

        Each entity dict must have: entity_kind, entity_id, content_text.

        Skips entities whose content hasn't changed.
        """
        # Separate new/changed from unchanged
        to_embed: list[dict] = []
        unchanged: list[Embedding] = []

        for entity in entities:
            content_hash = _hash_content(entity["content_text"])
            stmt = (
                select(Embedding)
                .where(Embedding.entity_kind == entity["entity_kind"])
                .where(Embedding.entity_id == entity["entity_id"])
            )
            result = await self._session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing and existing.content_hash == content_hash:
                unchanged.append(existing)
            else:
                to_embed.append({**entity, "content_hash": content_hash, "existing": existing})

        if not to_embed:
            return unchanged

        # Batch generate embeddings
        texts = [e["content_text"] for e in to_embed]
        vectors = await openai_embeddings.generate_embeddings_batch(texts)

        results = list(unchanged)
        for entity_data, vector in zip(to_embed, vectors):
            existing = entity_data.get("existing")
            if existing:
                existing.content_text = entity_data["content_text"]
                existing.content_hash = entity_data["content_hash"]
                existing.embedding = vector
                existing.model_name = settings.embedding_model
                await self._session.flush()
                results.append(existing)
            else:
                emb = Embedding(
                    id=uuid7(),
                    operator_id=operator_id,
                    entity_kind=entity_data["entity_kind"],
                    entity_id=entity_data["entity_id"],
                    content_text=entity_data["content_text"],
                    content_hash=entity_data["content_hash"],
                    embedding=vector,
                    model_name=settings.embedding_model,
                )
                self._session.add(emb)
                await self._session.flush()
                results.append(emb)

        logger.info(
            "Batch embedded %d entities (%d new/updated, %d unchanged)",
            len(entities), len(to_embed), len(unchanged),
        )
        return results

    async def delete_embedding(
        self, entity_kind: str, entity_id: _uuid.UUID
    ) -> None:
        """Delete an embedding for an entity."""
        stmt = (
            delete(Embedding)
            .where(Embedding.entity_kind == entity_kind)
            .where(Embedding.entity_id == entity_id)
        )
        await self._session.execute(stmt)

    # ------------------------------------------------------------------
    # Semantic search
    # ------------------------------------------------------------------

    async def search(
        self,
        query: str,
        *,
        operator_id: _uuid.UUID | None = None,
        entity_kinds: list[str] | None = None,
        top_k: int = 10,
    ) -> list[SearchResult]:
        """Perform semantic search using cosine similarity.

        Args:
            query: The natural language search query.
            operator_id: Optional filter by operator.
            entity_kinds: Optional filter to specific entity types.
            top_k: Number of results to return.

        Returns:
            List of SearchResult ordered by similarity (highest first).
        """
        query_vector = await openai_embeddings.generate_embedding(query)

        # Build the query using pgvector's cosine distance operator
        # 1 - cosine_distance = cosine_similarity
        vector_literal = f"[{','.join(str(v) for v in query_vector)}]"

        filters = []
        params: dict = {"top_k": top_k}

        if operator_id is not None:
            filters.append("operator_id = :operator_id")
            params["operator_id"] = str(operator_id)

        if entity_kinds:
            placeholders = ", ".join(f":ek_{i}" for i in range(len(entity_kinds)))
            filters.append(f"entity_kind IN ({placeholders})")
            for i, ek in enumerate(entity_kinds):
                params[f"ek_{i}"] = ek

        where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""

        sql = f"""
            SELECT
                entity_kind,
                entity_id,
                content_text,
                1 - (embedding <=> '{vector_literal}'::vector) AS similarity
            FROM vector.embeddings
            {where_clause}
            ORDER BY embedding <=> '{vector_literal}'::vector
            LIMIT :top_k
        """

        result = await self._session.execute(text(sql), params)
        rows = result.fetchall()

        return [
            SearchResult(
                entity_kind=row[0],
                entity_id=row[1],
                content_text=row[2],
                similarity=float(row[3]),
            )
            for row in rows
        ]

    async def find_similar(
        self,
        entity_kind: str,
        entity_id: _uuid.UUID,
        *,
        top_k: int = 5,
    ) -> list[SearchResult]:
        """Find entities similar to a given entity.

        Uses the entity's stored embedding for the search.
        Excludes the source entity from results.
        """
        # Get the entity's embedding
        stmt = (
            select(Embedding)
            .where(Embedding.entity_kind == entity_kind)
            .where(Embedding.entity_id == entity_id)
        )
        result = await self._session.execute(stmt)
        source = result.scalar_one_or_none()

        if source is None:
            return []

        vector_literal = f"[{','.join(str(v) for v in source.embedding)}]"

        sql = f"""
            SELECT
                entity_kind,
                entity_id,
                content_text,
                1 - (embedding <=> '{vector_literal}'::vector) AS similarity
            FROM vector.embeddings
            WHERE NOT (entity_kind = :src_kind AND entity_id = :src_id)
            ORDER BY embedding <=> '{vector_literal}'::vector
            LIMIT :top_k
        """

        result = await self._session.execute(
            text(sql),
            {"src_kind": entity_kind, "src_id": str(entity_id), "top_k": top_k},
        )
        rows = result.fetchall()

        return [
            SearchResult(
                entity_kind=row[0],
                entity_id=row[1],
                content_text=row[2],
                similarity=float(row[3]),
            )
            for row in rows
        ]


def _hash_content(content: str) -> str:
    """SHA-256 hash of content for change detection."""
    return hashlib.sha256(content.encode()).hexdigest()[:16]
