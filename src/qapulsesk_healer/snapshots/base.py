"""Abstract base for page snapshots.

A snapshot is whatever representation we hand to the LLM so it can propose
new locators. Web snapshots are minified HTML; mobile snapshots are minified
XML from Appium's `driver.page_source`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from qapulsesk_healer.strategies import Platform


class Snapshot(ABC):
    """A minified, LLM-friendly view of the current page."""

    def __init__(self, raw: str, platform: Platform) -> None:
        self.raw = raw
        self.platform = platform

    @abstractmethod
    def minify(self, max_chars: int = 30_000) -> str:
        """Return a compact representation safe to embed in an LLM prompt."""

    @property
    @abstractmethod
    def kind(self) -> str:
        """Short label describing the snapshot kind (e.g. 'html', 'xml-ios')."""
