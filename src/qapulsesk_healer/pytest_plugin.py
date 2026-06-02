"""pytest plugin — registered via the `pytest11` entry point in pyproject.toml.

Adds a `--qapulsesk-heal` CLI flag and a `healer` fixture that tests can use to
get a configured Healer for their adapter.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from _pytest.config import Config
    from _pytest.config.argparsing import Parser


def pytest_addoption(parser: Parser) -> None:
    group = parser.getgroup("qapulsesk-healer")
    group.addoption(
        "--qapulsesk-heal",
        action="store_true",
        default=False,
        help="Enable LLM-powered locator healing on element-not-found failures.",
    )
    group.addoption(
        "--qapulsesk-heal-log",
        action="store",
        default=None,
        help="Optional path to write a JSON audit log of heal attempts.",
    )


def pytest_configure(config: Config) -> None:
    config.addinivalue_line(
        "markers",
        "no_heal: disable qapulsesk-healer for this test (used with --qapulsesk-heal).",
    )


@pytest.fixture
def heal_enabled(request: pytest.FixtureRequest) -> bool:
    """True when --qapulsesk-heal is passed and the test isn't marked @no_heal."""
    if request.node.get_closest_marker("no_heal") is not None:
        return False
    return bool(request.config.getoption("--qapulsesk-heal"))
