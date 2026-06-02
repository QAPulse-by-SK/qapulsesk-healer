"""End-to-end Selenium example.

Demonstrates the Healer recovering from a deliberately stale locator on a
public sandbox site (the-internet.herokuapp.com).

Run:
    pip install qapulsesk-healer[selenium]
    export ANTHROPIC_API_KEY="sk-ant-..."
    python examples/selenium_demo.py
"""

from __future__ import annotations

import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from qapulsesk_healer import Healer
from qapulsesk_healer.adapters.selenium import SeleniumAdapter

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


def main() -> None:
    options = Options()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://the-internet.herokuapp.com/login")

        healer = Healer(adapter=SeleniumAdapter(driver))

        # The real id is "username" — we pretend the test was written against
        # an old "#user-input" selector that no longer exists. The Healer should
        # detect the failure, ask the LLM, and find the field anyway.
        username = healer.find(
            by="css",
            value="#user-input",
            intent="Username text input on the login form",
        )
        username.send_keys("tomsmith")

        password = healer.find(
            by="css",
            value="#pwd",
            intent="Password text input on the login form",
        )
        password.send_keys("SuperSecretPassword!")

        submit = healer.find(
            by="css",
            value="button.login",
            intent="Login submit button",
        )
        submit.click()

        print("Page title after submit:", driver.title)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
