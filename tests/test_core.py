"""Tests for the Healer orchestrator (LLM and adapter are mocked)."""
from __future__ import annotations

from typing import Any

import pytest

from qapulsesk_healer.candidates import Candidate
from qapulsesk_healer.core import Healer, NoCandidateMatched
from qapulsesk_healer.snapshots.web import WebSnapshot


class FakeAdapter:
    """Test double for the Adapter protocol.

    `valid_locators` is the set of (strategy, value) tuples that should resolve.
    Everything else raises LookupError.
    """

    def __init__(self, valid_locators: set[tuple[str, str]], page_html: str = "<html/>") -> None:
        self._valid = valid_locators
        self._page_html = page_html
        self.find_calls: list[tuple[str, str]] = []

    def snapshot(self) -> WebSnapshot:
        return WebSnapshot(raw=self._page_html)

    def find(self, strategy: str, value: str) -> Any:
        self.find_calls.append((strategy, value))
        if (strategy, value) not in self._valid:
            raise LookupError(f"Element not found: {strategy}={value}")
        return f"<element {strategy}={value}>"


class FakeLLM:
    """Test double for LLMProvider — returns a hard-coded candidate list."""

    def __init__(self, candidates: list[Candidate]) -> None:
        self._candidates = candidates
        self.call_count = 0

    def propose_candidates(self, **kwargs: Any) -> list[Candidate]:
        self.call_count += 1
        return self._candidates


class TestHealerFind:
    def test_returns_immediately_when_original_locator_works(self) -> None:
        adapter = FakeAdapter(valid_locators={("css", "#submit")})
        llm = FakeLLM(candidates=[])
        healer = Healer(adapter=adapter, llm=llm)

        result = healer.find(by="css", value="#submit", intent="Submit button")

        assert result == "<element css=#submit>"
        assert llm.call_count == 0, "LLM must not be called when original locator works"

    def test_heals_when_original_fails_and_first_candidate_matches(self) -> None:
        adapter = FakeAdapter(valid_locators={("test_id", "submit")})
        llm = FakeLLM(
            candidates=[
                Candidate(strategy="test_id", value="submit", confidence=0.9, reasoning=""),
                Candidate(strategy="css", value=".btn-primary", confidence=0.5, reasoning=""),
            ]
        )
        healer = Healer(adapter=adapter, llm=llm)

        result = healer.find(by="css", value="#stale", intent="Submit button")

        assert result == "<element test_id=submit>"
        assert llm.call_count == 1
        # First call was the original (failed), then the chosen candidate. Note
        # the chosen candidate is found twice — once during ranking, once during
        # the final find() to return the element.
        assert ("css", "#stale") in adapter.find_calls
        assert ("test_id", "submit") in adapter.find_calls

    def test_falls_back_to_lower_ranked_candidate(self) -> None:
        adapter = FakeAdapter(valid_locators={("css", ".btn-primary")})
        llm = FakeLLM(
            candidates=[
                Candidate(strategy="test_id", value="submit", confidence=0.9, reasoning=""),
                Candidate(strategy="css", value=".btn-primary", confidence=0.5, reasoning=""),
            ]
        )
        healer = Healer(adapter=adapter, llm=llm)

        result = healer.find(by="css", value="#stale", intent="Submit button")

        assert result == "<element css=.btn-primary>"

    def test_raises_when_no_candidate_matches(self) -> None:
        adapter = FakeAdapter(valid_locators=set())
        llm = FakeLLM(
            candidates=[
                Candidate(strategy="css", value="#one", confidence=0.7, reasoning=""),
                Candidate(strategy="css", value="#two", confidence=0.3, reasoning=""),
            ]
        )
        healer = Healer(adapter=adapter, llm=llm)

        with pytest.raises(NoCandidateMatched) as exc_info:
            healer.find(by="css", value="#stale", intent="Submit button")

        result = exc_info.value.result
        assert result.healed is False
        assert len(result.candidates) == 2


class TestHealerHeal:
    def test_heal_returns_result_without_raising_on_failure(self) -> None:
        adapter = FakeAdapter(valid_locators=set())
        llm = FakeLLM(
            candidates=[Candidate(strategy="css", value="#x", confidence=0.5, reasoning="")]
        )
        healer = Healer(adapter=adapter, llm=llm)

        result = healer.heal(by="css", value="#stale", intent="Anything")

        assert result.healed is False
        assert result.chosen is None
        assert len(result.candidates) == 1
