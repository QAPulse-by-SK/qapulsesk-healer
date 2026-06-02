# qapulsesk-healer

> Self-healing locators for Selenium, Cypress, Playwright & Appium. When a locator breaks, an LLM proposes ranked replacements from the live DOM/XML source.

Part of the [**QAPulse by SK**](https://skakarh.com) ecosystem.

[![CI](https://github.com/QAPulse-by-SK/qapulsesk-healer/actions/workflows/ci.yml/badge.svg)](https://github.com/QAPulse-by-SK/qapulsesk-healer/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

---

## The problem

UI tests break when locators break. A button gets a new `id`, a class is renamed, a `data-testid` is removed, an Android `resource-id` shifts after an OS update — and your whole suite goes red overnight, even though the *intent* of every test is still valid.

Most teams fix this with brittle, repetitive maintenance: re-inspect the element, update the page object, re-run, repeat.

## What this does

`qapulsesk-healer` watches your locator failures, captures the current DOM (or Appium XML page source), and asks an LLM to propose ranked replacement locators that match the original intent. You get:

- **Ranked candidates** with confidence + reasoning
- **Cross-platform**: web (Selenium / Playwright / Cypress) and mobile (Appium iOS + Android)
- **Pluggable LLM**: ships with Anthropic Claude; provider interface lets you swap in OpenAI or Gemini
- **pytest plugin**: drop-in auto-retry that heals before failing the test
- **Audit log**: every heal saved as `*.heal.json` for review and future PR auto-patches

## Install

Pick an LLM provider plus a framework adapter. Both are extras:

```bash
# Recommended for new users — Gemini's free tier covers typical workloads
pip install qapulsesk-healer[gemini,selenium]

# Or with Anthropic Claude
pip install qapulsesk-healer[anthropic,selenium]

# Other frameworks
pip install qapulsesk-healer[gemini,playwright]
pip install qapulsesk-healer[gemini,appium]      # mobile (v0.2)
pip install qapulsesk-healer[all]                # everything + dev tooling
```

Set the corresponding API key:

```bash
# Free tier: https://aistudio.google.com/apikey
export GEMINI_API_KEY="..."

# Or paid: https://console.anthropic.com/settings/keys
export ANTHROPIC_API_KEY="sk-ant-..."
```

If **both** are set, the Healer prefers Gemini (free). You can always pass an explicit provider with `Healer(adapter=..., llm=GeminiProvider(...))` to override.

> **Free tier privacy note:** Gemini's free tier logs usage for model improvement. Fine for public sites without sensitive data; use a paid Gemini tier or Anthropic for flows that contain PII.

## Quickstart

### Selenium

```python
from selenium import webdriver
from qapulsesk_healer import Healer
from qapulsesk_healer.adapters.selenium import SeleniumAdapter

driver = webdriver.Chrome()
driver.get("https://example.com/login")

healer = Healer(adapter=SeleniumAdapter(driver))

# Original locator no longer matches the page
element = healer.find(
    by="css",
    value="#submit-btn",
    intent="Login submit button",
)
element.click()
```

### Playwright

```python
from playwright.sync_api import sync_playwright
from qapulsesk_healer import Healer
from qapulsesk_healer.adapters.playwright import PlaywrightAdapter

with sync_playwright() as p:
    page = p.chromium.launch().new_page()
    page.goto("https://example.com/login")

    healer = Healer(adapter=PlaywrightAdapter(page))
    locator = healer.find(by="css", value="#submit-btn", intent="Login submit button")
    locator.click()
```

### Appium (iOS / Android)

```python
from appium import webdriver
from qapulsesk_healer import Healer
from qapulsesk_healer.adapters.appium import AppiumAdapter

driver = webdriver.Remote("http://localhost:4723", options=...)
healer = Healer(adapter=AppiumAdapter(driver))

element = healer.find(
    by="accessibility_id",
    value="login_button",
    intent="Primary login CTA",
)
element.click()
```

## How it works

```
┌────────────────────┐    locator fails    ┌──────────────────┐
│  Your test code    │ ──────────────────► │  Healer.find()   │
└────────────────────┘                     └────────┬─────────┘
                                                    │
                                ┌───────────────────┼───────────────────┐
                                ▼                                       ▼
                       ┌────────────────┐                     ┌──────────────────┐
                       │  Snapshot      │                     │  Original locator│
                       │  (HTML / XML)  │                     │  + intent string │
                       └────────┬───────┘                     └────────┬─────────┘
                                │                                      │
                                └──────────────┬───────────────────────┘
                                               ▼
                                     ┌───────────────────┐
                                     │  LLMProvider      │
                                     │  (Anthropic /     │
                                     │   OpenAI / Gemini)│
                                     └─────────┬─────────┘
                                               ▼
                                  ┌──────────────────────────┐
                                  │  Ranked candidates       │
                                  │  [{locator, strategy,    │
                                  │    confidence, reason}]  │
                                  └─────────┬────────────────┘
                                            ▼
                                  Adapter tries each candidate
                                  in confidence order → returns
                                  first match.
```

## Roadmap

| Version | Frameworks | Status |
|---------|------------|--------|
| v0.1.0  | Selenium, Playwright (web); Gemini + Anthropic providers | 🚧 In progress |
| v0.2.0  | + Appium (iOS, Android)   | 📋 Planned |
| v0.3.0  | + Cypress (via `cy.task` bridge) | 📋 Planned |
| v0.4.0  | Auto-PR healed locators back to POMs | 💡 Idea |
| v0.5.0  | Multi-provider LLM (OpenAI, Ollama, local models) | 💡 Idea |

## Related projects

Part of the QAPulse by SK ecosystem:

- [**qapulsesk-report**](https://github.com/QAPulse-by-SK/QAPulseSK-report) — Dark-theme HTML test reporter with AI failure analysis
- [**qapulsesk-gen**](https://github.com/QAPulse-by-SK/QAPulseSK-gen) — Test generator from HAR or plain English
- [**qapulsesk-assert**](https://github.com/QAPulse-by-SK/QAPulseSK-assert) — Fuzzy, semantic, visual and a11y assertions
- [**selenium-boilerplate**](https://github.com/QAPulse-by-SK/selenium-boilerplate) — Production Selenium + Python POM boilerplate

## Contributing

Issues and PRs welcome. This is an early-stage project — design decisions, naming, and API surface are still in flux. The cleanest way to contribute right now is to open an issue describing a real flaky-locator scenario you've hit, ideally with a minimal HTML/XML snippet.

## License

MIT © 2026 [Shahnawaz Kakarh](https://skakarh.com)
