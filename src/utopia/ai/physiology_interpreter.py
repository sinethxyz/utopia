"""Physiology Interpreter — translates raw WHOOP data into actionable signals.

Takes raw physiological data (recovery, sleep, strain, HRV) and produces
a human-readable interpretation with capacity implications that the State
Estimator and Policy Selector can consume.

This module bridges the gap between raw numbers and cognitive policy.
"""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass, field

from utopia.ai.providers import claude

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are the Physiology Interpreter inside Utopia, a private cognitive operating system.

Your job: translate raw physiological data (WHOOP recovery, sleep stages, HRV, strain) into actionable capacity signals that inform the operator's cognitive policy.

## Key Signals to Interpret

- Recovery score: 0-100. Below 33 = red (depleted), 33-66 = yellow (fragile), above 66 = green (capable).
- HRV (RMSSD): Higher is generally better. Sudden drops signal stress or illness.
- Sleep performance: Total sleep vs. needed. Slow wave and REM matter most.
- Strain: Cumulative load. High strain + low recovery = depletion risk.
- Resting heart rate: Lower is better baseline. Elevation signals stress.

## Rules

1. Be honest about depletion. The operator's ambition does not override physiology.
2. Context matters: a 50% recovery after illness is different from 50% after partying.
3. Trends matter more than single readings. Flag multi-day patterns.
4. Connect physiology to cognitive capacity explicitly. Recovery 30 means: "Deep work is not available to you right now."
5. If data is missing or stale (>24h), note the uncertainty.
6. Don't moralize. State the facts and their implications for action depth.

## Output Format

Respond with ONLY a JSON object (no markdown, no explanation):
{
  "capacity_level": "<depleted|fragile|moderate|strong|peak>",
  "capacity_score": <0-100>,
  "key_signals": [
    {"signal": "<name>", "value": "<value>", "interpretation": "<what this means>", "concern_level": "<none|low|moderate|high>"}
  ],
  "action_depth_ceiling": "<tiny|narrow|moderate|deep>",
  "recovery_trajectory": "<declining|stable|improving|unknown>",
  "warnings": ["<any urgent physiological concerns>"],
  "recommendation": "<1-2 sentence capacity-aware recommendation>",
  "confidence": <0.0 to 1.0>
}
"""


@dataclass
class PhysiologyInterpretation:
    """Structured interpretation of physiological data."""

    capacity_level: str = "unknown"
    capacity_score: int = 50
    key_signals: list[dict] = field(default_factory=list)
    action_depth_ceiling: str = "narrow"
    recovery_trajectory: str = "unknown"
    warnings: list[str] = field(default_factory=list)
    recommendation: str = ""
    confidence: float = 0.0
    model_usage: dict = field(default_factory=dict)


async def interpret_physiology(
    operator_id: uuid.UUID,
    physiology_data: dict,
    *,
    recent_trends: dict | None = None,
) -> tuple[PhysiologyInterpretation, dict]:
    """Interpret raw physiological data into capacity signals.

    Args:
        operator_id: The operator whose physiology to interpret.
        physiology_data: Dict with keys like "recovery", "sleep", "strain",
                         "hrv", "resting_heart_rate".
        recent_trends: Optional dict with multi-day trend data.

    Returns:
        (PhysiologyInterpretation, usage_metadata) tuple.
    """
    context = {"physiology": physiology_data}
    if recent_trends:
        context["trends"] = recent_trends

    user_message = (
        f"Here is the operator's current physiological data:\n\n"
        f"{json.dumps(context, indent=2, default=str)}"
    )

    text, usage = await claude.complete(
        system=SYSTEM_PROMPT,
        user=user_message,
        max_tokens=768,
    )

    parsed = _parse_response(text)

    interpretation = PhysiologyInterpretation(
        capacity_level=parsed["capacity_level"],
        capacity_score=parsed["capacity_score"],
        key_signals=parsed["key_signals"],
        action_depth_ceiling=parsed["action_depth_ceiling"],
        recovery_trajectory=parsed["recovery_trajectory"],
        warnings=parsed["warnings"],
        recommendation=parsed["recommendation"],
        confidence=parsed["confidence"],
        model_usage=usage,
    )

    return interpretation, usage


def _parse_response(text: str) -> dict:
    """Parse the JSON response from Claude, with fallback."""
    try:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
            cleaned = cleaned.rsplit("```", 1)[0]
        data = json.loads(cleaned)
    except (json.JSONDecodeError, IndexError):
        logger.warning("Failed to parse physiology interpreter response: %s", text[:200])
        data = {
            "capacity_level": "unknown",
            "capacity_score": 50,
            "key_signals": [],
            "action_depth_ceiling": "narrow",
            "recovery_trajectory": "unknown",
            "warnings": ["Could not parse physiological interpretation"],
            "recommendation": "Proceed with caution — interpretation unavailable.",
            "confidence": 0.2,
        }

    capacity_levels = {"depleted", "fragile", "moderate", "strong", "peak", "unknown"}
    depth_ceilings = {"tiny", "narrow", "moderate", "deep"}
    trajectories = {"declining", "stable", "improving", "unknown"}

    capacity_level = data.get("capacity_level", "unknown")
    if capacity_level not in capacity_levels:
        capacity_level = "unknown"

    action_depth = data.get("action_depth_ceiling", "narrow")
    if action_depth not in depth_ceilings:
        action_depth = "narrow"

    trajectory = data.get("recovery_trajectory", "unknown")
    if trajectory not in trajectories:
        trajectory = "unknown"

    return {
        "capacity_level": capacity_level,
        "capacity_score": max(0, min(100, int(data.get("capacity_score", 50)))),
        "key_signals": data.get("key_signals", []),
        "action_depth_ceiling": action_depth,
        "recovery_trajectory": trajectory,
        "warnings": data.get("warnings", []),
        "recommendation": data.get("recommendation", ""),
        "confidence": min(max(float(data.get("confidence", 0.5)), 0.0), 1.0),
    }
