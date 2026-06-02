"""Tests for the provider factory and the Gemini provider (mocked SDK)."""

from __future__ import annotations

import sys
import types
from unittest.mock import MagicMock

import pytest

from qapulsesk_healer.llm.base import default_provider


class TestDefaultProvider:
    def test_prefers_gemini_when_both_keys_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("GEMINI_API_KEY", "gemini-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "anthropic-key")

        # Stub `google.genai` so GeminiProvider can be instantiated without the SDK.
        fake_client = MagicMock()
        fake_genai = MagicMock()
        fake_genai.Client.return_value = fake_client
        fake_google = types.ModuleType("google")
        fake_google.genai = fake_genai  # type: ignore[attr-defined]
        monkeypatch.setitem(sys.modules, "google", fake_google)
        monkeypatch.setitem(sys.modules, "google.genai", fake_genai)

        provider = default_provider()

        assert type(provider).__name__ == "GeminiProvider"

    def test_falls_back_to_anthropic_when_only_anthropic_key_set(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.setenv("ANTHROPIC_API_KEY", "anthropic-key")

        # Stub `anthropic` so AnthropicProvider can be instantiated without the SDK.
        fake_anthropic = MagicMock()
        fake_module = types.ModuleType("anthropic")
        fake_module.Anthropic = fake_anthropic  # type: ignore[attr-defined]
        monkeypatch.setitem(sys.modules, "anthropic", fake_module)

        provider = default_provider()

        assert type(provider).__name__ == "AnthropicProvider"

    def test_raises_when_no_keys_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

        with pytest.raises(RuntimeError, match="No LLM provider available"):
            default_provider()


class TestGeminiProvider:
    """Unit tests for GeminiProvider — the SDK is fully mocked."""

    def _install_fake_genai(self, monkeypatch: pytest.MonkeyPatch, response_text: str) -> MagicMock:
        """Install a fake `google.genai` SDK and return the mock client instance."""
        fake_response = MagicMock()
        fake_response.text = response_text

        fake_client = MagicMock()
        fake_client.models.generate_content.return_value = fake_response

        fake_genai_module = MagicMock()
        fake_genai_module.Client.return_value = fake_client

        fake_types_module = types.ModuleType("google.genai.types")
        fake_types_module.GenerateContentConfig = MagicMock()  # type: ignore[attr-defined]

        fake_google = types.ModuleType("google")
        fake_google.genai = fake_genai_module  # type: ignore[attr-defined]

        monkeypatch.setitem(sys.modules, "google", fake_google)
        monkeypatch.setitem(sys.modules, "google.genai", fake_genai_module)
        monkeypatch.setitem(sys.modules, "google.genai.types", fake_types_module)

        return fake_client

    def test_propose_candidates_parses_json_response(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        fake_client = self._install_fake_genai(
            monkeypatch,
            response_text='{"candidates": [{"strategy": "css", "value": "#go", '
            '"confidence": 0.9, "reasoning": "id is stable"}]}',
        )

        from qapulsesk_healer.llm.gemini import GeminiProvider
        from qapulsesk_healer.snapshots.web import WebSnapshot

        provider = GeminiProvider()
        candidates = provider.propose_candidates(
            snapshot=WebSnapshot(raw="<html><body><a id='go'>Go</a></body></html>"),
            original_strategy="css",
            original_value="#stale",
            intent="Go link",
        )

        assert len(candidates) == 1
        assert candidates[0].strategy == "css"
        assert candidates[0].value == "#go"
        assert candidates[0].confidence == 0.9
        fake_client.models.generate_content.assert_called_once()

    def test_missing_api_key_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        self._install_fake_genai(monkeypatch, response_text="{}")

        from qapulsesk_healer.llm.gemini import GeminiProvider

        with pytest.raises(RuntimeError, match="GEMINI_API_KEY is not set"):
            GeminiProvider()
