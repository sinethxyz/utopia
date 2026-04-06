"""Policy Selector (Schrodinger) — produces the one correct next move.

Consumes the state estimate, blocker estimate, and evidence to produce
a PolicyDecision: mode, intervention_kind, action_depth, next_move,
rationale, and caution_flags.

Pipeline position:
  evidence -> state estimator -> blocker classifier -> POLICY SELECTOR
"""

from __future__ import annotations

import json
import logging
import uuid
from decimal import Decimal

from utopia.ai.providers import claude
from utopia.enums import ActionDepth, InterventionKind
from utopia.schemas.execution import PolicyDecisionCreate

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are Schrodinger, the Policy Selector inside Utopia, a private cognitive operating system.

Your job: given the operator's state estimate, blocker estimate, and evidence, produce the ONE correct next move.

## Intervention Kinds (what type of action)

- recover: Rest, sleep, step away. Capacity must rebuild.
- preserve: Protect current state. Do minimal, avoid new load.
- orient: Re-establish direction. Review life arcs, seasons, missions.
- reenter: Resume an interrupted thread using re-entry context.
- clarify: Reduce ambiguity. Decompose the problem, ask one question.
- ask: Pose a single high-leverage question to unlock motion.
- execute: Do the work. Conditions support action.
- close_loop: Finish something that is nearly done.
- review: Reflect on recent traces, patterns, outcomes.

## Action Depth (how deep should the action go)

- tiny: Absolute minimum friction. One sentence, one click, one thought.
- narrow: Single track, 5-15 minutes, deterministic outcome.
- moderate: Balanced scope, 15-45 minutes, requires some judgment.
- deep: Full focus session, 45+ minutes, sustained concentration.

## Rules

1. Match action depth to the operator's ACTUAL capacity, not their ambition.
2. If state is "recover" or "preserve", action_depth must be "tiny" or "narrow".
3. If blocker is "physiological_depletion", intervention MUST be "recover".
4. The next_move must be CONCRETE and ACTIONABLE — not vague advice.
5. Bad example: "Consider working on your project"
6. Good example: "Open the ThreadX doc and write the first test case name"
7. Caution flags should warn about traps: overcommitting, narrative distortion, etc.
8. If the operator is in a productive state with no major blocker, say "execute" and give a specific next step.
9. mode and intervention_kind should usually match unless there's a reason to differ.

## Output Format

Respond with ONLY a JSON object (no markdown, no explanation):
{
  "intervention_kind": "<one of the intervention kinds above>",
  "action_depth": "<tiny|narrow|moderate|deep>",
  "next_move": "<the specific, concrete next action>",
  "rationale": "<1-2 sentences explaining why this move>",
  "confidence": <0.0 to 1.0>,
  "caution_flags": ["<warning 1>", "<warning 2>"]
}
"""


async def select_policy(
    operator_id: uuid.UUID,
    evidence: dict,
    state_estimate: dict,
    blocker_estimate: dict,
    *,
    thread_id: uuid.UUID | None = None,
    state_estimate_id: uuid.UUID | None = None,
    blocker_estimate_id: uuid.UUID | None = None,
) -> tuple[PolicyDecisionCreate, dict]:
    """Run the Policy Selector on state + blocker + evidence.

    Args:
        operator_id: The operator.
        evidence: Raw evidence dict.
        state_estimate: Dict with state_kind, confidence, contributing_factors.
        blocker_estimate: Dict with blocker_kind, confidence, supporting_evidence.
        thread_id: Optional thread context.
        state_estimate_id: UUID of the persisted state estimate.
        blocker_estimate_id: UUID of the persisted blocker estimate.

    Returns:
        (PolicyDecisionCreate, usage_metadata) tuple.
    """
    context = {
        "state_estimate": state_estimate,
        "blocker_estimate": blocker_estimate,
        "evidence": evidence,
    }
    user_message = f"Here is the operator's full assessment context:\n\n{json.dumps(context, indent=2, default=str)}"

    text, usage = await claude.complete(
        system=SYSTEM_PROMPT,
        user=user_message,
        max_tokens=768,
    )

    parsed = _parse_response(text)

    create = PolicyDecisionCreate(
        operator_id=operator_id,
        thread_id=thread_id,
        state_estimate_id=state_estimate_id,
        blocker_estimate_id=blocker_estimate_id,
        mode=parsed["intervention_kind"],
        intervention_kind=parsed["intervention_kind"],
        action_depth=parsed["action_depth"],
        next_move=parsed["next_move"],
        rationale=parsed["rationale"],
        confidence=parsed["confidence"],
        caution_flags=parsed["caution_flags"],
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
        logger.warning("Failed to parse policy selector response: %s", text[:200])
        data = {
            "intervention_kind": "orient",
            "action_depth": "tiny",
            "next_move": "Take a moment to review your current threads and identify which one matters most right now.",
            "rationale": "Could not parse AI response. Defaulting to orientation.",
            "confidence": 0.2,
            "caution_flags": ["AI response parse failure — this is a fallback recommendation"],
        }

    try:
        intervention_kind = InterventionKind(data["intervention_kind"])
    except (ValueError, KeyError):
        intervention_kind = InterventionKind.orient

    try:
        action_depth = ActionDepth(data["action_depth"])
    except (ValueError, KeyError):
        action_depth = ActionDepth.tiny

    return {
        "intervention_kind": intervention_kind,
        "action_depth": action_depth,
        "next_move": data.get("next_move", "Review your current state and pick the smallest useful action."),
        "rationale": data.get("rationale"),
        "confidence": Decimal(str(min(max(float(data.get("confidence", 0.5)), 0.0), 1.0))),
        "caution_flags": data.get("caution_flags", []),
    }
