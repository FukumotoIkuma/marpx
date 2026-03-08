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
        assert (
            _is_content_section(
                parent_tag="BODY",
                parent_has_marpit=False,
                advanced_background_role="background",
            )
            is False
        )

    def test_excludes_advanced_background_pseudo_section(self) -> None:
        assert (
            _is_content_section(
                parent_tag="DIV",
                parent_has_marpit=False,
                advanced_background_role="pseudo",
            )
            is False
        )

    def test_includes_content_section(self) -> None:
        assert (
            _is_content_section(
                parent_tag="BODY",
                parent_has_marpit=False,
                advanced_background_role="content",
            )
            is True
        )

    def test_includes_marpit_parent_section(self) -> None:
        assert (
            _is_content_section(
                parent_tag="SECTION",
                parent_has_marpit=True,
                advanced_background_role=None,
            )
            is True
        )


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

    captured: dict[str, object] = {}
    style_tags: list[str] = []

    class FakePage:
        async def goto(self, *_args, **_kwargs) -> None:
            return None

        async def wait_for_selector(self, *_args, **_kwargs) -> None:
            return None

        async def add_style_tag(self, *, content: str) -> None:
            style_tags.append(content)

        async def wait_for_function(self, *_args, **_kwargs) -> None:
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
        lambda data, width_px=None, height_px=None, scale=1.0: (
            captured.update(
                {
                    "svg": data,
                    "width_px": width_px,
                    "height_px": height_px,
                    "scale": scale,
                }
            )
            or b"PNG"
        ),
    )

    async def _unexpected_screenshot(*_args, **_kwargs):
        raise AssertionError("inline SVG should not use screenshot fallback")

    monkeypatch.setattr(
        "marpx.fallback_renderer._screenshot_element",
        _unexpected_screenshot,
    )

    updated = render_fallbacks_sync(html, presentation, tmp_path / "fallbacks")

    element = updated.slides[0].elements[0]
    assert isinstance(captured["svg"], bytes)
    assert b"svg" in captured["svg"]
    assert b'width="200.000px"' in captured["svg"]
    assert b'height="100.000px"' in captured["svg"]
    assert captured["width_px"] == 200
    assert captured["height_px"] == 100
    assert captured["scale"] == 2.0
    assert any(".bespoke-marp-osc" in content for content in style_tags)
    assert element.unsupported_info is not None
    assert element.unsupported_info.fallback_image_path is not None
    assert Path(element.unsupported_info.fallback_image_path).exists()


def test_render_fallbacks_navigates_to_target_slide_before_screenshot(
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
                        element_type=ElementType.MATH,
                        box=Box(x=10, y=20, width=200, height=100),
                    )
                ],
            )
        ]
    )

    navigate_calls: list[int] = []

    class FakePage:
        async def goto(self, *_args, **_kwargs) -> None:
            return None

        async def wait_for_selector(self, *_args, **_kwargs) -> None:
            return None

        async def add_style_tag(self, **_kwargs) -> None:
            return None

        async def wait_for_function(self, *_args, **_kwargs) -> None:
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

    async def _fake_screenshot_element(*_args, **_kwargs):
        path = tmp_path / "fallbacks" / "slide_0_el_0_fallback.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"PNG")
        return path

    monkeypatch.setattr(
        "marpx.fallback_renderer._screenshot_element",
        _fake_screenshot_element,
    )

    async def _fake_navigate(_page, slide_index: int) -> None:
        navigate_calls.append(slide_index)

    monkeypatch.setattr(
        "marpx.fallback_renderer._navigate_to_slide",
        _fake_navigate,
    )

    updated = render_fallbacks_sync(html, presentation, tmp_path / "fallbacks")

    assert navigate_calls == [0]
    assert (
        updated.slides[0].elements[0].unsupported_info is not None
        and updated.slides[0].elements[0].unsupported_info.fallback_image_path
    )
