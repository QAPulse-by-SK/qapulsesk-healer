"""Candidate locator and heal-result data structures."""
from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class Candidate(BaseModel):
    """A single proposed replacement locator.

    Attributes:
        strategy: The locator strategy (e.g. "css", "xpath", "accessibility_id").
        value: The locator value itself.
        confidence: Float in [0.0, 1.0] expressing model confidence.
        reasoning: Short LLM explanation for *why* this candidate matches the intent.
    """

    strategy: str
    value: str
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str = ""

    @field_validator("value")
    @classmethod
    def _value_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Candidate.value must be non-empty")
        return v


class HealResult(BaseModel):
    """Result of a heal attempt.

    Attributes:
        original_strategy: The strategy that originally failed.
        original_value: The value that originally failed.
        intent: Human-readable description of what the element does.
        candidates: Ranked replacements, highest confidence first.
        chosen_index: Index into candidates of the one that successfully matched,
            or None if no candidate matched.
    """

    original_strategy: str
    original_value: str
    intent: str
    candidates: list[Candidate] = Field(default_factory=list)
    chosen_index: int | None = None

    @property
    def chosen(self) -> Candidate | None:
        """The candidate that successfully resolved to a real element, if any."""
        if self.chosen_index is None:
            return None
        return self.candidates[self.chosen_index]

    @property
    def healed(self) -> bool:
        """True if a replacement locator successfully matched an element."""
        return self.chosen is not None

    def ranked(self) -> list[Candidate]:
        """Candidates sorted by confidence descending (stable)."""
        return sorted(self.candidates, key=lambda c: c.confidence, reverse=True)
