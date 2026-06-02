"""Appium adapter — scheduled for v0.2.0.

Skeleton in place so the public import path is stable from day one. Mobile
work (iOS XCUITest + Android UiAutomator2) lands in v0.2.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from appium.webdriver.webdriver import WebDriver


class AppiumAdapter:
    """Adapter for Appium drivers (iOS / Android). Not yet implemented."""

    def __init__(self, driver: WebDriver) -> None:
        self._driver = driver
        raise NotImplementedError(
            "AppiumAdapter ships in qapulsesk-healer v0.2.0. "
            "Track progress at https://github.com/QAPulse-by-SK/qapulsesk-healer/issues"
        )

    def snapshot(self) -> Any:
        raise NotImplementedError

    def find(self, strategy: str, value: str) -> Any:
        raise NotImplementedError
