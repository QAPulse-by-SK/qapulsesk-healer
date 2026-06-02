# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Multi-provider LLM support.** Refactored `llm.py` into a `qapulsesk_healer.llm`
  package: `base.py` (Protocol + prompt + parser + `default_provider()` factory),
  `anthropic.py` (existing AnthropicProvider), `gemini.py` (new GeminiProvider)
- `GeminiProvider` backed by `google-genai` SDK, defaults to `gemini-2.5-flash`,
  uses `response_mime_type="application/json"` for strict JSON output
- `default_provider()` factory: prefers `GEMINI_API_KEY` (free tier) over
  `ANTHROPIC_API_KEY`, raises a helpful `RuntimeError` if neither is set
- New `[gemini]` and `[anthropic]` install extras; SDK dependencies are now
  opt-in per provider (no more eager `anthropic` install for users on Gemini)
- Tests for `default_provider` priority order and `GeminiProvider` (mocked SDK)
- Live integration tests against skakarh.com (`tests/integration/test_skakarh_healing.py`),
  gated by `@pytest.mark.integration` and either `GEMINI_API_KEY` or `ANTHROPIC_API_KEY`
- Nightly GitHub Actions workflow (`.github/workflows/nightly-integration.yml`)
  that runs the integration suite at 03:30 UTC, prefers `GEMINI_API_KEY` secret
- `examples/skakarh_demo.py` and `examples/skakarh_playwright_demo.py`
- Lazy `__init__.py` re-exports so coverage measurement is accurate when the
  pytest plugin entry point triggers package import before `coverage.py` activates
- Tests for `llm.base._parse_candidates`, `_build_prompt`, `SeleniumAdapter`,
  `PlaywrightAdapter` (mocked drivers, no network)
- `[tool.coverage.run]` and `[tool.coverage.report]` config in `pyproject.toml`

### Changed
- `Healer.__init__` now calls `default_provider()` instead of hard-wiring
  `AnthropicProvider()`. Users on the previous Anthropic-only setup are
  unaffected as long as `ANTHROPIC_API_KEY` remains set.
- `anthropic` SDK moved from base dependencies to the `[anthropic]` extra.
  **Breaking** for anyone importing `from qapulsesk_healer.llm import AnthropicProvider`
  without installing `[anthropic]` — install the extra to restore.

### Scaffold (initial)
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
