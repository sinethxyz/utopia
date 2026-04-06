"""OpenAI embeddings provider.

Uses httpx to call the OpenAI embeddings API. This avoids adding
the full openai SDK as a dependency since httpx is already available.
"""

from __future__ import annotations

import logging

import httpx

from utopia.config import settings

logger = logging.getLogger(__name__)

EMBEDDINGS_URL = "https://api.openai.com/v1/embeddings"


async def generate_embedding(
    text: str,
    *,
    model: str | None = None,
) -> list[float]:
    """Generate an embedding vector for the given text.

    Args:
        text: The text to embed.
        model: Optional model override. Defaults to settings.embedding_model.

    Returns:
        List of floats representing the embedding vector.

    Raises:
        httpx.HTTPStatusError: If the API returns an error.
    """
    model = model or settings.embedding_model

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            EMBEDDINGS_URL,
            headers={
                "Authorization": f"Bearer {settings.openai_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "input": text,
                "model": model,
            },
        )
        response.raise_for_status()

    data = response.json()
    embedding = data["data"][0]["embedding"]

    logger.debug(
        "Generated embedding: model=%s dimensions=%d",
        model, len(embedding),
    )

    return embedding


async def generate_embeddings_batch(
    texts: list[str],
    *,
    model: str | None = None,
) -> list[list[float]]:
    """Generate embeddings for multiple texts in a single API call.

    Args:
        texts: List of texts to embed.
        model: Optional model override.

    Returns:
        List of embedding vectors, one per input text, in order.
    """
    model = model or settings.embedding_model

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            EMBEDDINGS_URL,
            headers={
                "Authorization": f"Bearer {settings.openai_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "input": texts,
                "model": model,
            },
        )
        response.raise_for_status()

    data = response.json()
    # Sort by index to ensure order matches input
    sorted_data = sorted(data["data"], key=lambda x: x["index"])
    embeddings = [item["embedding"] for item in sorted_data]

    logger.info(
        "Generated %d embeddings: model=%s dimensions=%d",
        len(embeddings), model, len(embeddings[0]) if embeddings else 0,
    )

    return embeddings
