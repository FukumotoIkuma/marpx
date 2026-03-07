"""Unit tests for fallback section selection."""
from __future__ import annotations

from pathlib import Path

import pytest

from marpx.fallback_renderer import _is_content_section, render_fallbacks_sync
from marpx.models import (
    Box,
    ElementType,
    Presentation,
    Slide,
    SlideElement,
    UnsupportedInfo,
)


class TestIsContentSection:
    def test_excludes_advanced_background_section(self) -> None:
        assert _is_content_section(
            parent_tag="BODY",
            parent_has_marpit=False,
            advanced_background_role="background",
        ) is False

    def test_excludes_advanced_background_pseudo_section(self) -> None:
        assert _is_content_section(
            parent_tag="DIV",
            parent_has_marpit=False,
            advanced_background_role="pseudo",
        ) is False

    def test_includes_content_section(self) -> None:
        assert _is_content_section(
            parent_tag="BODY",
            parent_has_marpit=False,
            advanced_background_role="content",
        ) is True

    def test_includes_marpit_parent_section(self) -> None:
        assert _is_content_section(
            parent_tag="SECTION",
            parent_has_marpit=True,
            advanced_background_role=None,
        ) is True


def test_render_fallbacks_rasterizes_inline_svg_without_screenshot(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    html = tmp_path / "input.html"
    html.write_text("<section id='s1'></section>", encoding="utf-8")
    presentation = Presentation(
        slides=[
            Slide(
                width_px=1280,
                height_px=720,
                elements=[
                    SlideElement(
                        element_type=ElementType.UNSUPPORTED,
                        box=Box(x=10, y=20, width=200, height=100),
                        unsupported_info=UnsupportedInfo(
                            reason="Unsupported element: svg",
                            tag_name="svg",
                            svg_markup="<svg xmlns='http://www.w3.org/2000/svg'></svg>",
                        ),
                    )
                ],
            )
        ]
    )

    captured: dict[str, bytes] = {}

    class FakePage:
        async def goto(self, *_args, **_kwargs) -> None:
            return None

        async def wait_for_selector(self, *_args, **_kwargs) -> None:
            return None

    class FakeBrowser:
        async def new_page(self, **_kwargs):
            return FakePage()

        async def close(self) -> None:
            return None

    class FakePlaywright:
        chromium = None

        def __init__(self) -> None:
            self.chromium = self

        async def launch(self):
            return FakeBrowser()

    class FakePlaywrightContext:
        async def __aenter__(self):
            return FakePlaywright()

        async def __aexit__(self, exc_type, exc, tb) -> None:
            return None

    monkeypatch.setattr(
        "marpx.fallback_renderer.async_playwright",
        lambda: FakePlaywrightContext(),
    )
    monkeypatch.setattr(
        "marpx.fallback_renderer.rasterize_svg_to_png",
        lambda data: captured.setdefault("svg", data) or b"PNG",
    )

    async def _unexpected_screenshot(*_args, **_kwargs):
        raise AssertionError("inline SVG should not use screenshot fallback")

    monkeypatch.setattr(
        "marpx.fallback_renderer._screenshot_element",
        _unexpected_screenshot,
    )

    updated = render_fallbacks_sync(html, presentation, tmp_path / "fallbacks")

    element = updated.slides[0].elements[0]
    assert captured["svg"].startswith(b"<svg")
    assert element.unsupported_info is not None
    assert element.unsupported_info.fallback_image_path is not None
    assert Path(element.unsupported_info.fallback_image_path).exists()
