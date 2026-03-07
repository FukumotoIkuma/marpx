"""Tests for the capability classifier module."""

from __future__ import annotations

import pytest

from marpx.capabilities import (
    Capability,
    CapabilityDecision,
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
# CapabilityDecision
# ---------------------------------------------------------------------------


class TestCapabilityDecision:
    def test_repr_without_reason(self) -> None:
        d = CapabilityDecision(Capability.NATIVE)
        assert "native" in repr(d)
        assert "reason" not in repr(d)

    def test_repr_with_reason(self) -> None:
        d = CapabilityDecision(Capability.SUBTREE_FALLBACK, reason="svg element")
        assert "subtree_fallback" in repr(d)
        assert "svg element" in repr(d)


# ---------------------------------------------------------------------------
# classify_element - native types
# ---------------------------------------------------------------------------

_NATIVE_TYPES = [
    ElementType.HEADING,
    ElementType.PARAGRAPH,
    ElementType.BLOCKQUOTE,
    ElementType.UNORDERED_LIST,
    ElementType.ORDERED_LIST,
    ElementType.CODE_BLOCK,
    ElementType.IMAGE,
    ElementType.TABLE,
]


class TestClassifyElementNative:
    @pytest.mark.parametrize(
        "etype", _NATIVE_TYPES, ids=[e.value for e in _NATIVE_TYPES]
    )
    def test_native_element_types(self, etype: ElementType) -> None:
        element = _make_element(etype)
        decision = classify_element(element)
        assert decision.capability == Capability.NATIVE
        assert decision.reason == ""


# ---------------------------------------------------------------------------
# classify_element - unsupported / subtree fallback
# ---------------------------------------------------------------------------


class TestClassifyElementUnsupported:
    def test_unsupported_without_info(self) -> None:
        element = _make_element(ElementType.UNSUPPORTED)
        decision = classify_element(element)
        assert decision.capability == Capability.SUBTREE_FALLBACK
        assert decision.reason == ""

    def test_unsupported_with_reason(self) -> None:
        info = UnsupportedInfo(reason="SVG graphic", tag_name="svg")
        element = _make_element(ElementType.UNSUPPORTED, unsupported_info=info)
        decision = classify_element(element)
        assert decision.capability == Capability.SUBTREE_FALLBACK
        assert decision.reason == "SVG graphic"

    def test_unsupported_with_empty_reason(self) -> None:
        info = UnsupportedInfo(reason="", tag_name="div")
        element = _make_element(ElementType.UNSUPPORTED, unsupported_info=info)
        decision = classify_element(element)
        assert decision.capability == Capability.SUBTREE_FALLBACK
        assert decision.reason == ""


# ---------------------------------------------------------------------------
# classify_slide
# ---------------------------------------------------------------------------


class TestClassifySlide:
    def test_empty_slide(self) -> None:
        slide = _make_slide()
        decisions = classify_slide(slide)
        assert decisions == {}

    def test_all_native(self) -> None:
        elements = [
            _make_element(ElementType.HEADING),
            _make_element(ElementType.PARAGRAPH),
            _make_element(ElementType.TABLE),
        ]
        slide = _make_slide(elements)
        decisions = classify_slide(slide)
        assert len(decisions) == 3
        assert all(d.capability == Capability.NATIVE for d in decisions.values())

    def test_all_unsupported(self) -> None:
        elements = [
            _make_element(ElementType.UNSUPPORTED, UnsupportedInfo(reason="svg")),
            _make_element(ElementType.UNSUPPORTED, UnsupportedInfo(reason="math")),
        ]
        slide = _make_slide(elements)
        decisions = classify_slide(slide)
        assert len(decisions) == 2
        assert all(
            d.capability == Capability.SUBTREE_FALLBACK for d in decisions.values()
        )

    def test_mixed_elements(self) -> None:
        elements = [
            _make_element(ElementType.HEADING),
            _make_element(ElementType.UNSUPPORTED, UnsupportedInfo(reason="mermaid")),
            _make_element(ElementType.PARAGRAPH),
        ]
        slide = _make_slide(elements)
        decisions = classify_slide(slide)
        assert decisions[0].capability == Capability.NATIVE
        assert decisions[1].capability == Capability.SUBTREE_FALLBACK
        assert decisions[1].reason == "mermaid"
        assert decisions[2].capability == Capability.NATIVE

    def test_index_mapping_is_correct(self) -> None:
        elements = [
            _make_element(ElementType.IMAGE),
            _make_element(ElementType.CODE_BLOCK),
        ]
        slide = _make_slide(elements)
        decisions = classify_slide(slide)
        assert set(decisions.keys()) == {0, 1}


# ---------------------------------------------------------------------------
# should_fallback_slide
# ---------------------------------------------------------------------------


class TestShouldFallbackSlide:
    def test_empty_slide_no_fallback(self) -> None:
        slide = _make_slide()
        assert should_fallback_slide(slide) is False

    def test_is_fallback_flag(self) -> None:
        slide = _make_slide(is_fallback=True)
        assert should_fallback_slide(slide) is True

    def test_all_native_no_fallback(self) -> None:
        elements = [
            _make_element(ElementType.HEADING),
            _make_element(ElementType.PARAGRAPH),
            _make_element(ElementType.TABLE),
        ]
        slide = _make_slide(elements)
        assert should_fallback_slide(slide) is False

    def test_all_unsupported_triggers_fallback(self) -> None:
        """100% unsupported exceeds the 80% threshold."""
        elements = [
            _make_element(ElementType.UNSUPPORTED, UnsupportedInfo(reason="a")),
            _make_element(ElementType.UNSUPPORTED, UnsupportedInfo(reason="b")),
            _make_element(ElementType.UNSUPPORTED, UnsupportedInfo(reason="c")),
        ]
        slide = _make_slide(elements)
        assert should_fallback_slide(slide) is True

    def test_below_threshold_no_fallback(self) -> None:
        """3 native + 1 unsupported = 25% unsupported, well below threshold."""
        elements = [
            _make_element(ElementType.HEADING),
            _make_element(ElementType.PARAGRAPH),
            _make_element(ElementType.TABLE),
            _make_element(ElementType.UNSUPPORTED, UnsupportedInfo(reason="svg")),
        ]
        slide = _make_slide(elements)
        assert should_fallback_slide(slide) is False

    def test_at_threshold_no_fallback(self) -> None:
        """Exactly 80% unsupported should NOT trigger (strictly greater than)."""
        # 4 unsupported + 1 native = 80% unsupported
        elements = [
            _make_element(ElementType.HEADING),
            _make_element(ElementType.UNSUPPORTED, UnsupportedInfo(reason="a")),
            _make_element(ElementType.UNSUPPORTED, UnsupportedInfo(reason="b")),
            _make_element(ElementType.UNSUPPORTED, UnsupportedInfo(reason="c")),
            _make_element(ElementType.UNSUPPORTED, UnsupportedInfo(reason="d")),
        ]
        slide = _make_slide(elements)
        assert should_fallback_slide(slide) is False

    def test_above_threshold_triggers_fallback(self) -> None:
        """5 unsupported + 1 native = ~83% unsupported, above threshold."""
        elements = [
            _make_element(ElementType.HEADING),
            _make_element(ElementType.UNSUPPORTED, UnsupportedInfo(reason="a")),
            _make_element(ElementType.UNSUPPORTED, UnsupportedInfo(reason="b")),
            _make_element(ElementType.UNSUPPORTED, UnsupportedInfo(reason="c")),
            _make_element(ElementType.UNSUPPORTED, UnsupportedInfo(reason="d")),
            _make_element(ElementType.UNSUPPORTED, UnsupportedInfo(reason="e")),
        ]
        slide = _make_slide(elements)
        assert should_fallback_slide(slide) is True

    def test_single_unsupported_element(self) -> None:
        """1 unsupported out of 1 = 100%, triggers fallback."""
        elements = [
            _make_element(ElementType.UNSUPPORTED, UnsupportedInfo(reason="x")),
        ]
        slide = _make_slide(elements)
        assert should_fallback_slide(slide) is True

    def test_single_native_element(self) -> None:
        elements = [_make_element(ElementType.PARAGRAPH)]
        slide = _make_slide(elements)
        assert should_fallback_slide(slide) is False
