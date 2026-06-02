"""Tests for the Candidate and HealResult models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from qapulsesk_healer.candidates import Candidate, HealResult


class TestCandidate:
    def test_valid_candidate(self) -> None:
        c = Candidate(strategy="css", value="#login", confidence=0.92, reasoning="stable id")
        assert c.strategy == "css"
        assert c.value == "#login"
        assert c.confidence == 0.92

    def test_confidence_out_of_range_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Candidate(strategy="css", value="#x", confidence=1.5)
        with pytest.raises(ValidationError):
            Candidate(strategy="css", value="#x", confidence=-0.1)

    def test_empty_value_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Candidate(strategy="css", value="   ", confidence=0.5)


class TestHealResult:
    def _result_with_two_candidates(self) -> HealResult:
        return HealResult(
            original_strategy="css",
            original_value="#old",
            intent="Login button",
            candidates=[
                Candidate(strategy="css", value="#new", confidence=0.6, reasoning=""),
                Candidate(strategy="test_id", value="login", confidence=0.9, reasoning=""),
            ],
        )

    def test_healed_false_when_no_chosen_index(self) -> None:
        r = self._result_with_two_candidates()
        assert r.healed is False
        assert r.chosen is None

    def test_healed_true_when_chosen_index_set(self) -> None:
        r = self._result_with_two_candidates()
        r.chosen_index = 1
        assert r.healed is True
        assert r.chosen is not None
        assert r.chosen.value == "login"

    def test_ranked_orders_by_confidence_desc(self) -> None:
        r = self._result_with_two_candidates()
        ranked = r.ranked()
        assert ranked[0].confidence == 0.9
        assert ranked[1].confidence == 0.6
