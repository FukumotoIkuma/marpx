"""Unit tests for converter orchestration."""

from __future__ import annotations

from pathlib import Path

import pytest

from marpx.converter import ConversionError, convert
from marpx.models import Box, ElementType, Presentation, Slide, UnsupportedElement
from marpx.pptx_builder.image import MissingDependencyError


def _make_presentation_with_math() -> Presentation:
    return Presentation(
        slides=[
            Slide(
                width_px=1280,
                height_px=720,
                slide_number=0,
                elements=[
                    UnsupportedElement(
                        element_type=ElementType.MATH,
                        box=Box(x=10, y=20, width=100, height=50),
                    )
                ],
            )
        ]
    )


class _FakeBrowserManager:
    """Fake SyncBrowserManager context manager for testing."""

    def __enter__(self):
        return object()  # fake browser

    def __exit__(self, *exc):
        return False


def test_convert_marks_slide_fallback_when_not_prefer_editable(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    markdown = tmp_path / "input.md"
    markdown.write_text("# title\n", encoding="utf-8")
    html = tmp_path / "input.html"
    html.write_text("<section></section>", encoding="utf-8")
    captured_render_info: dict[str, dict] = {}

    monkeypatch.setattr(
        "marpx.converter.SyncBrowserManager",
        _FakeBrowserManager,
    )
    monkeypatch.setattr(
        "marpx.converter.render_to_html",
        lambda *args, **kwargs: html,
    )
    monkeypatch.setattr(
        "marpx.converter.extract_presentation_sync",
        lambda *args, **kwargs: _make_presentation_with_math(),
    )

    def fake_render_fallbacks(
        html_path, presentation, output_dir, fallback_mode, slide_render_info
    ):
        # Capture the slide_render_info to verify is_fallback was set
        captured_render_info["info"] = slide_render_info

    monkeypatch.setattr(
        "marpx.converter.render_fallbacks_sync",
        fake_render_fallbacks,
    )
    monkeypatch.setattr(
        "marpx.converter.build_pptx",
        lambda presentation, output_path, slide_render_info=None: Path(output_path),
    )

    convert(markdown, tmp_path / "out.pptx", prefer_editable=False)

    # With prefer_editable=False, the slide should be marked as fallback
    # because 100% of elements (1 MATH) are non-native (above 80% threshold)
    info = captured_render_info["info"]
    assert info[0].is_fallback is True


def test_convert_respects_prefer_editable(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    markdown = tmp_path / "input.md"
    markdown.write_text("# title\n", encoding="utf-8")
    html = tmp_path / "input.html"
    html.write_text("<section></section>", encoding="utf-8")
    captured_render_info: dict[str, dict] = {}

    monkeypatch.setattr(
        "marpx.converter.SyncBrowserManager",
        _FakeBrowserManager,
    )
    monkeypatch.setattr(
        "marpx.converter.render_to_html",
        lambda *args, **kwargs: html,
    )
    monkeypatch.setattr(
        "marpx.converter.extract_presentation_sync",
        lambda *args, **kwargs: _make_presentation_with_math(),
    )

    def fake_render_fallbacks(
        html_path, presentation, output_dir, fallback_mode, slide_render_info
    ):
        captured_render_info["info"] = slide_render_info

    monkeypatch.setattr(
        "marpx.converter.render_fallbacks_sync",
        fake_render_fallbacks,
    )
    monkeypatch.setattr(
        "marpx.converter.build_pptx",
        lambda presentation, output_path, slide_render_info=None: Path(output_path),
    )

    convert(markdown, tmp_path / "out.pptx", prefer_editable=True)

    # With prefer_editable=True, the slide should NOT be marked as fallback
    info = captured_render_info["info"]
    assert info[0].is_fallback is False


def test_convert_rejects_invalid_fallback_mode(tmp_path: Path) -> None:
    markdown = tmp_path / "input.md"
    markdown.write_text("# title\n", encoding="utf-8")

    with pytest.raises(ConversionError, match="Invalid fallback mode"):
        convert(markdown, tmp_path / "out.pptx", fallback_mode="invalid")


def test_convert_surfaces_missing_svg_dependency(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    markdown = tmp_path / "input.md"
    markdown.write_text("# title\n", encoding="utf-8")
    html = tmp_path / "input.html"
    html.write_text("<section></section>", encoding="utf-8")

    monkeypatch.setattr(
        "marpx.converter.SyncBrowserManager",
        _FakeBrowserManager,
    )
    monkeypatch.setattr(
        "marpx.converter.render_to_html",
        lambda *args, **kwargs: html,
    )
    monkeypatch.setattr(
        "marpx.converter.extract_presentation_sync",
        lambda *args, **kwargs: Presentation(slides=[]),
    )
    monkeypatch.setattr(
        "marpx.converter.render_fallbacks_sync",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        "marpx.converter.build_pptx",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            MissingDependencyError("SVG images require `rsvg-convert`")
        ),
    )

    with pytest.raises(ConversionError, match="rsvg-convert"):
        convert(markdown, tmp_path / "out.pptx")
