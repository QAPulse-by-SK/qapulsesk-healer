"""Tests for the Selenium adapter — uses a mocked driver, no real browser."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from qapulsesk_healer.adapters.selenium import SeleniumAdapter, _xpath_literal


class TestSeleniumAdapterSnapshot:
    def test_snapshot_captures_page_source(self) -> None:
        driver = MagicMock()
        driver.page_source = "<html><body>hi</body></html>"
        adapter = SeleniumAdapter(driver=driver)

        snap = adapter.snapshot()

        assert snap.raw == "<html><body>hi</body></html>"
        assert snap.kind == "html"


class TestSeleniumAdapterFind:
    def test_css_strategy_uses_css_selector(self) -> None:
        driver = MagicMock()
        adapter = SeleniumAdapter(driver=driver)

        adapter.find(strategy="css", value="#submit")

        driver.find_element.assert_called_once_with("css selector", "#submit")

    def test_xpath_strategy_uses_xpath(self) -> None:
        driver = MagicMock()
        adapter = SeleniumAdapter(driver=driver)

        adapter.find(strategy="xpath", value="//button[@id='x']")

        driver.find_element.assert_called_once_with("xpath", "//button[@id='x']")

    def test_test_id_strategy_maps_to_data_testid_css(self) -> None:
        driver = MagicMock()
        adapter = SeleniumAdapter(driver=driver)

        adapter.find(strategy="test_id", value="submit-btn")

        driver.find_element.assert_called_once_with("css selector", '[data-testid="submit-btn"]')

    def test_role_strategy_maps_to_role_css(self) -> None:
        driver = MagicMock()
        adapter = SeleniumAdapter(driver=driver)

        adapter.find(strategy="role", value="button")

        driver.find_element.assert_called_once_with("css selector", '[role="button"]')

    def test_text_strategy_builds_xpath(self) -> None:
        driver = MagicMock()
        adapter = SeleniumAdapter(driver=driver)

        adapter.find(strategy="text", value="Sign in")

        args, _ = driver.find_element.call_args
        assert args[0] == "xpath"
        assert "Sign in" in args[1]
        assert "normalize-space" in args[1]

    def test_unsupported_strategy_raises(self) -> None:
        driver = MagicMock()
        adapter = SeleniumAdapter(driver=driver)

        with pytest.raises(ValueError, match="does not support strategy"):
            adapter.find(strategy="banana", value="x")


class TestXpathLiteral:
    def test_string_without_quotes_uses_double(self) -> None:
        assert _xpath_literal("Sign in") == '"Sign in"'

    def test_string_with_double_quotes_uses_single(self) -> None:
        assert _xpath_literal('He said "hi"') == "'He said \"hi\"'"

    def test_string_with_single_quotes_uses_double(self) -> None:
        assert _xpath_literal("it's") == '"it\'s"'

    def test_string_with_both_quote_types_uses_concat(self) -> None:
        result = _xpath_literal('He said "it\'s ok"')
        assert result.startswith("concat(")
        assert result.endswith(")")
