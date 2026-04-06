"""Blocker Classifier — diagnoses why motion is failing.

Consumes the same evidence as the State Estimator plus the state
estimate itself. Produces a BlockerEstimate with blocker_kind,
confidence, and supporting_evidence.

Pipeline position:
  evidence -> state estimator -> BLOCKER CLASSIFIER -> policy selector
"""

from __future__ import annotations

import json
import logging
import uuid
from decimal import Decimal

from utopia.ai.providers import claude
from utopia.enums import BlockerKind
from utopia.schemas.execution import BlockerEstimateCreate

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are the Blocker Classifier module inside Utopia, a private cognitive operating system.

Your job: given evidence about the operator and their current state estimate, diagnose the PRIMARY reason motion is failing or would fail.

## Blocker Types

- ambiguity: The next step is unclear. The problem needs shrinking or decomposition.
- scope_overload: Too many things competing for attention. Reduce to one.
- physiological_depletion: Energy/recovery is too low for productive work.
- emotional_threat: Fear, anxiety, or emotional resistance is blocking action.
- context_fracture: The operator was interrupted and has lost context. Needs re-entry.
- vector_conflict: Multiple commitments pull in different directions.
- environmental_friction: The environment makes action costly (noise, setup, tools).
- stimulation_hijack: Distraction is pulling attention away from the work.
- narrative_distortion: The operator's self-story is sabotaging action ("I always fail at this").
- completion_aversion: The work is nearly done but the operator avoids finishing.
- problem_misclassification: The problem is framed wrong. Reframing is needed.
- decision_fog: Too many options, can't choose. Needs more evidence or a forcing function.

## Rules

1. Each blocker implies a DIFFERENT intervention. Classify precisely.
2. If the operator's state is "recover" or "preserve", the blocker is almost always "physiological_depletion".
3. Multiple failed_start events suggest "ambiguity" or "emotional_threat".
4. Thread switching without completion suggests "context_fracture" or "stimulation_hijack".
5. High resistance + high clarity suggests "emotional_threat" or "completion_aversion".
6. If no clear blocker exists (the operator is in a productive state), use "ambiguity" with low confidence.

## Output Format

Respond with ONLY a JSON object (no markdown, no explanation):
{
  "blocker_kind": "<one of the blocker types above>",
  "confidence": <0.0 to 1.0>,
  "supporting_evidence": [
    {"source": "<evidence type>", "signal": "<field>", "value": "<value>", "reasoning": "<why this matters>"}
  ]
}
"""


async def classify_blocker(
    operator_id: uuid.UUID,
    evidence: dict,
    state_estimate: dict,
    *,
    thread_id: uuid.UUID | None = None,
) -> tuple[BlockerEstimateCreate, dict]:
    """Run the Blocker Classifier on evidence + state estimate.

    Args:
        operator_id: The operator to classify blockers for.
        evidence: Same evidence dict used by the state estimator.
        state_estimate: Dict with state_kind, confidence, contributing_factors.
        thread_id: Optional thread context.

    Returns:
        (BlockerEstimateCreate, usage_metadata) tuple.
    """
    context = {
        "state_estimate": state_estimate,
        "evidence": evidence,
    }
    user_message = f"Here is the operator's state estimate and evidence:\n\n{json.dumps(context, indent=2, default=str)}"

    text, usage = await claude.complete(
        system=SYSTEM_PROMPT,
        user=user_message,
        max_tokens=512,
    )

    parsed = _parse_response(text)

    create = BlockerEstimateCreate(
        operator_id=operator_id,
        thread_id=thread_id,
        blocker_kind=parsed["blocker_kind"],
        confidence=parsed["confidence"],
        supporting_evidence=parsed["supporting_evidence"],
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
        logger.warning("Failed to parse blocker classifier response: %s", text[:200])
        data = {
            "blocker_kind": "ambiguity",
            "confidence": 0.3,
            "supporting_evidence": [
                {"source": "parse_error", "signal": "fallback", "value": "true", "reasoning": "Could not parse AI response"}
            ],
        }

    try:
        blocker_kind = BlockerKind(data["blocker_kind"])
    except (ValueError, KeyError):
        blocker_kind = BlockerKind.ambiguity
        data["confidence"] = 0.3

    return {
        "blocker_kind": blocker_kind,
        "confidence": Decimal(str(min(max(float(data.get("confidence", 0.5)), 0.0), 1.0))),
        "supporting_evidence": data.get("supporting_evidence", []),
    }
