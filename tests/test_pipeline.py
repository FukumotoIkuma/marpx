"""Tests for the pipeline context and related refactoring."""

from __future__ import annotations

from pathlib import Path

import pytest

from marpx.pipeline import ElementRenderInfo, PipelineContext, SlideRenderInfo


class TestElementRenderInfo:
    def test_defaults(self):
        info = ElementRenderInfo(capability="native")
        assert info.capability == "native"
        assert info.reason == ""
        assert info.fallback_image_path is None

    def test_with_fallback_path(self):
        info = ElementRenderInfo(
            capability="subtree_fallback",
            reason="Math expression",
            fallback_image_path="/tmp/fb.png",
        )
        assert info.capability == "subtree_fallback"
        assert info.reason == "Math expression"
        assert info.fallback_image_path == "/tmp/fb.png"


class TestSlideRenderInfo:
    def test_defaults(self):
        info = SlideRenderInfo()
        assert info.is_fallback is False
        assert info.fallback_image_path is None
        assert info.element_render_info == {}

    def test_with_elements(self):
        info = SlideRenderInfo(
            is_fallback=True,
            fallback_image_path="/tmp/slide.png",
            element_render_info={
                0: ElementRenderInfo(capability="native"),
                1: ElementRenderInfo(capability="subtree_fallback"),
            },
        )
        assert info.is_fallback is True
        assert len(info.element_render_info) == 2


class TestPipelineContext:
    def test_basic_construction(self, tmp_path: Path):
        ctx = PipelineContext(
            markdown_path=tmp_path / "test.md",
            output_path=tmp_path / "test.pptx",
            temp_dir=tmp_path / "tmp",
        )
        assert ctx.markdown_path == tmp_path / "test.md"
        assert ctx.presentation is None
        assert ctx.html_path is None
        assert ctx.slide_render_info == {}

    def test_get_slide_info_creates_if_absent(self, tmp_path: Path):
        ctx = PipelineContext(
            markdown_path=tmp_path / "test.md",
            output_path=tmp_path / "test.pptx",
            temp_dir=tmp_path / "tmp",
        )
        info = ctx.get_slide_info(0)
        assert isinstance(info, SlideRenderInfo)
        assert 0 in ctx.slide_render_info
        # Second call returns same instance
        assert ctx.get_slide_info(0) is info

    def test_get_element_info_returns_none_for_missing(self, tmp_path: Path):
        ctx = PipelineContext(
            markdown_path=tmp_path / "test.md",
            output_path=tmp_path / "test.pptx",
            temp_dir=tmp_path / "tmp",
        )
        assert ctx.get_element_info(0, 0) is None

    def test_get_element_info_returns_info(self, tmp_path: Path):
        el_info = ElementRenderInfo(capability="native")
        ctx = PipelineContext(
            markdown_path=tmp_path / "test.md",
            output_path=tmp_path / "test.pptx",
            temp_dir=tmp_path / "tmp",
            slide_render_info={
                0: SlideRenderInfo(element_render_info={2: el_info}),
            },
        )
        assert ctx.get_element_info(0, 2) is el_info
        assert ctx.get_element_info(0, 99) is None
        assert ctx.get_element_info(1, 0) is None


class TestClassifyPresentation:
    """Test the extracted _classify_presentation function."""

    def test_classify_all_native(self):
        from marpx.converter import _classify_presentation
        from marpx.models import Box, Presentation, Slide, SlideElement, ElementType

        slide = Slide(
            width_px=1280,
            height_px=720,
            elements=[
                SlideElement(
                    element_type=ElementType.HEADING,
                    box=Box(x=0, y=0, width=100, height=50),
                ),
                SlideElement(
                    element_type=ElementType.PARAGRAPH,
                    box=Box(x=0, y=50, width=100, height=50),
                ),
            ],
        )
        pres = Presentation(slides=[slide])
        result = _classify_presentation(pres)

        assert 0 in result
        sri = result[0]
        assert sri.is_fallback is False
        assert sri.element_render_info[0].capability == "native"
        assert sri.element_render_info[1].capability == "native"

    def test_classify_with_unsupported(self):
        from marpx.converter import _classify_presentation
        from marpx.models import (
            Box,
            Presentation,
            Slide,
            SlideElement,
            ElementType,
            UnsupportedInfo,
        )

        slide = Slide(
            width_px=1280,
            height_px=720,
            elements=[
                SlideElement(
                    element_type=ElementType.MATH,
                    box=Box(x=0, y=0, width=100, height=50),
                    unsupported_info=UnsupportedInfo(
                        reason="Math expression",
                        tag_name="mjx-container",
                    ),
                ),
            ],
        )
        pres = Presentation(slides=[slide])
        result = _classify_presentation(pres)

        sri = result[0]
        assert sri.element_render_info[0].capability == "subtree_fallback"

    def test_classify_does_not_mutate_model(self):
        from marpx.converter import _classify_presentation
        from marpx.models import Box, Presentation, Slide, SlideElement, ElementType

        slide = Slide(
            width_px=1280,
            height_px=720,
            elements=[
                SlideElement(
                    element_type=ElementType.HEADING,
                    box=Box(x=0, y=0, width=100, height=50),
                ),
            ],
        )
        pres = Presentation(slides=[slide])
        _classify_presentation(pres)

        # Model should NOT be mutated by classify
        assert slide.elements[0].capability is None
        assert slide.is_fallback is False


class TestApplyRenderInfoToModels:
    """Test backward compatibility bridge."""

    def test_applies_capability(self):
        from marpx.converter import _apply_render_info_to_models
        from marpx.models import Box, Presentation, Slide, SlideElement, ElementType

        slide = Slide(
            width_px=1280,
            height_px=720,
            elements=[
                SlideElement(
                    element_type=ElementType.HEADING,
                    box=Box(x=0, y=0, width=100, height=50),
                ),
            ],
        )
        pres = Presentation(slides=[slide])
        sri = {
            0: SlideRenderInfo(
                element_render_info={
                    0: ElementRenderInfo(capability="native"),
                },
            ),
        }
        _apply_render_info_to_models(pres, sri)

        assert slide.elements[0].capability == "native"

    def test_applies_slide_fallback(self):
        from marpx.converter import _apply_render_info_to_models
        from marpx.models import Presentation, Slide

        slide = Slide(width_px=1280, height_px=720)
        pres = Presentation(slides=[slide])
        sri = {0: SlideRenderInfo(is_fallback=True)}
        _apply_render_info_to_models(pres, sri)

        assert slide.is_fallback is True


class TestSyncBrowserManager:
    """Test the context manager for browser lifecycle."""

    def test_context_manager_protocol(self):
        """SyncBrowserManager implements the context manager protocol."""
        from marpx.extractor import SyncBrowserManager

        mgr = SyncBrowserManager()
        assert hasattr(mgr, "__enter__")
        assert hasattr(mgr, "__exit__")


class TestCloseSyncBrowserDeprecation:
    """Test that close_sync_browser emits a deprecation warning."""

    def test_deprecation_warning(self):
        from marpx.extractor import close_sync_browser

        with pytest.warns(DeprecationWarning, match="close_sync_browser"):
            close_sync_browser()
