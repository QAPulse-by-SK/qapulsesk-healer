"""Web HTML snapshot — minifies a page so the LLM sees signal, not noise."""

from __future__ import annotations

from bs4 import BeautifulSoup, Comment

from qapulsesk_healer.snapshots.base import Snapshot
from qapulsesk_healer.strategies import Platform

# Tags whose content is almost never relevant to locator selection.
_STRIP_TAGS = {"script", "style", "noscript", "svg", "path", "meta", "link"}

# Attributes that meaningfully identify or describe an element. Everything
# else gets dropped to shrink the prompt.
_KEEP_ATTRS = {
    "id",
    "class",
    "name",
    "type",
    "role",
    "href",
    "for",
    "value",
    "placeholder",
    "title",
    "alt",
    "aria-label",
    "aria-labelledby",
    "aria-describedby",
    "data-testid",
    "data-test",
    "data-cy",
    "data-qa",
}


class WebSnapshot(Snapshot):
    """An HTML page source, minified for LLM consumption."""

    def __init__(self, raw: str) -> None:
        super().__init__(raw=raw, platform=Platform.WEB)

    @property
    def kind(self) -> str:
        return "html"

    def minify(self, max_chars: int = 30_000) -> str:
        soup = BeautifulSoup(self.raw, "lxml")

        # Drop noisy elements wholesale.
        for tag_name in _STRIP_TAGS:
            for tag in soup.find_all(tag_name):
                tag.decompose()

        # Drop HTML comments.
        for comment in soup.find_all(string=lambda s: isinstance(s, Comment)):
            comment.extract()

        # Prune attributes on every remaining element.
        for tag in soup.find_all(True):
            attrs = dict(tag.attrs)
            tag.attrs = {k: v for k, v in attrs.items() if k in _KEEP_ATTRS}

        rendered = str(soup)

        if len(rendered) <= max_chars:
            return rendered

        # Truncate from the middle so we keep the document head + the page tail.
        head = rendered[: max_chars // 2]
        tail = rendered[-max_chars // 2 :]
        return f"{head}\n<!-- ...truncated... -->\n{tail}"
