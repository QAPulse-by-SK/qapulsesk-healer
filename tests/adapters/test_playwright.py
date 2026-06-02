"""Tests for the Playwright adapter — uses a mocked Page, no real browser."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from qapulsesk_healer.adapters.playwright import PlaywrightAdapter


def _adapter_with_mock_page() -> tuple[PlaywrightAdapter, MagicMock]:
    page = MagicMock()
    # Make page.content() return a string and locator.first.wait_for() a no-op.
    page.content.return_value = "<html/>"
    return PlaywrightAdapter(page=page), page


class TestPlaywrightAdapterSnapshot:
    def test_snapshot_uses_page_content(self) -> None:
        adapter, page = _adapter_with_mock_page()
        page.content.return_value = "<html><body>hi</body></html>"

        snap = adapter.snapshot()

        assert snap.raw == "<html><body>hi</body></html>"
        assert snap.kind == "html"


class TestPlaywrightAdapterFind:
    def test_css_uses_page_locator(self) -> None:
        adapter, page = _adapter_with_mock_page()

        adapter.find(strategy="css", value="#submit")

        page.locator.assert_called_once_with("#submit")

    def test_xpath_uses_xpath_prefix(self) -> None:
        adapter, page = _adapter_with_mock_page()

        adapter.find(strategy="xpath", value="//button")

        page.locator.assert_called_once_with("xpath=//button")

    def test_test_id_uses_get_by_test_id(self) -> None:
        adapter, page = _adapter_with_mock_page()

        adapter.find(strategy="test_id", value="login-btn")

        page.get_by_test_id.assert_called_once_with("login-btn")

    def test_text_uses_get_by_text_exact(self) -> None:
        adapter, page = _adapter_with_mock_page()

        adapter.find(strategy="text", value="Sign in")

        page.get_by_text.assert_called_once_with("Sign in", exact=True)

    def test_role_uses_get_by_role(self) -> None:
        adapter, page = _adapter_with_mock_page()

        adapter.find(strategy="role", value="button")

        page.get_by_role.assert_called_once_with("button")

    def test_id_translates_to_hash_selector(self) -> None:
        adapter, page = _adapter_with_mock_page()

        adapter.find(strategy="id", value="submit")

        page.locator.assert_called_once_with("#submit")

    def test_name_translates_to_attribute_selector(self) -> None:
        adapter, page = _adapter_with_mock_page()

        adapter.find(strategy="name", value="email")

        page.locator.assert_called_once_with('[name="email"]')

    def test_class_name_translates_to_dot_selector(self) -> None:
        adapter, page = _adapter_with_mock_page()

        adapter.find(strategy="class_name", value="btn-primary")

        page.locator.assert_called_once_with(".btn-primary")

    def test_tag_name_uses_tag_selector(self) -> None:
        adapter, page = _adapter_with_mock_page()

        adapter.find(strategy="tag_name", value="button")

        page.locator.assert_called_once_with("button")

    def test_unsupported_strategy_raises(self) -> None:
        adapter, _ = _adapter_with_mock_page()

        with pytest.raises(ValueError, match="does not support strategy"):
            adapter.find(strategy="banana", value="x")

    def test_find_waits_for_element_attached(self) -> None:
        adapter, page = _adapter_with_mock_page()

        adapter.find(strategy="css", value="#submit")

        page.locator.return_value.first.wait_for.assert_called_once_with(
            state="attached", timeout=2_000
        )
