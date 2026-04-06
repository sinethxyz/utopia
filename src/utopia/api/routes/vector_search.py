"""Vector search routes — embedding management and semantic retrieval."""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from utopia.api.deps import get_vector_search_service
from utopia.services.vector_search_service import VectorSearchService

router = APIRouter(prefix="/vector-search", tags=["vector-search"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class EmbedRequest(BaseModel):
    operator_id: uuid.UUID
    entity_kind: str
    entity_id: uuid.UUID
    content_text: str


class EmbedBatchRequest(BaseModel):
    operator_id: uuid.UUID
    entities: list[EmbedRequest]


class EmbeddingRead(BaseModel):
    id: uuid.UUID
    operator_id: uuid.UUID
    entity_kind: str
    entity_id: uuid.UUID
    content_text: str
    model_name: str


class SearchRequest(BaseModel):
    query: str
    operator_id: uuid.UUID | None = None
    entity_kinds: list[str] | None = None
    top_k: int = Field(default=10, ge=1, le=100)


class SearchResultRead(BaseModel):
    entity_kind: str
    entity_id: uuid.UUID
    content_text: str
    similarity: float


class SimilarRequest(BaseModel):
    entity_kind: str
    entity_id: uuid.UUID
    top_k: int = Field(default=5, ge=1, le=50)


# ---------------------------------------------------------------------------
# Embed endpoints
# ---------------------------------------------------------------------------

@router.post("/embed", response_model=EmbeddingRead, status_code=201)
async def embed_entity(
    data: EmbedRequest,
    svc: VectorSearchService = Depends(get_vector_search_service),
) -> EmbeddingRead:
    """Generate and store an embedding for a single entity."""
    emb = await svc.embed_entity(
        data.operator_id, data.entity_kind, data.entity_id, data.content_text
    )
    await svc.commit()
    return EmbeddingRead(
        id=emb.id,
        operator_id=emb.operator_id,
        entity_kind=emb.entity_kind,
        entity_id=emb.entity_id,
        content_text=emb.content_text,
        model_name=emb.model_name,
    )


@router.post("/embed/batch", response_model=list[EmbeddingRead], status_code=201)
async def embed_batch(
    data: EmbedBatchRequest,
    svc: VectorSearchService = Depends(get_vector_search_service),
) -> list[EmbeddingRead]:
    """Generate and store embeddings for multiple entities."""
    entities = [
        {
            "entity_kind": e.entity_kind,
            "entity_id": e.entity_id,
            "content_text": e.content_text,
        }
        for e in data.entities
    ]
    results = await svc.embed_entities_batch(data.operator_id, entities)
    await svc.commit()
    return [
        EmbeddingRead(
            id=emb.id,
            operator_id=emb.operator_id,
            entity_kind=emb.entity_kind,
            entity_id=emb.entity_id,
            content_text=emb.content_text,
            model_name=emb.model_name,
        )
        for emb in results
    ]


# ---------------------------------------------------------------------------
# Search endpoints
# ---------------------------------------------------------------------------

@router.post("/search", response_model=list[SearchResultRead])
async def search(
    data: SearchRequest,
    svc: VectorSearchService = Depends(get_vector_search_service),
) -> list[SearchResultRead]:
    """Perform semantic search across all embedded entities."""
    results = await svc.search(
        data.query,
        operator_id=data.operator_id,
        entity_kinds=data.entity_kinds,
        top_k=data.top_k,
    )
    return [
        SearchResultRead(
            entity_kind=r.entity_kind,
            entity_id=r.entity_id,
            content_text=r.content_text,
            similarity=r.similarity,
        )
        for r in results
    ]


@router.post("/similar", response_model=list[SearchResultRead])
async def find_similar(
    data: SimilarRequest,
    svc: VectorSearchService = Depends(get_vector_search_service),
) -> list[SearchResultRead]:
    """Find entities similar to a given entity."""
    results = await svc.find_similar(
        data.entity_kind, data.entity_id, top_k=data.top_k
    )
    return [
        SearchResultRead(
            entity_kind=r.entity_kind,
            entity_id=r.entity_id,
            content_text=r.content_text,
            similarity=r.similarity,
        )
        for r in results
    ]
