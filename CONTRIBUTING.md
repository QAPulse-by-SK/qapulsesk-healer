# Contributing to qapulsesk-healer

Thanks for considering a contribution! This document covers local setup, branching, commit conventions, and the PR review flow.

## Code of conduct

Be excellent to each other. Disagreements happen — keep them about the code, not the person.

---

## Local development setup

**Prerequisites:** Python 3.10 or newer, `git`, an Anthropic API key (for integration tests only — unit tests run fully offline).

```bash
# 1. Fork on GitHub, then clone your fork
git clone https://github.com/<your-username>/qapulsesk-healer.git
cd qapulsesk-healer

# 2. Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate         # macOS/Linux
# .venv\Scripts\activate           # Windows

# 3. Install in editable mode with all extras + dev tooling
pip install -e ".[selenium,playwright,appium,dev]"
#   ^ shorthand: pip install -r requirements-dev.txt

# 4. Verify the toolchain
make check                         # runs lint + typecheck + unit tests
```

### Why hatchling and not Poetry?

`pyproject.toml` (PEP 621) with the hatchling build backend is the modern Python standard and is what `pip install -e .` understands natively. Poetry adds a lockfile and a parallel CLI — useful for some teams, but redundant here and a footgun if both are present. **Don't add a `poetry.lock` or `pdm.lock`** — `pyproject.toml` is the single source of truth.

### A note on requirements*.txt

`requirements.txt` and `requirements-dev.txt` exist as convenience pointers — they restate dependencies declared in `pyproject.toml`. If you change a dependency, update **both** `pyproject.toml` and `requirements.txt`; CI installs from `pyproject.toml`.

---

## Branching strategy

We use a lightweight **trunk-based** flow.

| Branch | Purpose | Lifetime |
|---|---|---|
| `main` | Always green, always releasable. Protected. | Permanent |
| `feat/<short-name>` | New features | Until merged |
| `fix/<short-name>` | Bug fixes | Until merged |
| `chore/<short-name>` | Tooling, deps, docs-only changes | Until merged |
| `release/v<x.y.z>` | Final QA + version bumps before tagging | Until tagged |

Examples:

```
feat/appium-ios-adapter
fix/heal-result-ranking-stability
chore/bump-anthropic-sdk
release/v0.2.0
```

**Rules:**

1. `main` is **protected** — no direct pushes. Everything goes through a PR.
2. Branches are created **from `main`** and merged back **to `main`** via squash merge (one commit per PR, clean history).
3. Delete branches after merge.
4. Rebase your branch on `main` before requesting review if it's more than a day old.

---

## Commit messages

We follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/):

```
<type>: <short imperative summary>

<optional body — what and why, not how>

<optional footer — closes #123, BREAKING CHANGE: ...>
```

Allowed types: `feat`, `fix`, `chore`, `docs`, `test`, `refactor`, `perf`, `ci`, `build`.

Examples:

```
feat: add Appium iOS adapter with predicate-string support
fix: handle empty <body> in WebSnapshot.minify
docs: clarify ANTHROPIC_API_KEY requirement in README
test: cover HealResult.ranked() stability
```

---

## Pull request flow

1. **Open an issue first** if the change is non-trivial. It avoids wasted work.
2. **Branch from `main`** using the naming convention above.
3. **Add or update tests** — every behavioural change needs a test. Aim for unit tests that mock the LLM and adapter; reserve `@pytest.mark.integration` for tests that hit a real API.
4. **Update `CHANGELOG.md`** under `[Unreleased]` with one line in the appropriate section (`Added`, `Changed`, `Fixed`, `Deprecated`, `Removed`, `Security`).
5. **Run the full check locally:**

   ```bash
   make check
   ```

6. **Open the PR.** Fill in the template; link any related issues.
7. **CI must pass** before review.
8. **Address review comments** by pushing more commits — don't force-push during review unless asked.
9. On approval, the reviewer squash-merges. The PR title becomes the squash-commit subject — keep it Conventional-Commit-formatted.

---

## Coding standards

- **Formatter:** `ruff format` (configured in `pyproject.toml`)
- **Linter:** `ruff check`
- **Type checker:** `mypy --strict`
- **Test runner:** `pytest`
- **Line length:** 100 characters
- **Type hints:** every public function and method is fully annotated
- **Docstrings:** Google style; every public class and module has a top-level docstring

Run everything in one shot:

```bash
make check
```

Auto-fix what's auto-fixable:

```bash
make format
ruff check . --fix
```

---

## Adding a new adapter

A new framework adapter must:

1. Live under `src/qapulsesk_healer/adapters/<framework>.py`
2. Satisfy the `Adapter` Protocol in `core.py` (`snapshot()` and `find(strategy, value)`)
3. Be installable as an extra in `pyproject.toml` (e.g. `qapulsesk-healer[<framework>]`)
4. Ship with an example in `examples/<framework>_demo.py`
5. Have unit tests with a fake driver in `tests/adapters/test_<framework>.py`
6. Be documented in the README's Quickstart section and roadmap table

---

## Releasing (maintainers only)

## Integration tests

Live integration tests (under `tests/integration/`) run the **full heal loop**: real browser, real Anthropic API call, real website. They are gated two ways so they never run by accident:

1. They carry `@pytest.mark.integration`, so they are excluded by `pytest -m "not integration"` (which is what CI's `make test` does).
2. They skip themselves if `ANTHROPIC_API_KEY` is not set.

### Running locally

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
pytest -m integration -v
```

### CI

The `.github/workflows/nightly-integration.yml` workflow runs at 03:30 UTC and can be triggered manually from the Actions tab. The `ANTHROPIC_API_KEY` secret must be set on the repo (Settings → Secrets and variables → Actions). If it's missing the workflow logs a warning and exits cleanly — it never fails the build.

### Why nightly, not per-PR

Live tests hit a real LLM and a real website. Running them on every push would burn API credits and create flakiness from external factors (site downtime, model behaviour changes) that have nothing to do with your code. Nightly gives daily confidence without those costs.

---

## Releasing (maintainers only)

1. Cut a `release/v<x.y.z>` branch from `main`.
2. Bump the version in `src/qapulsesk_healer/__init__.py` and `pyproject.toml`.
3. Move `[Unreleased]` items in `CHANGELOG.md` under a new `[<x.y.z>] - YYYY-MM-DD` heading.
4. Open a PR; merge after CI passes.
5. Tag: `git tag -a v<x.y.z> -m "Release v<x.y.z>"` and `git push --tags`.
6. PyPI publish runs from the tag (see `.github/workflows/release.yml`, ships in a later iteration).

---

## Questions

Open a GitHub Discussion or reach out via [skakarh.com](https://skakarh.com).
