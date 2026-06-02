"""Playwright adapter.

Wraps a Playwright Page so the Healer can capture HTML and resolve locators
using Playwright's native locator API.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from qapulsesk_healer.snapshots.web import WebSnapshot

if TYPE_CHECKING:
    from playwright.sync_api import Locator, Page


class PlaywrightAdapter:
    """Adapter that satisfies the Healer's `Adapter` Protocol via Playwright."""

    def __init__(self, page: Page) -> None:
        self._page = page

    def snapshot(self) -> WebSnapshot:
        return WebSnapshot(raw=self._page.content())

    def find(self, strategy: str, value: str) -> Locator:
        """Resolve a locator and verify exactly one element matches.

        Playwright locators are lazy, so we call `.wait_for(state="attached")` to
        materialize the lookup and raise immediately if nothing matches.
        """
        locator: Locator
        if strategy == "css":
            locator = self._page.locator(value)
        elif strategy == "xpath":
            locator = self._page.locator(f"xpath={value}")
        elif strategy == "test_id":
            locator = self._page.get_by_test_id(value)
        elif strategy == "text":
            locator = self._page.get_by_text(value, exact=True)
        elif strategy == "role":
            locator = self._page.get_by_role(value)  # type: ignore[arg-type]
        elif strategy == "id":
            locator = self._page.locator(f"#{value}")
        elif strategy == "name":
            locator = self._page.locator(f'[name="{value}"]')
        elif strategy == "class_name":
            locator = self._page.locator(f".{value}")
        elif strategy == "tag_name":
            locator = self._page.locator(value)
        else:
            raise ValueError(f"PlaywrightAdapter does not support strategy: {strategy!r}")

        locator.first.wait_for(state="attached", timeout=2_000)
        return locator.first
