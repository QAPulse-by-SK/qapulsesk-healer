"""Google Gemini provider.

Gemini's free tier (via Google AI Studio) covers typical locator-healing
workloads at zero cost. Get a key at https://aistudio.google.com/apikey.

Note: free-tier usage is logged by Google for model improvement. Fine for
public sites without sensitive data; consider a paid tier (or Anthropic) when
testing flows that contain PII.
"""

from __future__ import annotations

import os

from qapulsesk_healer.candidates import Candidate
from qapulsesk_healer.llm.base import (
    DEFAULT_MAX_CANDIDATES,
    _build_prompt,
    _parse_candidates,
    _with_retry,
)
from qapulsesk_healer.snapshots.base import Snapshot

DEFAULT_MODEL = "gemini-2.5-flash"


class GeminiProvider:
    """LLMProvider backed by Google's Gemini API.

    Install with: ``pip install qapulsesk-healer[gemini]``.
    Set ``GEMINI_API_KEY`` in the environment or pass ``api_key=`` explicitly.

    Uses Gemini's ``response_mime_type='application/json'`` to force strict
    JSON output — no markdown fences, no preamble.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = DEFAULT_MODEL,
        max_output_tokens: int = 4096,
    ) -> None:
        # Lazy import so users without google-genai installed still get a clean error.
        from google import genai

        resolved_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not resolved_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Export it or pass api_key explicitly. "
                "Get a free key at https://aistudio.google.com/apikey."
            )

        self._client = genai.Client(api_key=resolved_key)
        self._model = model
        self._max_output_tokens = max_output_tokens

    def propose_candidates(
        self,
        snapshot: Snapshot,
        original_strategy: str,
        original_value: str,
        intent: str,
        max_candidates: int = DEFAULT_MAX_CANDIDATES,
    ) -> list[Candidate]:
        from google.genai import types

        prompt = _build_prompt(
            snapshot=snapshot,
            original_strategy=original_strategy,
            original_value=original_value,
            intent=intent,
            max_candidates=max_candidates,
        )

        response = _with_retry(
            lambda: self._client.models.generate_content(
                model=self._model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=self._max_output_tokens,
                    temperature=0.0,
                    response_mime_type="application/json",
                    # Disable reasoning tokens — this is structured generation,
                    # not a multi-step reasoning task. Saves a big chunk of the
                    # output budget on Gemini 2.5 Flash.
                    thinking_config=types.ThinkingConfig(thinking_budget=0),
                ),
            )
        )

        text = response.text or ""
        return _parse_candidates(text)
