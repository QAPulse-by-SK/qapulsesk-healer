"""Mobile (Appium) XML page-source snapshot."""

from __future__ import annotations

from xml.etree import ElementTree as ET

from qapulsesk_healer.snapshots.base import Snapshot
from qapulsesk_healer.strategies import Platform

# Attributes worth keeping on each XML node when sending to the LLM. Bounds and
# coordinate fields are dropped — they're noise for locator generation.
_KEEP_ATTRS_IOS = {
    "name",
    "label",
    "value",
    "type",
    "enabled",
    "visible",
    "accessible",
}
_KEEP_ATTRS_ANDROID = {
    "resource-id",
    "content-desc",
    "text",
    "class",
    "package",
    "checkable",
    "clickable",
    "enabled",
    "focusable",
}


class MobileSnapshot(Snapshot):
    """An Appium XML page source for iOS or Android, minified."""

    def __init__(self, raw: str, platform: Platform) -> None:
        if platform not in (Platform.IOS, Platform.ANDROID):
            raise ValueError("MobileSnapshot requires Platform.IOS or Platform.ANDROID")
        super().__init__(raw=raw, platform=platform)

    @property
    def kind(self) -> str:
        return f"xml-{self.platform.value}"

    def minify(self, max_chars: int = 30_000) -> str:
        keep = _KEEP_ATTRS_IOS if self.platform is Platform.IOS else _KEEP_ATTRS_ANDROID

        try:
            root = ET.fromstring(self.raw)
        except ET.ParseError:
            # Fall back to the raw string truncated — better than nothing.
            return self.raw[:max_chars]

        for elem in root.iter():
            elem.attrib = {k: v for k, v in elem.attrib.items() if k in keep}

        rendered = ET.tostring(root, encoding="unicode")

        if len(rendered) <= max_chars:
            return rendered

        head = rendered[: max_chars // 2]
        tail = rendered[-max_chars // 2 :]
        return f"{head}\n<!-- ...truncated... -->\n{tail}"
