"""qapulsesk-healer — self-healing locators for Selenium, Cypress, Playwright & Appium.

Part of the QAPulse by SK ecosystem. https://skakarh.com

The public re-exports below are lazy: importing the package itself (e.g. when
pytest discovers the `pytest11` entry point in :mod:`qapulsesk_healer.pytest_plugin`)
does not eagerly load `core`, `candidates`, etc. They load only on first
attribute access. This keeps `coverage.py` accurate when measurements start
after the package has been imported.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

__version__ = "0.1.0"

__all__ = [
    "Candidate",
    "HealResult",
    "Healer",
    "MobileStrategy",
    "Platform",
    "WebStrategy",
    "__version__",
]

# Static analysers (mypy, IDEs) see these as normal imports thanks to
# TYPE_CHECKING. At runtime they go through __getattr__ below.
if TYPE_CHECKING:
    from qapulsesk_healer.candidates import Candidate, HealResult
    from qapulsesk_healer.core import Healer
    from qapulsesk_healer.strategies import MobileStrategy, Platform, WebStrategy


def __getattr__(name: str) -> Any:
    """Lazy re-exports — imported on first access, never at package init."""
    if name == "Healer":
        from qapulsesk_healer.core import Healer

        return Healer
    if name == "Candidate":
        from qapulsesk_healer.candidates import Candidate

        return Candidate
    if name == "HealResult":
        from qapulsesk_healer.candidates import HealResult

        return HealResult
    if name == "Platform":
        from qapulsesk_healer.strategies import Platform

        return Platform
    if name == "WebStrategy":
        from qapulsesk_healer.strategies import WebStrategy

        return WebStrategy
    if name == "MobileStrategy":
        from qapulsesk_healer.strategies import MobileStrategy

        return MobileStrategy
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
