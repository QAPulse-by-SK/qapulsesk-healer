# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Live integration tests against skakarh.com (`tests/integration/test_skakarh_healing.py`),
  gated by `@pytest.mark.integration` and the `ANTHROPIC_API_KEY` environment variable
- Nightly GitHub Actions workflow (`.github/workflows/nightly-integration.yml`)
  that runs the integration suite at 03:30 UTC
- `examples/skakarh_demo.py` — Selenium example against the QAPulse by SK homepage
- `examples/skakarh_playwright_demo.py` — Playwright equivalent
- Lazy `__init__.py` re-exports so coverage measurement is accurate when the
  pytest plugin entry point triggers package import before `coverage.py` activates
- Tests for `llm._parse_candidates`, `llm._build_prompt`, `SeleniumAdapter`,
  `PlaywrightAdapter` (mocked drivers, no network)
- `[tool.coverage.run]` and `[tool.coverage.report]` config in `pyproject.toml`
- Project scaffold for v0.1.0
- `Healer` orchestrator with `Adapter` and `LLMProvider` Protocols
- `AnthropicProvider` backed by Claude Sonnet 4.5
- `WebSnapshot` (HTML minifier) and `MobileSnapshot` (XML minifier for iOS/Android)
- `SeleniumAdapter` — full implementation with convenience strategies (`test_id`, `text`, `role`)
- `PlaywrightAdapter` — full implementation using native Playwright locator API
- `AppiumAdapter` skeleton (scheduled for v0.2.0)
- `CypressAdapter` skeleton (scheduled for v0.3.0)
- pytest plugin with `--qapulsesk-heal` flag and `@pytest.mark.no_heal` marker
- Unit tests for strategies, candidates, snapshots, and core orchestrator
- Selenium example targeting `the-internet.herokuapp.com/login`
- GitHub Actions CI matrix across Python 3.10 / 3.11 / 3.12
- Ruff + mypy + pytest configuration
- `Makefile` with `install`, `test`, `lint`, `format`, `typecheck` targets
- Contribution, security, and issue/PR templates

[Unreleased]: https://github.com/QAPulse-by-SK/qapulsesk-healer/compare/HEAD...HEAD
