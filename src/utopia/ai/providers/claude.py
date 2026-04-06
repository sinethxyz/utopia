"""Claude API provider for the AI Fabric.

Wraps the Anthropic SDK to provide a simple interface for the
reasoning modules. Each module calls `complete()` with a system
prompt and user message, and gets back structured text.
"""

from __future__ import annotations

import logging
import time

import anthropic

from utopia.config import settings

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "claude-sonnet-4-20250514"


async def complete(
    *,
    system: str,
    user: str,
    model: str = DEFAULT_MODEL,
    max_tokens: int = 1024,
    temperature: float = 0.2,
) -> tuple[str, dict]:
    """Call Claude and return (response_text, usage_metadata).

    The usage_metadata dict contains:
        model, prompt_tokens, completion_tokens, total_tokens, latency_ms

    Raises anthropic.APIError on failure.
    """
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    start = time.monotonic()
    response = await client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    latency_ms = int((time.monotonic() - start) * 1000)

    text = response.content[0].text if response.content else ""
    usage = {
        "model": model,
        "prompt_tokens": response.usage.input_tokens,
        "completion_tokens": response.usage.output_tokens,
        "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
        "latency_ms": latency_ms,
    }

    logger.info(
        "Claude call: model=%s tokens=%d latency=%dms",
        model, usage["total_tokens"], latency_ms,
    )

    return text, usage
