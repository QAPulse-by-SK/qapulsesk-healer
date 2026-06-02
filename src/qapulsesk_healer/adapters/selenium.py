"""Selenium adapter.

Wraps a Selenium WebDriver so the Healer can capture a page snapshot and
resolve locators in Selenium's native vocabulary.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qapulsesk_healer.snapshots.web import WebSnapshot

if TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver
    from selenium.webdriver.remote.webelement import WebElement

# Map Healer strategy strings to Selenium's `By.*` constants. Imported lazily
# so users who don't `pip install ...[selenium]` still get clean errors.
_BY_MAP: dict[str, str] = {
    "css": "css selector",
    "xpath": "xpath",
    "id": "id",
    "name": "name",
    "link_text": "link text",
    "partial_link_text": "partial link text",
    "tag_name": "tag name",
    "class_name": "class name",
}


class SeleniumAdapter:
    """Adapter that satisfies the Healer's `Adapter` Protocol via Selenium."""

    def __init__(self, driver: WebDriver) -> None:
        self._driver = driver

    def snapshot(self) -> WebSnapshot:
        """Capture the current page as a WebSnapshot."""
        return WebSnapshot(raw=self._driver.page_source)

    def find(self, strategy: str, value: str) -> WebElement:
        """Resolve a locator to a Selenium WebElement.

        For convenience strategies the LLM may propose (`text`, `role`, `test_id`),
        we translate to a CSS or XPath expression that Selenium understands.
        """
        # Convenience strategies → CSS/XPath
        if strategy == "test_id":
            return self._driver.find_element("css selector", f'[data-testid="{value}"]')
        if strategy == "text":
            xpath = f"//*[normalize-space(text())={_xpath_literal(value)}]"
            return self._driver.find_element("xpath", xpath)
        if strategy == "role":
            return self._driver.find_element("css selector", f'[role="{value}"]')

        by = _BY_MAP.get(strategy)
        if by is None:
            raise ValueError(f"SeleniumAdapter does not support strategy: {strategy!r}")
        return self._driver.find_element(by, value)


def _xpath_literal(s: str) -> str:
    """Safely quote a string for embedding in an XPath expression."""
    if '"' not in s:
        return f'"{s}"'
    if "'" not in s:
        return f"'{s}'"
    # Contains both quote types — use concat().
    parts = s.split('"')
    quoted = ", '\"', ".join(f'"{p}"' for p in parts)
    return f"concat({quoted})"
