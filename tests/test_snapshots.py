"""Tests for snapshot minification."""
from __future__ import annotations

from qapulsesk_healer.snapshots.mobile import MobileSnapshot
from qapulsesk_healer.snapshots.web import WebSnapshot
from qapulsesk_healer.strategies import Platform


class TestWebSnapshot:
    def test_strips_script_tags(self) -> None:
        html = """
        <html><head><script>alert('boom')</script></head>
        <body><button id="go">Go</button></body></html>
        """
        snap = WebSnapshot(raw=html)
        minified = snap.minify()
        assert "alert" not in minified
        assert "<script>" not in minified
        assert 'id="go"' in minified

    def test_drops_unwanted_attributes(self) -> None:
        html = '<div id="keep" style="color:red" onclick="boom()">x</div>'
        snap = WebSnapshot(raw=html)
        minified = snap.minify()
        assert 'id="keep"' in minified
        assert "style" not in minified
        assert "onclick" not in minified

    def test_keeps_test_attributes(self) -> None:
        html = '<button data-testid="submit" data-cy="go" aria-label="Submit">OK</button>'
        snap = WebSnapshot(raw=html)
        minified = snap.minify()
        assert "data-testid" in minified
        assert "data-cy" in minified
        assert "aria-label" in minified

    def test_truncates_when_too_large(self) -> None:
        big = "<div>x</div>" * 5_000
        snap = WebSnapshot(raw=f"<html><body>{big}</body></html>")
        minified = snap.minify(max_chars=1_000)
        assert len(minified) <= 1_100  # allow room for truncation marker
        assert "truncated" in minified


class TestMobileSnapshot:
    def test_ios_snapshot_keeps_ios_attributes(self) -> None:
        xml = '<XCUIElementTypeButton name="Login" label="Log in" value="" enabled="true"/>'
        snap = MobileSnapshot(raw=xml, platform=Platform.IOS)
        minified = snap.minify()
        assert 'name="Login"' in minified
        assert 'label="Log in"' in minified

    def test_android_snapshot_keeps_android_attributes(self) -> None:
        xml = (
            '<android.widget.Button resource-id="com.app:id/login" '
            'content-desc="Log in" text="Login" class="android.widget.Button"/>'
        )
        snap = MobileSnapshot(raw=xml, platform=Platform.ANDROID)
        minified = snap.minify()
        assert "resource-id" in minified
        assert "content-desc" in minified
