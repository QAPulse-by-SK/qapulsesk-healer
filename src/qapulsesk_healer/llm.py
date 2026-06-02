"""LLM provider abstraction for generating ranked locator candidates.

v0.1.0 ships an Anthropic Claude implementation. The `LLMProvider` Protocol
lets future versions slot in OpenAI, Gemini, or local models without touching
the rest of the codebase.
"""

from __future__ import annotations

import json
import os
from typing import Protocol

from qapulsesk_healer.candidates import Candidate
from qapulsesk_healer.snapshots.base import Snapshot
from qapulsesk_healer.strategies import strategies_for

DEFAULT_MODEL = "claude-sonnet-4-5"
DEFAULT_MAX_CANDIDATES = 5


def _build_prompt(
    snapshot: Snapshot,
    original_strategy: str,
    original_value: str,
    intent: str,
    max_candidates: int,
) -> str:
    """Construct the user-message prompt sent to the LLM."""
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


class AnthropicProvider:
    """LLMProvider backed by the Anthropic Messages API."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = DEFAULT_MODEL,
        max_tokens: int = 1024,
    ) -> None:
        # Lazy-import so unit tests that mock the provider don't require the SDK.
        from anthropic import Anthropic

        resolved_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not resolved_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY is not set. Export it or pass api_key explicitly."
            )

        self._client = Anthropic(api_key=resolved_key)
        self._model = model
        self._max_tokens = max_tokens

    def propose_candidates(
        self,
        snapshot: Snapshot,
        original_strategy: str,
        original_value: str,
        intent: str,
        max_candidates: int = DEFAULT_MAX_CANDIDATES,
    ) -> list[Candidate]:
        prompt = _build_prompt(
            snapshot=snapshot,
            original_strategy=original_strategy,
            original_value=original_value,
            intent=intent,
            max_candidates=max_candidates,
        )

        response = self._client.messages.create(
            model=self._model,
            max_tokens=self._max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )

        text = "".join(block.text for block in response.content if block.type == "text")
        return _parse_candidates(text)


def _parse_candidates(text: str) -> list[Candidate]:
    """Parse the model's JSON response into a list of Candidate objects.

    Tolerant of common formatting noise — leading/trailing whitespace and
    markdown code fences are stripped before parsing.
    """
    cleaned = text.strip()
    if cleaned.startswith("```"):
        # Strip the opening fence (with or without a language tag).
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
