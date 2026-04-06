"""Problem Structurer — decomposes raw problems into structured reasoning artifacts.

Takes the operator's raw problem description and produces a ProblemStructure:
objective, stakes, actors, incentives, constraints, assumptions, unknowns,
irreversibilities, bottlenecks, observable facts, narrative layer, and
distortion candidates.

This is the entry point to the Reasoning layer's AI pipeline.
"""

from __future__ import annotations

import json
import logging
import uuid
from decimal import Decimal

from utopia.ai.providers import claude
from utopia.schemas.reasoning import ProblemStructureCreate

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are the Problem Structurer inside Utopia, a private cognitive operating system.

Your job: take a raw problem description and decompose it into a structured analysis. The operator often cannot see the full shape of their problem. Your job is to expose it.

## Output Fields

- objective: What the operator is actually trying to achieve (may differ from what they said).
- stakes: What is at risk if this goes wrong — be specific and honest.
- actors: People, systems, or forces involved. Include the operator themselves.
- incentives: What each actor wants and why they behave as they do.
- constraints: Hard limits (time, money, skills, dependencies, legal).
- assumptions: Things the operator is taking for granted that may not be true.
- unknowns: What we don't know that would change the answer if we did.
- irreversibilities: Actions that cannot be undone — these need extra scrutiny.
- bottlenecks: The single point that gates progress right now.
- observable_facts: What is objectively true, verifiable, not narrative.
- narrative_layer: Stories the operator is telling themselves about this problem.
- distortion_candidates: Ways the operator's current state might be distorting their perception.

## Rules

1. Separate facts from narrative ruthlessly. Most problems contain both.
2. If the operator's stated objective seems misaligned with their actual behavior, flag it.
3. Unknowns are not the same as risks. Unknowns are information gaps.
4. Distortion candidates should reference the operator's current state if available.
5. Be concrete. "Time pressure" is not a constraint — "must decide by Friday" is.
6. If the problem is simple, say so. Not everything needs deep decomposition.

## Output Format

Respond with ONLY a JSON object (no markdown, no explanation):
{
  "objective": "<string>",
  "stakes": "<string>",
  "actors": [{"name": "<who>", "role": "<what they do>", "incentive": "<what they want>"}],
  "incentives": [{"actor": "<who>", "incentive": "<what>", "alignment": "<aligned|neutral|opposed>"}],
  "constraints": [{"type": "<time|money|skill|dependency|legal|other>", "description": "<specific>"}],
  "assumptions": ["<assumption 1>", "<assumption 2>"],
  "unknowns": ["<unknown 1>", "<unknown 2>"],
  "irreversibilities": ["<irreversible action 1>"],
  "bottlenecks": ["<bottleneck 1>"],
  "observable_facts": ["<fact 1>", "<fact 2>"],
  "narrative_layer": ["<story the operator is telling themselves>"],
  "distortion_candidates": ["<possible distortion>"],
  "confidence": <0.0 to 1.0>
}
"""


async def structure_problem(
    problem_id: uuid.UUID,
    raw_prompt: str,
    *,
    operator_state: dict | None = None,
    thread_context: str | None = None,
) -> tuple[ProblemStructureCreate, dict]:
    """Decompose a raw problem into a structured analysis.

    Args:
        problem_id: UUID of the Problem record this structure belongs to.
        raw_prompt: The operator's raw problem description.
        operator_state: Optional current state estimate for distortion detection.
        thread_context: Optional thread description for additional context.

    Returns:
        (ProblemStructureCreate, usage_metadata) tuple.
    """
    context_parts = [f"Problem: {raw_prompt}"]
    if operator_state:
        context_parts.append(
            f"Operator's current state: {json.dumps(operator_state, default=str)}"
        )
    if thread_context:
        context_parts.append(f"Thread context: {thread_context}")

    user_message = "\n\n".join(context_parts)

    text, usage = await claude.complete(
        system=SYSTEM_PROMPT,
        user=user_message,
        max_tokens=1024,
    )

    parsed = _parse_response(text)

    create = ProblemStructureCreate(
        problem_id=problem_id,
        objective=parsed["objective"],
        stakes=parsed["stakes"],
        actors=parsed["actors"],
        incentives=parsed["incentives"],
        constraints=parsed["constraints"],
        assumptions=parsed["assumptions"],
        unknowns=parsed["unknowns"],
        irreversibilities=parsed["irreversibilities"],
        bottlenecks=parsed["bottlenecks"],
        observable_facts=parsed["observable_facts"],
        narrative_layer=parsed["narrative_layer"],
        distortion_candidates=parsed["distortion_candidates"],
        confidence=parsed["confidence"],
    )

    return create, usage


def _parse_response(text: str) -> dict:
    """Parse the JSON response from Claude, with fallback."""
    try:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
            cleaned = cleaned.rsplit("```", 1)[0]
        data = json.loads(cleaned)
    except (json.JSONDecodeError, IndexError):
        logger.warning("Failed to parse problem structurer response: %s", text[:200])
        data = {
            "objective": "Unable to parse — review raw prompt.",
            "stakes": None,
            "actors": [],
            "incentives": [],
            "constraints": [],
            "assumptions": [],
            "unknowns": ["Problem structure could not be parsed from AI response"],
            "irreversibilities": [],
            "bottlenecks": [],
            "observable_facts": [],
            "narrative_layer": [],
            "distortion_candidates": [],
            "confidence": 0.2,
        }

    return {
        "objective": data.get("objective"),
        "stakes": data.get("stakes"),
        "actors": data.get("actors", []),
        "incentives": data.get("incentives", []),
        "constraints": data.get("constraints", []),
        "assumptions": data.get("assumptions", []),
        "unknowns": data.get("unknowns", []),
        "irreversibilities": data.get("irreversibilities", []),
        "bottlenecks": data.get("bottlenecks", []),
        "observable_facts": data.get("observable_facts", []),
        "narrative_layer": data.get("narrative_layer", []),
        "distortion_candidates": data.get("distortion_candidates", []),
        "confidence": Decimal(
            str(min(max(float(data.get("confidence", 0.5)), 0.0), 1.0))
        ),
    }
