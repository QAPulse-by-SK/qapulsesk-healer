"""LLM provider abstractions and concrete backends.

Public surface:
    - :class:`LLMProvider` — Protocol every backend satisfies
    - :class:`AnthropicProvider` — Claude (Anthropic API)
    - :class:`GeminiProvider` — Google Gemini (free tier available)
    - :func:`default_provider` — picks a provider based on available env vars

Re-exports are lazy via ``__getattr__`` so importing this package does not
trigger imports of the ``anthropic`` or ``google.genai`` SDKs unless the
corresponding provider is actually instantiated.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qapulsesk_healer.llm.base import LLMProvider, default_provider

__all__ = [
    "AnthropicProvider",
    "GeminiProvider",
    "LLMProvider",
    "default_provider",
]

if TYPE_CHECKING:
    from qapulsesk_healer.llm.anthropic import AnthropicProvider
    from qapulsesk_healer.llm.gemini import GeminiProvider


def __getattr__(name: str) -> Any:
    if name == "AnthropicProvider":
        from qapulsesk_healer.llm.anthropic import AnthropicProvider

        return AnthropicProvider
    if name == "GeminiProvider":
        from qapulsesk_healer.llm.gemini import GeminiProvider

        return GeminiProvider
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
