"""Tests for SVG/Math/Mermaid quality improvements (Phase 5).

Unit tests for MATH element type, capability classification, and extractor handling.
"""

from __future__ import annotations

from marpx.capabilities import (
    Capability,
    classify_element,
    classify_slide,
    should_fallback_slide,
)
from marpx.models import (
    Box,
    ElementType,
    Slide,
    SlideElement,
    UnsupportedInfo,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_element(
    element_type: ElementType,
    unsupported_info: UnsupportedInfo | None = None,
) -> SlideElement:
    """Create a minimal SlideElement for testing."""
    return SlideElement(
        element_type=element_type,
        box=Box(x=0, y=0, width=100, height=50),
        unsupported_info=unsupported_info,
    )


def _make_slide(
    elements: list[SlideElement] | None = None,
    is_fallback: bool = False,
) -> Slide:
    """Create a minimal Slide for testing."""
    return Slide(
        width_px=1280,
        height_px=720,
        elements=elements or [],
        slide_number=1,
        is_fallback=is_fallback,
    )


# ---------------------------------------------------------------------------
# ElementType - MATH existence
# ---------------------------------------------------------------------------


class TestMathElementType:
    """Verify MATH enum member exists in ElementType."""

    def test_math_type_exists(self) -> None:
        assert hasattr(ElementType, "MATH")
        assert ElementType.MATH.value == "math"

    def test_math_type_is_distinct(self) -> None:
        """MATH should be a separate type, not aliased to UNSUPPORTED."""
        assert ElementType.MATH != ElementType.UNSUPPORTED

    def test_math_in_all_types(self) -> None:
        all_values = {e.value for e in ElementType}
        assert "math" in all_values


# ---------------------------------------------------------------------------
# classify_element - MATH type
# ---------------------------------------------------------------------------


class TestClassifyMathElement:
    """Verify that MATH elements are classified as SUBTREE_FALLBACK."""

    def test_math_returns_subtree_fallback(self) -> None:
        info = UnsupportedInfo(
            reason="Math expression (MathJax)", tag_name="mjx-container"
        )
        element = _make_element(ElementType.MATH, unsupported_info=info)
        decision = classify_element(element)
        assert decision.capability == Capability.SUBTREE_FALLBACK
        assert "Math" in decision.reason

    def test_math_without_info_returns_subtree_fallback(self) -> None:
        element = _make_element(ElementType.MATH)
        decision = classify_element(element)
        assert decision.capability == Capability.SUBTREE_FALLBACK
        assert "Math expression" in decision.reason

    def test_math_is_not_native(self) -> None:
        """MATH should NOT be classified as native."""
        element = _make_element(ElementType.MATH)
        decision = classify_element(element)
        assert decision.capability != Capability.NATIVE


# ---------------------------------------------------------------------------
# Slide with MATH elements
# ---------------------------------------------------------------------------


class TestSlideWithMath:
    """Verify slides with MATH elements behave correctly."""

    def test_slide_with_math_element(self) -> None:
        math_el = _make_element(
            ElementType.MATH,
            UnsupportedInfo(
                reason="Math expression (MathJax)", tag_name="mjx-container"
            ),
        )
        slide = _make_slide([math_el])
        assert len(slide.elements) == 1
        assert slide.elements[0].element_type == ElementType.MATH

    def test_classify_slide_with_math(self) -> None:
        math_el = _make_element(
            ElementType.MATH,
            UnsupportedInfo(reason="Math expression"),
        )
        heading_el = _make_element(ElementType.HEADING)
        slide = _make_slide([heading_el, math_el])
        decisions = classify_slide(slide)
        assert decisions[0].capability == Capability.NATIVE
        assert decisions[1].capability == Capability.SUBTREE_FALLBACK

    def test_single_math_triggers_slide_fallback(self) -> None:
        """A single MATH element = 100% non-native, triggers slide fallback."""
        math_el = _make_element(
            ElementType.MATH,
            UnsupportedInfo(reason="Math expression"),
        )
        slide = _make_slide([math_el])
        assert should_fallback_slide(slide) is True

    def test_math_with_many_native_no_slide_fallback(self) -> None:
        """MATH mixed with many native elements should not trigger slide fallback."""
        elements = [
            _make_element(ElementType.HEADING),
            _make_element(ElementType.PARAGRAPH),
            _make_element(ElementType.PARAGRAPH),
            _make_element(ElementType.TABLE),
            _make_element(
                ElementType.MATH,
                UnsupportedInfo(reason="Math expression"),
            ),
        ]
        slide = _make_slide(elements)
        # 1 out of 5 = 20% non-native, well below 80% threshold
        assert should_fallback_slide(slide) is False


# ---------------------------------------------------------------------------
# _build_slide_element - MATH type handling
# ---------------------------------------------------------------------------


class TestBuildSlideElementMath:
    """Verify _build_slide_element handles MATH type correctly."""

    def test_build_math_element(self) -> None:
        from marpx.extractor import _build_slide_element

        raw = {
            "type": "math",
            "box": {"x": 10, "y": 20, "width": 300, "height": 50},
            "unsupportedInfo": {
                "reason": "Math expression (MathJax)",
                "tagName": "mjx-container",
            },
        }
        element = _build_slide_element(raw)
        assert element.element_type == ElementType.MATH
        assert element.unsupported_info is not None
        assert element.unsupported_info.reason == "Math expression (MathJax)"
        assert element.unsupported_info.tag_name == "mjx-container"

    def test_build_math_element_without_info(self) -> None:
        from marpx.extractor import _build_slide_element

        raw = {
            "type": "math",
            "box": {"x": 0, "y": 0, "width": 100, "height": 40},
        }
        element = _build_slide_element(raw)
        assert element.element_type == ElementType.MATH
        assert element.unsupported_info is not None
        assert element.unsupported_info.reason == "Math expression"
        assert element.unsupported_info.tag_name == "mjx-container"

    def test_build_math_element_box(self) -> None:
        from marpx.extractor import _build_slide_element

        raw = {
            "type": "math",
            "box": {"x": 50.5, "y": 100.3, "width": 250.0, "height": 80.0},
            "unsupportedInfo": {
                "reason": "Math expression (MathJax)",
                "tagName": "mjx-container",
            },
        }
        element = _build_slide_element(raw)
        assert element.box.x == 50.5
        assert element.box.y == 100.3
        assert element.box.width == 250.0
        assert element.box.height == 80.0
