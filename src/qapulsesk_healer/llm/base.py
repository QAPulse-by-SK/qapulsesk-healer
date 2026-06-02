"""LLM provider Protocol, prompt builder, JSON parser, and provider factory.

This module is provider-agnostic. Concrete backends (Anthropic, Gemini) live
in sibling modules and reuse the prompt + parser defined here so the prompt
contract stays consistent across providers.
"""

from __future__ import annotations

import json
import logging
import os
import time
from collections.abc import Callable
from typing import Protocol, TypeVar

from qapulsesk_healer.candidates import Candidate
from qapulsesk_healer.snapshots.base import Snapshot
from qapulsesk_healer.strategies import strategies_for

DEFAULT_MAX_CANDIDATES = 5
DEFAULT_RETRY_ATTEMPTS = 4
DEFAULT_RETRY_INITIAL_DELAY = 1.0

log = logging.getLogger(__name__)

T = TypeVar("T")


def _build_prompt(
    snapshot: Snapshot,
    original_strategy: str,
    original_value: str,
    intent: str,
    max_candidates: int,
) -> str:
    """Construct the user-message prompt sent to whichever LLM is configured."""
    allowed = strategies_for(snapshot.platform)

    return f"""You are a test-automation expert helping repair a broken locator.

PLATFORM: {snapshot.platform.value}
SNAPSHOT KIND: {snapshot.kind}

ORIGINAL LOCATOR (no longer matches):
  strategy: {original_strategy}
  value:    {original_value}

INTENT (what this element does):
  {intent}

ALLOWED STRATEGIES for this platform: {", ".join(allowed)}

PAGE SOURCE (minified):
```
{snapshot.minify()}
```

Propose up to {max_candidates} replacement locators that most likely match the
ORIGINAL INTENT given the current page source. Rank them by your confidence
(highest first). Prefer stable strategies (accessibility id, data-testid,
resource-id, aria-label) over fragile ones (xpath by position, generated class
names). Each candidate's `value` must be syntactically valid for its strategy.

Respond with ONLY a JSON object (no prose, no markdown fences) of the form:
{{
  "candidates": [
    {{
      "strategy": "<one of the allowed strategies>",
      "value": "<the locator value>",
      "confidence": <float between 0 and 1>,
      "reasoning": "<one sentence>"
    }}
  ]
}}"""


def _parse_candidates(text: str) -> list[Candidate]:
    """Parse a model JSON response into a list of :class:`Candidate` objects.

    Tolerant of common formatting noise — leading/trailing whitespace and
    markdown code fences are stripped before parsing.
    """
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned.rsplit("```", 1)[0]
    cleaned = cleaned.strip()

    try:
        payload = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError(f"LLM response was not valid JSON: {exc}\nGot: {text!r}") from exc

    raw_candidates = payload.get("candidates", [])
    if not isinstance(raw_candidates, list):
        raise ValueError("LLM response 'candidates' field is not a list")

    return [Candidate(**c) for c in raw_candidates]


class LLMProvider(Protocol):
    """Interface every LLM backend must satisfy."""

    def propose_candidates(
        self,
        snapshot: Snapshot,
        original_strategy: str,
        original_value: str,
        intent: str,
        max_candidates: int = DEFAULT_MAX_CANDIDATES,
    ) -> list[Candidate]: ...


def default_provider() -> LLMProvider:
    """Return a configured :class:`LLMProvider` based on available env vars.

    Priority order — Gemini first because its free tier covers typical
    locator-healing workloads at zero cost:

    1. ``GEMINI_API_KEY`` → :class:`GeminiProvider`
    2. ``ANTHROPIC_API_KEY`` → :class:`AnthropicProvider`
    3. Neither set → :class:`RuntimeError` with guidance on how to obtain a key.

    Raises:
        RuntimeError: If neither environment variable is set.
    """
    if os.environ.get("GEMINI_API_KEY"):
        from qapulsesk_healer.llm.gemini import GeminiProvider

        return GeminiProvider()
    if os.environ.get("ANTHROPIC_API_KEY"):
        from qapulsesk_healer.llm.anthropic import AnthropicProvider

        return AnthropicProvider()
    raise RuntimeError(
        "No LLM provider available. Set one of:\n"
        "  GEMINI_API_KEY    (free tier: https://aistudio.google.com/apikey)\n"
        "  ANTHROPIC_API_KEY (paid: https://console.anthropic.com/settings/keys)\n"
        "Or pass an explicit `llm=` to Healer(...)."
    )


def _is_transient(exc: BaseException) -> bool:
    """Decide whether an exception from an LLM SDK is worth retrying.

    Transient = network/server hiccups that typically resolve in seconds:
    HTTP 429 (rate-limited), 500 (server error), 502/503/504 (gateway/unavailable).
    Everything else (auth errors, malformed requests) is fatal — no retry.
    """
    # Probe a few well-known attribute names that SDKs use to expose status codes.
    # We do it duck-typed so we don't have to import every SDK's error class.
    for attr in ("status_code", "code", "http_status"):
        status = getattr(exc, attr, None)
        if isinstance(status, int) and status in {429, 500, 502, 503, 504}:
            return True
    # Fall back to the message — most SDKs render the code in the string form.
    msg = str(exc).lower()
    return any(
        token in msg
        for token in (" 429", " 500", " 502", " 503", " 504", "unavailable", "overloaded")
    )


def _with_retry(
    fn: Callable[[], T],
    *,
    attempts: int = DEFAULT_RETRY_ATTEMPTS,
    initial_delay: float = DEFAULT_RETRY_INITIAL_DELAY,
    sleep: Callable[[float], None] = time.sleep,
) -> T:
    """Call `fn()` with exponential backoff on transient LLM errors.

    Delay sequence: ``initial_delay``, ``2 * initial_delay``, ``4 * ...``, ...
    Non-transient errors raise immediately. After all attempts are exhausted,
    the last transient error is re-raised.

    `sleep` is parameterised so tests can pass a no-op.
    """
    last_exc: BaseException | None = None
    delay = initial_delay
    for attempt in range(1, attempts + 1):
        try:
            return fn()
        except Exception as exc:
            if not _is_transient(exc):
                raise
            last_exc = exc
            if attempt == attempts:
                break
            log.warning(
                "Transient LLM error on attempt %d/%d (%s). Retrying in %.1fs.",
                attempt,
                attempts,
                type(exc).__name__,
                delay,
            )
            sleep(delay)
            delay *= 2
    assert last_exc is not None
    raise last_exc
