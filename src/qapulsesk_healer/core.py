"""The Healer — orchestrator that takes a broken locator, captures a snapshot,
asks the LLM for candidates, and tries each one until something matches.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Protocol

from qapulsesk_healer.candidates import HealResult
from qapulsesk_healer.llm import AnthropicProvider, LLMProvider

if TYPE_CHECKING:
    from qapulsesk_healer.snapshots.base import Snapshot

log = logging.getLogger(__name__)


class Adapter(Protocol):
    """Interface every framework adapter must implement.

    Selenium, Playwright, Cypress, Appium all wear a different glove. This
    interface is the smallest set of operations the Healer needs.
    """

    def snapshot(self) -> Snapshot:
        """Return a Snapshot of the current page state."""
        ...

    def find(self, strategy: str, value: str) -> Any:
        """Resolve a locator to an element. Raise if not found."""
        ...


class HealerError(Exception):
    """Base exception for Healer failures."""


class NoCandidateMatched(HealerError):
    """Raised when no LLM-proposed candidate resolved to an element."""

    def __init__(self, result: HealResult) -> None:
        super().__init__(
            f"No candidate matched for intent={result.intent!r} "
            f"(original {result.original_strategy}={result.original_value!r}). "
            f"Tried {len(result.candidates)} candidate(s)."
        )
        self.result = result


class Healer:
    """Coordinates heal attempts across any framework via an Adapter.

    Example:
        >>> from selenium import webdriver
        >>> from qapulsesk_healer import Healer
        >>> from qapulsesk_healer.adapters.selenium import SeleniumAdapter
        >>>
        >>> driver = webdriver.Chrome()
        >>> driver.get("https://example.com")
        >>> healer = Healer(adapter=SeleniumAdapter(driver))
        >>> el = healer.find(by="css", value="#submit", intent="Login submit button")
    """

    def __init__(
        self,
        adapter: Adapter,
        llm: LLMProvider | None = None,
        max_candidates: int = 5,
    ) -> None:
        self._adapter = adapter
        self._llm: LLMProvider = llm if llm is not None else AnthropicProvider()
        self._max_candidates = max_candidates

    def find(self, by: str, value: str, intent: str) -> Any:
        """Find an element, healing the locator if the original fails.

        Args:
            by: The locator strategy as the framework names it
                (e.g. "css", "xpath", "accessibility_id").
            value: The locator value.
            intent: Human-readable description of the element's purpose. The LLM
                uses this to match semantically equivalent elements in the DOM.

        Returns:
            The framework-native element handle.

        Raises:
            NoCandidateMatched: If neither the original locator nor any LLM-proposed
                candidate resolves to an element.
        """
        # 1. Try the original locator first — heal is a fallback, not the default path.
        try:
            return self._adapter.find(strategy=by, value=value)
        except Exception as original_err:  # noqa: BLE001 — adapters raise framework-specific errors
            log.info("Original locator failed (%s=%s): %s", by, value, original_err)

        # 2. Original failed → capture snapshot and ask the LLM.
        result = self.heal(by=by, value=value, intent=intent)

        if not result.healed or result.chosen is None:
            raise NoCandidateMatched(result)

        return self._adapter.find(strategy=result.chosen.strategy, value=result.chosen.value)

    def heal(self, by: str, value: str, intent: str) -> HealResult:
        """Generate ranked candidates and try each one in order.

        This is the lower-level entry point — `find()` is what tests usually call.
        Expose it so users can inspect candidates without raising.
        """
        snapshot = self._adapter.snapshot()
        candidates = self._llm.propose_candidates(
            snapshot=snapshot,
            original_strategy=by,
            original_value=value,
            intent=intent,
            max_candidates=self._max_candidates,
        )

        result = HealResult(
            original_strategy=by,
            original_value=value,
            intent=intent,
            candidates=candidates,
        )

        for idx, candidate in enumerate(result.ranked()):
            try:
                self._adapter.find(strategy=candidate.strategy, value=candidate.value)
            except Exception as err:  # noqa: BLE001
                log.debug("Candidate %s=%s failed: %s", candidate.strategy, candidate.value, err)
                continue
            result.chosen_index = idx
            log.info(
                "Healed locator: %s=%s → %s=%s (confidence=%.2f)",
                by,
                value,
                candidate.strategy,
                candidate.value,
                candidate.confidence,
            )
            return result

        return result
