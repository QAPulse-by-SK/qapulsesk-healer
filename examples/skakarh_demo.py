"""End-to-end Selenium example using skakarh.com.

Targets real, stable elements on the QAPulse by SK homepage. Each `find()` call
is given a deliberately **stale** CSS selector — the original locator no longer
matches the page. The Healer captures the DOM, asks Claude to propose new
locators, and tries each one until something matches.

Run:
    pip install -e ".[selenium]"
    export ANTHROPIC_API_KEY="sk-ant-..."
    python examples/skakarh_demo.py
"""

from __future__ import annotations

import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from qapulsesk_healer import Healer
from qapulsesk_healer.adapters.selenium import SeleniumAdapter

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

URL = "https://www.skakarh.com/"


def main() -> None:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1440,900")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(URL)

        healer = Healer(adapter=SeleniumAdapter(driver))

        # Each call passes a CSS selector that does NOT exist on the page.
        # The Healer should infer the correct one from the intent + DOM.

        subscribe = healer.find(
            by="css",
            value="a.subscribe-btn",  # stale
            intent="The 'Subscribe Free' newsletter CTA in the site header",
        )
        print(f"✓ Subscribe button found: {subscribe.text!r}")

        tagline = healer.find(
            by="css",
            value="h1.site-tagline",  # stale
            intent="The eyebrow tagline heading 'Your weekly signal for QA…'",
        )
        print(f"✓ Tagline found: {tagline.text[:60]!r}")

        all_pill = healer.find(
            by="css",
            value="button.filter-all",  # stale
            intent="The 'All' category filter pill above the latest articles grid",
        )
        print(f"✓ 'All' pill found: {all_pill.text!r}")

        blog_link = healer.find(
            by="css",
            value="a.nav-blog-link",  # stale
            intent="The 'Blog' link in the primary site navigation",
        )
        print(f"✓ Blog nav link found: {blog_link.text!r}")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
