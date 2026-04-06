"""Council — multi-perspective deliberation for complex decisions.

Runs multiple reasoning perspectives on a problem and synthesizes them
into a deliberation report. Each perspective applies a different lens
(risk, opportunity, contrarian, operator-state-aware) to the same problem.

This is the system's mechanism for avoiding single-perspective blindness.
"""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass, field

from utopia.ai.providers import claude

logger = logging.getLogger(__name__)

PERSPECTIVES = [
    {
        "name": "risk_analyst",
        "instruction": (
            "You evaluate downside risk. What could go wrong? What is irreversible? "
            "What is the worst realistic outcome? Where is the operator blind to danger?"
        ),
    },
    {
        "name": "opportunity_scout",
        "instruction": (
            "You evaluate upside potential. What could this unlock? What adjacent "
            "possibilities exist? Where is the operator being too conservative?"
        ),
    },
    {
        "name": "contrarian",
        "instruction": (
            "You challenge the framing. Is this the right problem? Is the operator "
            "solving the symptom instead of the cause? What would happen if they did nothing?"
        ),
    },
    {
        "name": "state_advisor",
        "instruction": (
            "You assess whether the operator's current cognitive and physiological state "
            "is appropriate for this decision. Should they decide now, or wait? Is their "
            "state distorting their judgment?"
        ),
    },
]

PERSPECTIVE_SYSTEM = """\
You are a member of the Council inside Utopia, a private cognitive operating system.

Your perspective: {perspective_name}
Your instruction: {perspective_instruction}

## Rules

1. Stay in character. Only evaluate from your assigned perspective.
2. Be specific and concrete. "There might be risks" is useless.
3. Reference specific evidence when available.
4. Disagree with other perspectives when your lens demands it.
5. Your output should be 2-4 key points, each with reasoning.

## Output Format

Respond with ONLY a JSON object (no markdown, no explanation):
{{
  "perspective": "{perspective_name}",
  "key_points": [
    {{"point": "<specific insight>", "reasoning": "<why this matters>", "confidence": <0.0-1.0>}}
  ],
  "recommendation": "<your recommendation from this perspective>",
  "dissents": ["<anything you'd push back on from other perspectives>"]
}}
"""

SYNTHESIS_SYSTEM = """\
You are the Council Synthesizer inside Utopia, a private cognitive operating system.

Your job: synthesize multiple perspective analyses into a single deliberation report. The perspectives may conflict — that's the point.

## Rules

1. Don't average the perspectives. Identify where they agree (signal) and where they disagree (decision points).
2. Flag any perspective that was clearly more relevant than others.
3. The final recommendation should account for the operator's current state.
4. If perspectives are deeply split, say so — the operator needs to decide.

## Output Format

Respond with ONLY a JSON object (no markdown, no explanation):
{
  "consensus_points": ["<things all perspectives agree on>"],
  "tension_points": [{"tension": "<the disagreement>", "perspectives": ["<who disagrees>"], "stakes": "<why it matters>"}],
  "dominant_perspective": "<which perspective should carry most weight and why>",
  "synthesis": "<2-3 sentence integrated recommendation>",
  "decision_readiness": "<ready|needs_more_info|defer>",
  "confidence": <0.0 to 1.0>
}
"""


@dataclass
class DeliberationResult:
    """Complete output of the Council deliberation."""

    perspectives: list[dict] = field(default_factory=list)
    consensus_points: list[str] = field(default_factory=list)
    tension_points: list[dict] = field(default_factory=list)
    dominant_perspective: str = ""
    synthesis: str = ""
    decision_readiness: str = "needs_more_info"
    confidence: float = 0.0
    model_usage: list[dict] = field(default_factory=list)


async def deliberate(
    problem_description: str,
    *,
    problem_structure: dict | None = None,
    operator_state: dict | None = None,
    physiology: dict | None = None,
    relevant_knowledge: list[dict] | None = None,
) -> DeliberationResult:
    """Run multi-perspective deliberation on a problem.

    Args:
        problem_description: The problem to deliberate on.
        problem_structure: Optional structured decomposition of the problem.
        operator_state: Optional current state estimate.
        physiology: Optional physiological data.
        relevant_knowledge: Optional retrieved knowledge fragments.

    Returns:
        DeliberationResult with all perspectives and synthesis.
    """
    result = DeliberationResult()

    # Build shared context
    context_parts = [f"Problem: {problem_description}"]
    if problem_structure:
        context_parts.append(
            f"Structured analysis:\n{json.dumps(problem_structure, indent=2, default=str)}"
        )
    if operator_state:
        context_parts.append(
            f"Operator state: {json.dumps(operator_state, default=str)}"
        )
    if physiology:
        context_parts.append(
            f"Physiology: {json.dumps(physiology, default=str)}"
        )
    if relevant_knowledge:
        context_parts.append(
            f"Relevant knowledge:\n{json.dumps(relevant_knowledge, indent=2, default=str)}"
        )

    shared_context = "\n\n".join(context_parts)

    # Run each perspective sequentially (could be parallelized with asyncio.gather)
    for perspective in PERSPECTIVES:
        system = PERSPECTIVE_SYSTEM.format(
            perspective_name=perspective["name"],
            perspective_instruction=perspective["instruction"],
        )

        text, usage = await claude.complete(
            system=system,
            user=shared_context,
            max_tokens=512,
        )
        result.model_usage.append({"module": f"council_{perspective['name']}", **usage})

        parsed = _parse_perspective(text, perspective["name"])
        result.perspectives.append(parsed)

    # Synthesize all perspectives
    synthesis_input = {
        "problem": problem_description,
        "perspectives": result.perspectives,
        "operator_state": operator_state,
    }

    text, usage = await claude.complete(
        system=SYNTHESIS_SYSTEM,
        user=json.dumps(synthesis_input, indent=2, default=str),
        max_tokens=512,
    )
    result.model_usage.append({"module": "council_synthesis", **usage})

    synthesis = _parse_synthesis(text)
    result.consensus_points = synthesis["consensus_points"]
    result.tension_points = synthesis["tension_points"]
    result.dominant_perspective = synthesis["dominant_perspective"]
    result.synthesis = synthesis["synthesis"]
    result.decision_readiness = synthesis["decision_readiness"]
    result.confidence = synthesis["confidence"]

    return result


def _parse_perspective(text: str, perspective_name: str) -> dict:
    """Parse a single perspective response."""
    try:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
            cleaned = cleaned.rsplit("```", 1)[0]
        data = json.loads(cleaned)
    except (json.JSONDecodeError, IndexError):
        logger.warning("Failed to parse %s perspective: %s", perspective_name, text[:200])
        data = {
            "perspective": perspective_name,
            "key_points": [{"point": "Parse failure", "reasoning": "Could not parse AI response", "confidence": 0.2}],
            "recommendation": "Unable to provide recommendation — parse failure.",
            "dissents": [],
        }

    return {
        "perspective": data.get("perspective", perspective_name),
        "key_points": data.get("key_points", []),
        "recommendation": data.get("recommendation", ""),
        "dissents": data.get("dissents", []),
    }


def _parse_synthesis(text: str) -> dict:
    """Parse the synthesis response."""
    try:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
            cleaned = cleaned.rsplit("```", 1)[0]
        data = json.loads(cleaned)
    except (json.JSONDecodeError, IndexError):
        logger.warning("Failed to parse council synthesis: %s", text[:200])
        data = {
            "consensus_points": [],
            "tension_points": [],
            "dominant_perspective": "unknown",
            "synthesis": "Council deliberation could not be synthesized.",
            "decision_readiness": "needs_more_info",
            "confidence": 0.2,
        }

    readiness = data.get("decision_readiness", "needs_more_info")
    if readiness not in {"ready", "needs_more_info", "defer"}:
        readiness = "needs_more_info"

    return {
        "consensus_points": data.get("consensus_points", []),
        "tension_points": data.get("tension_points", []),
        "dominant_perspective": data.get("dominant_perspective", ""),
        "synthesis": data.get("synthesis", ""),
        "decision_readiness": readiness,
        "confidence": min(max(float(data.get("confidence", 0.5)), 0.0), 1.0),
    }
