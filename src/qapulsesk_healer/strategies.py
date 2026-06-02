"""Locator strategies for web and mobile platforms.

Each strategy maps to the native locator syntax of the underlying framework
(Selenium / Playwright / Appium). Keeping them as enums lets the LLM emit
typed responses and lets adapters dispatch cleanly.
"""
from __future__ import annotations

from enum import Enum


class Platform(str, Enum):
    """Top-level platform that a Snapshot describes."""

    WEB = "web"
    IOS = "ios"
    ANDROID = "android"


class WebStrategy(str, Enum):
    """Locator strategies valid for Selenium / Playwright / Cypress."""

    CSS = "css"
    XPATH = "xpath"
    ID = "id"
    NAME = "name"
    LINK_TEXT = "link_text"
    PARTIAL_LINK_TEXT = "partial_link_text"
    TAG_NAME = "tag_name"
    CLASS_NAME = "class_name"
    TEXT = "text"
    ROLE = "role"
    TEST_ID = "test_id"


class MobileStrategy(str, Enum):
    """Locator strategies valid for Appium (iOS XCUITest + Android UiAutomator2)."""

    ACCESSIBILITY_ID = "accessibility_id"
    ID = "id"
    XPATH = "xpath"
    CLASS_NAME = "class_name"
    NAME = "name"
    # iOS-specific
    IOS_PREDICATE = "ios_predicate"
    IOS_CLASS_CHAIN = "ios_class_chain"
    # Android-specific
    ANDROID_UIAUTOMATOR = "android_uiautomator"


def strategies_for(platform: Platform) -> list[str]:
    """Return the list of strategy string values appropriate for a platform."""
    if platform is Platform.WEB:
        return [s.value for s in WebStrategy]
    if platform is Platform.IOS:
        return [
            MobileStrategy.ACCESSIBILITY_ID.value,
            MobileStrategy.ID.value,
            MobileStrategy.XPATH.value,
            MobileStrategy.CLASS_NAME.value,
            MobileStrategy.NAME.value,
            MobileStrategy.IOS_PREDICATE.value,
            MobileStrategy.IOS_CLASS_CHAIN.value,
        ]
    if platform is Platform.ANDROID:
        return [
            MobileStrategy.ACCESSIBILITY_ID.value,
            MobileStrategy.ID.value,
            MobileStrategy.XPATH.value,
            MobileStrategy.CLASS_NAME.value,
            MobileStrategy.ANDROID_UIAUTOMATOR.value,
        ]
    raise ValueError(f"Unknown platform: {platform}")
