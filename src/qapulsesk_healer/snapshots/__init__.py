"""Snapshot abstractions for web (HTML) and mobile (XML) page sources.

Re-exports are lazy to keep coverage measurement accurate — see the top-level
package docstring for the rationale.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

__all__ = ["MobileSnapshot", "Snapshot", "WebSnapshot"]

if TYPE_CHECKING:
    from qapulsesk_healer.snapshots.base import Snapshot
    from qapulsesk_healer.snapshots.mobile import MobileSnapshot
    from qapulsesk_healer.snapshots.web import WebSnapshot


def __getattr__(name: str) -> Any:
    if name == "Snapshot":
        from qapulsesk_healer.snapshots.base import Snapshot

        return Snapshot
    if name == "WebSnapshot":
        from qapulsesk_healer.snapshots.web import WebSnapshot

        return WebSnapshot
    if name == "MobileSnapshot":
        from qapulsesk_healer.snapshots.mobile import MobileSnapshot

        return MobileSnapshot
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
