"""State Estimator — determines the operator's current operating condition.

Consumes evidence (subjective checkins, behavior events, context snapshots,
physiology) and produces a StateEstimate with a state_kind, confidence,
and contributing_factors list.

This is the first module in the AI Fabric pipeline:
  evidence -> STATE ESTIMATOR -> blocker classifier -> policy selector
"""

from __future__ import annotations

import json
import logging
import uuid
from decimal import Decimal

from utopia.ai.providers import claude
from utopia.enums import StateKind
from utopia.schemas.execution import StateEstimateCreate

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are the State Estimator module inside Utopia, a private cognitive operating system.

Your job: given evidence about the operator's current condition, determine which operating state they are most likely in.

## Operating States

- recover: Capacity is depleted. The operator needs rest, not more tasks.
- preserve: Capacity is fragile. Protect what exists, avoid new load.
- orient: The operator has lost direction. They need to re-establish what matters.
- clarify: Ambiguity is the primary blocker. The problem needs shrinking.
- reenter: The operator was interrupted and needs to resume a thread.
- execute: Conditions are adequate for action. Do the work.
- deep_work: Conditions are excellent for sustained, focused effort.
- close_loop: Something is nearly finished. Push to completion.
- review: The operator should reflect on recent outcomes.
- drift: The operator is off course without awareness. Needs intervention.

## Rules

1. Be honest about low-energy states. Do not default to "execute".
2. Energy below 30 almost always means "recover" or "preserve".
3. High resistance + low clarity often means "clarify" or "orient".
4. Recent thread_switched or failed_start events suggest "reenter" or "clarify".
5. If recovery score from WHOOP is below 33, weight "recover" heavily.
6. "drift" is for when behavior contradicts stated direction — use sparingly.

## Output Format

Respond with ONLY a JSON object (no markdown, no explanation):
{
  "state_kind": "<one of the states above>",
  "confidence": <0.0 to 1.0>,
  "contributing_factors": [
    {"source": "<evidence type>", "signal": "<field name>", "value": "<value>", "weight": "<how much it influenced>"}
  ]
}
"""


async def estimate_state(
    operator_id: uuid.UUID,
    evidence: dict,
    *,
    thread_id: uuid.UUID | None = None,
) -> tuple[StateEstimateCreate, dict]:
    """Run the State Estimator on gathered evidence.

    Args:
        operator_id: The operator to estimate state for.
        evidence: Dict with keys like "checkin", "behavior_events",
                  "context", "physiology", "derived_features".
        thread_id: Optional thread context.

    Returns:
        (StateEstimateCreate, usage_metadata) tuple.
    """
    user_message = f"Here is the current evidence for the operator:\n\n{json.dumps(evidence, indent=2, default=str)}"

    text, usage = await claude.complete(
        system=SYSTEM_PROMPT,
        user=user_message,
        max_tokens=512,
    )

    parsed = _parse_response(text)

    create = StateEstimateCreate(
        operator_id=operator_id,
        thread_id=thread_id,
        state_kind=parsed["state_kind"],
        confidence=parsed["confidence"],
        contributing_factors=parsed["contributing_factors"],
    )

    return create, usage


def _parse_response(text: str) -> dict:
    """Parse the JSON response from Claude, with fallback."""
    try:
        # Strip any markdown code fences if present
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
            cleaned = cleaned.rsplit("```", 1)[0]
        data = json.loads(cleaned)
    except (json.JSONDecodeError, IndexError):
        logger.warning("Failed to parse state estimator response: %s", text[:200])
        data = {
            "state_kind": "orient",
            "confidence": 0.3,
            "contributing_factors": [
                {"source": "parse_error", "signal": "fallback", "value": "true", "weight": "high"}
            ],
        }

    # Validate state_kind
    try:
        state_kind = StateKind(data["state_kind"])
    except (ValueError, KeyError):
        state_kind = StateKind.orient
        data["confidence"] = 0.3

    return {
        "state_kind": state_kind,
        "confidence": Decimal(str(min(max(float(data.get("confidence", 0.5)), 0.0), 1.0))),
        "contributing_factors": data.get("contributing_factors", []),
    }
