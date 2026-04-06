"""Context Retriever — RAG over the Aether knowledge graph.

Given a query (from the operator, a problem, or another AI module),
retrieves relevant knowledge from Aether via vector search, then
synthesizes the results into a coherent context package that downstream
modules can consume.

This is the knowledge access layer of the AI Fabric.
"""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass, field

from utopia.ai.providers import claude
from utopia.services.vector_search_service import VectorSearchService

logger = logging.getLogger(__name__)

SYNTHESIS_PROMPT = """\
You are the Context Retriever inside Utopia, a private cognitive operating system.

Your job: given a query and retrieved knowledge fragments, synthesize a context package that helps downstream reasoning modules make better decisions.

## Rules

1. Prioritize relevance over completeness. Only include fragments that directly inform the query.
2. Flag contradictions between fragments — they are valuable signals.
3. Separate facts from heuristics from opinions.
4. If the retrieved fragments don't contain relevant knowledge, say so clearly.
5. Note the confidence/source quality of each fragment.

## Output Format

Respond with ONLY a JSON object (no markdown, no explanation):
{
  "relevant_knowledge": [
    {"entity_kind": "<type>", "content": "<summary>", "relevance": "<why this matters>", "confidence": <0.0-1.0>}
  ],
  "synthesis": "<1-3 sentence summary of what the knowledge says about the query>",
  "contradictions": ["<any contradictions between fragments>"],
  "knowledge_gaps": ["<what we don't have knowledge about that would help>"],
  "confidence": <0.0 to 1.0>
}
"""


@dataclass
class RetrievalResult:
    """Output of the context retrieval pipeline."""

    relevant_knowledge: list[dict] = field(default_factory=list)
    synthesis: str = ""
    contradictions: list[str] = field(default_factory=list)
    knowledge_gaps: list[str] = field(default_factory=list)
    confidence: float = 0.0
    raw_results_count: int = 0
    model_usage: dict = field(default_factory=dict)


async def retrieve_context(
    vector_search_svc: VectorSearchService,
    query: str,
    *,
    operator_id: uuid.UUID | None = None,
    entity_kinds: list[str] | None = None,
    top_k: int = 10,
    synthesize: bool = True,
) -> RetrievalResult:
    """Retrieve and synthesize relevant knowledge for a query.

    Args:
        vector_search_svc: The vector search service for semantic retrieval.
        query: Natural language query to search for.
        operator_id: Optional filter by operator.
        entity_kinds: Optional filter to specific Aether entity types.
        top_k: Number of raw results to retrieve.
        synthesize: Whether to run Claude synthesis on results (set False for raw search).

    Returns:
        RetrievalResult with synthesized knowledge and metadata.
    """
    result = RetrievalResult()

    # 1. Semantic search over Aether embeddings
    search_results = await vector_search_svc.search(
        query,
        operator_id=operator_id,
        entity_kinds=entity_kinds,
        top_k=top_k,
    )

    result.raw_results_count = len(search_results)

    if not search_results:
        result.synthesis = "No relevant knowledge found in Aether."
        result.knowledge_gaps = [query]
        return result

    if not synthesize:
        result.relevant_knowledge = [
            {
                "entity_kind": r.entity_kind,
                "content": r.content_text,
                "similarity": r.similarity,
            }
            for r in search_results
        ]
        result.confidence = search_results[0].similarity if search_results else 0.0
        return result

    # 2. Synthesize with Claude
    fragments = [
        {
            "entity_kind": r.entity_kind,
            "content": r.content_text[:500],
            "similarity": round(r.similarity, 3),
        }
        for r in search_results
    ]

    user_message = (
        f"Query: {query}\n\n"
        f"Retrieved knowledge fragments:\n{json.dumps(fragments, indent=2, default=str)}"
    )

    text, usage = await claude.complete(
        system=SYNTHESIS_PROMPT,
        user=user_message,
        max_tokens=768,
    )
    result.model_usage = usage

    parsed = _parse_response(text)
    result.relevant_knowledge = parsed["relevant_knowledge"]
    result.synthesis = parsed["synthesis"]
    result.contradictions = parsed["contradictions"]
    result.knowledge_gaps = parsed["knowledge_gaps"]
    result.confidence = parsed["confidence"]

    return result


def _parse_response(text: str) -> dict:
    """Parse the JSON response from Claude, with fallback."""
    try:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
            cleaned = cleaned.rsplit("```", 1)[0]
        data = json.loads(cleaned)
    except (json.JSONDecodeError, IndexError):
        logger.warning("Failed to parse context retriever response: %s", text[:200])
        data = {
            "relevant_knowledge": [],
            "synthesis": "Could not synthesize — parse failure.",
            "contradictions": [],
            "knowledge_gaps": [],
            "confidence": 0.2,
        }

    return {
        "relevant_knowledge": data.get("relevant_knowledge", []),
        "synthesis": data.get("synthesis", ""),
        "contradictions": data.get("contradictions", []),
        "knowledge_gaps": data.get("knowledge_gaps", []),
        "confidence": min(max(float(data.get("confidence", 0.5)), 0.0), 1.0),
    }
