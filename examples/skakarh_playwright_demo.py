"""End-to-end Playwright example using skakarh.com.

Same scenario as `skakarh_demo.py` but driven by Playwright instead of Selenium —
proves the Healer is framework-agnostic.

Run:
    pip install -e ".[playwright]"
    playwright install chromium
    export ANTHROPIC_API_KEY="sk-ant-..."
    python examples/skakarh_playwright_demo.py
"""

from __future__ import annotations

import logging

from playwright.sync_api import sync_playwright

from qapulsesk_healer import Healer
from qapulsesk_healer.adapters.playwright import PlaywrightAdapter

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

URL = "https://www.skakarh.com/"


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        try:
            page.goto(URL, wait_until="domcontentloaded")

            healer = Healer(adapter=PlaywrightAdapter(page))

            subscribe = healer.find(
                by="css",
                value="a.subscribe-btn",  # stale
                intent="The 'Subscribe Free' newsletter CTA in the site header",
            )
            print(f"✓ Subscribe button found: {subscribe.text_content()!r}")

            tagline = healer.find(
                by="css",
                value="h1.site-tagline",  # stale
                intent="The eyebrow tagline heading 'Your weekly signal for QA…'",
            )
            text = tagline.text_content() or ""
            print(f"✓ Tagline found: {text[:60]!r}")

            all_pill = healer.find(
                by="css",
                value="button.filter-all",  # stale
                intent="The 'All' category filter pill above the latest articles grid",
            )
            print(f"✓ 'All' pill found: {all_pill.text_content()!r}")

        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    main()
