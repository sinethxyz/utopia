"""Contradiction Checker — detects inconsistencies between narrative and evidence.

Compares what the operator says with what the evidence shows. Produces
ContradictionReport artifacts when the operator's self-narrative diverges
from behavioral, physiological, or contextual evidence.

This is the system's honesty layer.
"""

from __future__ import annotations

import json
import logging
import uuid
from decimal import Decimal

from utopia.ai.providers import claude
from utopia.schemas.reasoning import ContradictionReportCreate

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are the Contradiction Checker inside Utopia, a private cognitive operating system.

Your job: detect inconsistencies between the operator's stated narrative and the actual evidence. The operator is not lying — they are often genuinely unable to see the gap. Your job is to expose it gently but precisely.

## Contradiction Kinds

- narrative_vs_behavior: The operator says one thing but their behavior shows another. ("I'm productive" but 5 failed starts today)
- physiology_vs_claim: Physiological data contradicts the operator's self-report. ("I feel fine" but recovery is 22%)
- vector_vs_action: The operator's stated direction conflicts with what they actually work on. ("Building X is priority" but no activity on X threads in 2 weeks)
- state_vs_depth: The operator is attempting action depth their state doesn't support. (State = recover but trying deep_work)
- temporal_pattern: A recurring pattern the operator doesn't acknowledge. (Always claims energy is fine on Monday, always crashes by Wednesday)

## Rules

1. Be precise about what contradicts what. Vague suspicion is not useful.
2. Severity should reflect the stakes: a minor energy miscalibration is low, a persistent vector conflict is high.
3. Not all inconsistencies are contradictions — some are honest uncertainty. Only flag clear divergences.
4. Include the specific evidence that supports the contradiction.
5. If no contradictions are found, say so clearly with high confidence.

## Output Format

Respond with ONLY a JSON object (no markdown, no explanation):
{
  "contradictions": [
    {
      "contradiction_kind": "<one of the kinds above>",
      "description": "<what contradicts what>",
      "evidence": [
        {"source": "<evidence type>", "claim": "<what operator says>", "reality": "<what evidence shows>"}
      ],
      "severity": <0.0 to 1.0>
    }
  ],
  "clean_signals": ["<areas where narrative and evidence align>"],
  "confidence": <0.0 to 1.0>
}
"""


async def check_contradictions(
    operator_id: uuid.UUID,
    *,
    operator_claims: dict | None = None,
    evidence: dict | None = None,
    state_estimate: dict | None = None,
    physiology: dict | None = None,
    recent_behavior: list[dict] | None = None,
    problem_id: uuid.UUID | None = None,
) -> tuple[list[ContradictionReportCreate], dict]:
    """Check for contradictions between narrative and evidence.

    Args:
        operator_id: The operator to check.
        operator_claims: What the operator says about their state/direction.
        evidence: Current evidence bundle (checkins, context, etc.).
        state_estimate: Current state estimate from the State Estimator.
        physiology: Current physiological data.
        recent_behavior: Recent behavior events.
        problem_id: Optional problem context.

    Returns:
        (list[ContradictionReportCreate], usage_metadata) tuple.
    """
    context = {}
    if operator_claims:
        context["operator_claims"] = operator_claims
    if evidence:
        context["evidence"] = evidence
    if state_estimate:
        context["state_estimate"] = state_estimate
    if physiology:
        context["physiology"] = physiology
    if recent_behavior:
        context["recent_behavior"] = recent_behavior

    if not context:
        return [], {"model": "none", "prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0, "latency_ms": 0}

    user_message = (
        f"Here is the operator's current data for contradiction analysis:\n\n"
        f"{json.dumps(context, indent=2, default=str)}"
    )

    text, usage = await claude.complete(
        system=SYSTEM_PROMPT,
        user=user_message,
        max_tokens=768,
    )

    parsed = _parse_response(text)

    reports = []
    for contradiction in parsed["contradictions"]:
        report = ContradictionReportCreate(
            operator_id=operator_id,
            problem_id=problem_id,
            contradiction_kind=contradiction["contradiction_kind"],
            description=contradiction["description"],
            evidence=contradiction.get("evidence", []),
            severity=Decimal(str(min(max(float(contradiction.get("severity", 0.5)), 0.0), 1.0))),
        )
        reports.append(report)

    return reports, usage


def _parse_response(text: str) -> dict:
    """Parse the JSON response from Claude, with fallback."""
    try:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
            cleaned = cleaned.rsplit("```", 1)[0]
        data = json.loads(cleaned)
    except (json.JSONDecodeError, IndexError):
        logger.warning("Failed to parse contradiction checker response: %s", text[:200])
        data = {
            "contradictions": [],
            "clean_signals": [],
            "confidence": 0.2,
        }

    valid_kinds = {
        "narrative_vs_behavior", "physiology_vs_claim", "vector_vs_action",
        "state_vs_depth", "temporal_pattern",
    }

    contradictions = []
    for c in data.get("contradictions", []):
        kind = c.get("contradiction_kind", "narrative_vs_behavior")
        if kind not in valid_kinds:
            kind = "narrative_vs_behavior"
        contradictions.append({
            "contradiction_kind": kind,
            "description": c.get("description", ""),
            "evidence": c.get("evidence", []),
            "severity": c.get("severity", 0.5),
        })

    return {
        "contradictions": contradictions,
        "clean_signals": data.get("clean_signals", []),
        "confidence": min(max(float(data.get("confidence", 0.5)), 0.0), 1.0),
    }
