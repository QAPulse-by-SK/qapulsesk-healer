"""Integration tests that exercise the full heal loop against skakarh.com.

These tests are heavyweight by design:
- They start a real Chromium browser via Selenium.
- They hit https://www.skakarh.com and load real HTML.
- They make real Anthropic API calls (each test costs a small amount of tokens).

They are NEVER run by default. They run only when BOTH:
  1. `ANTHROPIC_API_KEY` is set in the environment, AND
  2. pytest is invoked with `-m integration`.

CI runs them on a nightly cron via .github/workflows/nightly-integration.yml.
Locally:

    ANTHROPIC_API_KEY=sk-ant-... pytest -m integration -v
"""

from __future__ import annotations

import os

import pytest

# Skip the entire module if heavy dependencies aren't installed. We do this at
# import time so a `pip install -e ".[dev]"` (without `[selenium]`) doesn't blow
# up the test collection phase.
pytest.importorskip("selenium")
webdriver_module = pytest.importorskip("selenium.webdriver")

from selenium.webdriver.chrome.options import Options  # noqa: E402

from qapulsesk_healer import Healer  # noqa: E402
from qapulsesk_healer.adapters.selenium import SeleniumAdapter  # noqa: E402

URL = "https://www.skakarh.com/"

# Mark every test in this module as 'integration'. `-m integration` opts in;
# `-m "not integration"` (CI default) opts out.
pytestmark = pytest.mark.integration


def _api_key_missing() -> bool:
    return not os.environ.get("ANTHROPIC_API_KEY")


@pytest.fixture(scope="module")
def driver():  # type: ignore[no-untyped-def]
    """One headless Chrome for the whole module — minimise startup cost."""
    if _api_key_missing():
        pytest.skip("ANTHROPIC_API_KEY not set; skipping live integration tests.")

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1440,900")
    drv = webdriver_module.Chrome(options=options)
    drv.set_page_load_timeout(30)

    try:
        drv.get(URL)
        yield drv
    finally:
        drv.quit()


@pytest.fixture(scope="module")
def healer(driver):  # type: ignore[no-untyped-def]
    return Healer(adapter=SeleniumAdapter(driver))


class TestSkakarhHealing:
    """End-to-end: stale CSS selector + correct intent → working element."""

    def test_heals_subscribe_button(self, healer) -> None:  # type: ignore[no-untyped-def]
        element = healer.find(
            by="css",
            value="a.subscribe-btn",  # does not exist
            intent="The 'Subscribe Free' newsletter CTA in the site header",
        )
        # Whatever locator the LLM picked, it must have landed on the right thing.
        assert "Subscribe" in element.text

    def test_heals_tagline_heading(self, healer) -> None:  # type: ignore[no-untyped-def]
        element = healer.find(
            by="css",
            value="h1.site-tagline",  # does not exist
            intent=(
                "The eyebrow tagline heading at the top of the homepage that reads "
                "'Your weekly signal for QA, Test Automation & AI in Software Engineering'"
            ),
        )
        assert "QA" in element.text.upper()

    def test_heals_category_filter_pill(self, healer) -> None:  # type: ignore[no-untyped-def]
        element = healer.find(
            by="css",
            value="button.filter-all",  # does not exist
            intent="The 'All' category filter pill above the latest articles grid",
        )
        assert element.text.strip().lower() == "all"

    def test_original_locator_still_works_when_present(self, healer) -> None:  # type: ignore[no-untyped-def]
        # If the original locator works, no LLM call should be needed.
        element = healer.find(
            by="css",
            value="a.nav-subscribe",  # this DOES exist
            intent="Subscribe link",
        )
        assert "Subscribe" in element.text
