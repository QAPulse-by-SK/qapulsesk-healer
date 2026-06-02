"""Snapshot abstractions for web (HTML) and mobile (XML) page sources."""
from qapulsesk_healer.snapshots.base import Snapshot
from qapulsesk_healer.snapshots.mobile import MobileSnapshot
from qapulsesk_healer.snapshots.web import WebSnapshot

__all__ = ["MobileSnapshot", "Snapshot", "WebSnapshot"]
