"""Tests for the LLM provider layer (prompt builder + JSON parser).

These tests cover pure logic only — no real API calls. Integration tests that
hit the real Anthropic API live under the `integration` pytest marker.
"""

from __future__ import annotations

import pytest

from qapulsesk_healer.candidates import Candidate
from qapulsesk_healer.llm import _build_prompt, _parse_candidates
from qapulsesk_healer.snapshots.web import WebSnapshot


class TestBuildPrompt:
    def _snapshot(self) -> WebSnapshot:
        return WebSnapshot(raw='<html><body><button id="x">x</button></body></html>')

    def test_includes_platform_and_strategies(self) -> None:
        prompt = _build_prompt(
            snapshot=self._snapshot(),
            original_strategy="css",
            original_value="#stale",
            intent="Login button",
            max_candidates=3,
        )
        assert "PLATFORM: web" in prompt
        assert "css" in prompt
        assert "test_id" in prompt  # one of the allowed web strategies

    def test_includes_original_locator_and_intent(self) -> None:
        prompt = _build_prompt(
            snapshot=self._snapshot(),
            original_strategy="xpath",
            original_value="//button[@id='x']",
            intent="Primary CTA",
            max_candidates=5,
        )
        assert "xpath" in prompt
        assert "//button[@id='x']" in prompt
        assert "Primary CTA" in prompt

    def test_embeds_minified_page_source(self) -> None:
        prompt = _build_prompt(
            snapshot=self._snapshot(),
            original_strategy="css",
            original_value="#x",
            intent="x",
            max_candidates=3,
        )
        assert 'id="x"' in prompt

    def test_requests_json_only_response(self) -> None:
        prompt = _build_prompt(
            snapshot=self._snapshot(),
            original_strategy="css",
            original_value="#x",
            intent="x",
            max_candidates=3,
        )
        assert "JSON" in prompt
        assert "candidates" in prompt


class TestParseCandidates:
    def test_parses_clean_json(self) -> None:
        text = """{
            "candidates": [
                {"strategy": "css", "value": "#login", "confidence": 0.95, "reasoning": "stable id"},
                {"strategy": "test_id", "value": "login", "confidence": 0.8, "reasoning": "has test id"}
            ]
        }"""
        candidates = _parse_candidates(text)
        assert len(candidates) == 2
        assert candidates[0].strategy == "css"
        assert candidates[0].value == "#login"
        assert candidates[0].confidence == 0.95
        assert candidates[1].strategy == "test_id"

    def test_strips_markdown_code_fences(self) -> None:
        text = """```json
        {"candidates": [{"strategy": "css", "value": "#x", "confidence": 0.5, "reasoning": "y"}]}
        ```"""
        candidates = _parse_candidates(text)
        assert len(candidates) == 1
        assert candidates[0].value == "#x"

    def test_strips_unlabelled_code_fences(self) -> None:
        text = """```
        {"candidates": [{"strategy": "id", "value": "go", "confidence": 0.4, "reasoning": ""}]}
        ```"""
        candidates = _parse_candidates(text)
        assert len(candidates) == 1

    def test_tolerates_surrounding_whitespace(self) -> None:
        text = '\n\n  {"candidates": []}  \n\n'
        candidates = _parse_candidates(text)
        assert candidates == []

    def test_raises_on_invalid_json(self) -> None:
        with pytest.raises(ValueError, match="not valid JSON"):
            _parse_candidates("not json at all")

    def test_raises_when_candidates_not_a_list(self) -> None:
        with pytest.raises(ValueError, match="not a list"):
            _parse_candidates('{"candidates": "oops"}')

    def test_empty_candidates_list_is_valid(self) -> None:
        assert _parse_candidates('{"candidates": []}') == []

    def test_round_trip_with_candidate_objects(self) -> None:
        # The parsed objects should be real Candidate instances with validation applied.
        text = '{"candidates": [{"strategy": "css", "value": "#x", "confidence": 0.7, "reasoning": "r"}]}'
        candidates = _parse_candidates(text)
        assert isinstance(candidates[0], Candidate)
        assert candidates[0].reasoning == "r"
