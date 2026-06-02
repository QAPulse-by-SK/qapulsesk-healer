"""End-to-end Selenium demo against skakarh.com — the QAPulse by SK homepage.

Demonstrates the Healer recovering from deliberately stale CSS selectors. All
operations are read-only: we navigate, find elements, and assert their
identity. No forms are submitted, no newsletter is signed up to, no clicks
that mutate state.

Run:
    pip install qapulsesk-healer[selenium]
    export ANTHROPIC_API_KEY="sk-ant-..."
    python examples/skakarh_selenium_demo.py
"""

from __future__ import annotations

import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from qapulsesk_healer import Healer
from qapulsesk_healer.adapters.selenium import SeleniumAdapter

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

SITE = "https://www.skakarh.com/"


def main() -> None:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1440,900")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(SITE)

        healer = Healer(adapter=SeleniumAdapter(driver))

        # 1) Brand header link — the real anchor has no #brand-link id; the
        #    healer should map intent → the QAPulse by SK header link.
        brand_link = healer.find(
            by="css",
            value="#brand-link",
            intent="QAPulse by SK brand logo link in the site header",
        )
        print(f"[heal-1] brand link text: {brand_link.text!r}")

        # 2) Blog nav item — fake stale class.
        blog_link = healer.find(
            by="css",
            value=".nav-blog-link",
            intent="Blog link in the primary navigation menu",
        )
        print(f"[heal-2] blog link href: {blog_link.get_attribute('href')!r}")

        # 3) Newsletter CTA — fake stale id. Note: we do NOT click it, only locate.
        subscribe_cta = healer.find(
            by="css",
            value="#newsletter-cta",
            intent="Free newsletter subscription call-to-action button",
        )
        print(f"[heal-3] subscribe CTA text: {subscribe_cta.text!r}")

        # 4) Main page heading.
        hero_heading = healer.find(
            by="css",
            value=".hero-title",
            intent="The main h1 heading on the homepage",
        )
        print(f"[heal-4] hero heading: {hero_heading.text!r}")

        print("\nAll four healed locators resolved successfully against skakarh.com.")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
