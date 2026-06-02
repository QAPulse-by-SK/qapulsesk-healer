"""Tests for the locator strategy enums."""
from __future__ import annotations

import pytest

from qapulsesk_healer.strategies import (
    MobileStrategy,
    Platform,
    WebStrategy,
    strategies_for,
)


class TestStrategyEnums:
    def test_platform_values(self) -> None:
        assert Platform.WEB.value == "web"
        assert Platform.IOS.value == "ios"
        assert Platform.ANDROID.value == "android"

    def test_web_strategy_includes_common_choices(self) -> None:
        values = {s.value for s in WebStrategy}
        assert {"css", "xpath", "id", "test_id", "role", "text"} <= values

    def test_mobile_strategy_includes_ios_and_android_specifics(self) -> None:
        values = {s.value for s in MobileStrategy}
        assert {"accessibility_id", "ios_predicate", "android_uiautomator"} <= values


class TestStrategiesFor:
    def test_web_returns_web_strategies(self) -> None:
        allowed = strategies_for(Platform.WEB)
        assert "css" in allowed
        assert "ios_predicate" not in allowed

    def test_ios_returns_ios_strategies(self) -> None:
        allowed = strategies_for(Platform.IOS)
        assert "ios_predicate" in allowed
        assert "ios_class_chain" in allowed
        assert "android_uiautomator" not in allowed

    def test_android_returns_android_strategies(self) -> None:
        allowed = strategies_for(Platform.ANDROID)
        assert "android_uiautomator" in allowed
        assert "ios_predicate" not in allowed

    def test_unknown_platform_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown platform"):
            strategies_for("martian")  # type: ignore[arg-type]
