"""Anthropic Claude provider."""

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

DEFAULT_MODEL = "claude-sonnet-4-5"


class AnthropicProvider:
    """LLMProvider backed by the Anthropic Messages API.

    Install with: ``pip install qapulsesk-healer[anthropic]``.
    Set ``ANTHROPIC_API_KEY`` in the environment or pass ``api_key=`` explicitly.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = DEFAULT_MODEL,
        max_tokens: int = 1024,
    ) -> None:
        # Lazy import so users without the SDK installed still get clean errors.
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

        response = _with_retry(
            lambda: self._client.messages.create(
                model=self._model,
                max_tokens=self._max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
        )

        text = "".join(block.text for block in response.content if block.type == "text")
        return _parse_candidates(text)
