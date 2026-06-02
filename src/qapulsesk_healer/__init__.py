"""qapulsesk-healer — self-healing locators for Selenium, Cypress, Playwright & Appium.

Part of the QAPulse by SK ecosystem. https://skakarh.com
"""

from qapulsesk_healer.candidates import Candidate, HealResult
from qapulsesk_healer.core import Healer
from qapulsesk_healer.strategies import MobileStrategy, Platform, WebStrategy

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
