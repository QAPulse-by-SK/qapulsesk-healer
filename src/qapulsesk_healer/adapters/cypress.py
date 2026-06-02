"""Cypress adapter — scheduled for v0.3.0.

Cypress runs in-browser, so integration goes through a `cy.task` JS bridge
rather than a direct Python binding. Skeleton placed here so the import path
is stable from v0.1.0 onward.
"""
from __future__ import annotations

from typing import Any


class CypressAdapter:
    """Adapter that bridges Cypress via `cy.task`. Not yet implemented."""

    def __init__(self) -> None:
        raise NotImplementedError(
            "CypressAdapter ships in qapulsesk-healer v0.3.0. "
            "Track progress at https://github.com/QAPulse-by-SK/qapulsesk-healer/issues"
        )

    def snapshot(self) -> Any:
        raise NotImplementedError

    def find(self, strategy: str, value: str) -> Any:
        raise NotImplementedError
