"""Router — intent classification for incoming operator requests.

Classifies what the operator is actually asking for, so the system
can dispatch to the correct pipeline (assessment, problem structuring,
knowledge retrieval, review, etc.) rather than assuming everything
is an assessment request.

This is the front door of the AI Fabric.
"""

from __future__ import annotations

import json
import logging
import uuid

from utopia.ai.providers import claude

logger = logging.getLogger(__name__)

INTENT_KINDS = [
    "assess",
    "structure_problem",
    "retrieve_context",
    "interpret_physiology",
    "check_contradictions",
    "deliberate",
    "record_trace",
    "review",
    "reenter",
    "checkin",
    "unknown",
]

SYSTEM_PROMPT = """\
You are the Router module inside Utopia, a private cognitive operating system.

Your job: classify the operator's intent so the system dispatches to the correct pipeline.

## Intent Kinds

- assess: The operator wants a state assessment and next-move recommendation. ("How am I doing?", "What should I do?", "I'm stuck")
- structure_problem: The operator has a problem they want decomposed and analyzed. ("I need to decide...", "Help me think about...", "Break this down")
- retrieve_context: The operator wants to search their knowledge base. ("What do I know about...", "Find relevant...", "Remind me about...")
- interpret_physiology: The operator wants interpretation of their physiological data. ("How's my recovery?", "Am I depleted?", "What does my WHOOP say?")
- check_contradictions: The operator wants to verify consistency between claims and evidence. ("Am I being honest with myself?", "Does this match reality?")
- deliberate: The operator wants multi-perspective analysis of a decision. ("Give me different angles on...", "What would X think about...")
- record_trace: The operator is reporting what happened after an action. ("I did X and Y happened", "Update: finished the task")
- review: The operator wants to reflect on recent patterns and outcomes. ("What patterns do I see?", "Weekly review", "How did this week go?")
- reenter: The operator wants to resume a previously interrupted thread. ("Pick up where I left off", "Resume thread X")
- checkin: The operator is providing a subjective self-report. ("Energy 40, clarity 60", "Feeling overwhelmed")
- unknown: Cannot classify with confidence.

## Rules

1. Look for explicit intent signals first (keywords, question structure).
2. If the message contains numeric self-report values, it's probably "checkin".
3. If the message mentions a specific decision or tradeoff, lean toward "structure_problem".
4. Short, vague messages like "help" or "I'm lost" should map to "assess".
5. If truly ambiguous, use "assess" as the default — it's the safest starting point.

## Output Format

Respond with ONLY a JSON object (no markdown, no explanation):
{
  "intent": "<one of the intent kinds above>",
  "confidence": <0.0 to 1.0>,
  "extracted_context": {
    "thread_hint": "<thread name or null if not mentioned>",
    "problem_hint": "<problem description or null>",
    "urgency_signal": "<low|medium|high|null>"
  },
  "reasoning": "<1 sentence explaining classification>"
}
"""


async def classify_intent(
    operator_id: uuid.UUID,
    message: str,
    *,
    recent_state: dict | None = None,
) -> tuple[dict, dict]:
    """Classify the operator's intent from their message.

    Args:
        operator_id: The operator making the request.
        message: The raw message from the operator.
        recent_state: Optional dict with recent state_kind for context.

    Returns:
        (classification_dict, usage_metadata) tuple.
    """
    context_parts = [f"Operator message: {message}"]
    if recent_state:
        context_parts.append(f"Recent state: {json.dumps(recent_state, default=str)}")

    user_message = "\n\n".join(context_parts)

    text, usage = await claude.complete(
        system=SYSTEM_PROMPT,
        user=user_message,
        max_tokens=256,
    )

    parsed = _parse_response(text)
    return parsed, usage


def _parse_response(text: str) -> dict:
    """Parse the JSON response from Claude, with fallback."""
    try:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
            cleaned = cleaned.rsplit("```", 1)[0]
        data = json.loads(cleaned)
    except (json.JSONDecodeError, IndexError):
        logger.warning("Failed to parse router response: %s", text[:200])
        data = {
            "intent": "assess",
            "confidence": 0.3,
            "extracted_context": {},
            "reasoning": "Could not parse AI response — defaulting to assessment.",
        }

    intent = data.get("intent", "unknown")
    if intent not in INTENT_KINDS:
        intent = "assess"
        data["confidence"] = 0.3

    return {
        "intent": intent,
        "confidence": min(max(float(data.get("confidence", 0.5)), 0.0), 1.0),
        "extracted_context": data.get("extracted_context", {}),
        "reasoning": data.get("reasoning", ""),
    }
