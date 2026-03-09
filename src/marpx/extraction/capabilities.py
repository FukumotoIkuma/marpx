"""Capability classifier for slide elements.

Classifies each slide element into one of three rendering capability levels:
- native: Can be rendered as editable PowerPoint shapes
- subtree_fallback: Cannot be natively rendered; use element-level screenshot
- slide_fallback: The entire slide must be a screenshot (last resort)
"""

from __future__ import annotations

from enum import Enum
from typing import NamedTuple

from marpx.models import (
    ElementType,
    Slide,
    SlideElement,
    UnsupportedElement,
)


class Capability(str, Enum):
    NATIVE = "native"
    SUBTREE_FALLBACK = "subtree_fallback"
    SLIDE_FALLBACK = "slide_fallback"


class CapabilityDecision(NamedTuple):
    """Classification result for an element."""

    capability: Capability
    reason: str = ""

    def __repr__(self) -> str:
        if self.reason:
            return (
                f"CapabilityDecision({self.capability.value!r}, reason={self.reason!r})"
            )
        return f"CapabilityDecision({self.capability.value!r})"


_NATIVE_TYPES: frozenset[ElementType] = frozenset(
    {
        ElementType.HEADING,
        ElementType.PARAGRAPH,
        ElementType.BLOCKQUOTE,
        ElementType.DECORATED_BLOCK,
        ElementType.UNORDERED_LIST,
        ElementType.ORDERED_LIST,
        ElementType.CODE_BLOCK,
        ElementType.IMAGE,
        ElementType.TABLE,
    }
)

# Threshold: if more than this fraction of elements are non-native,
# fall back the entire slide.
_SLIDE_FALLBACK_THRESHOLD: float = 0.8


def classify_element(element: SlideElement) -> CapabilityDecision:
    """Classify a single element's rendering capability."""
    # Native elements
    if element.element_type in _NATIVE_TYPES:
        return CapabilityDecision(Capability.NATIVE)

    # Math elements -> native if LaTeX source available, else subtree fallback
    if element.element_type == ElementType.MATH:
        if (
            isinstance(element, UnsupportedElement)
            and element.unsupported_info
            and element.unsupported_info.latex_source
        ):
            return CapabilityDecision(Capability.NATIVE)
        reason = ""
        if isinstance(element, UnsupportedElement) and element.unsupported_info:
            reason = element.unsupported_info.reason
        return CapabilityDecision(
            Capability.SUBTREE_FALLBACK, reason or "Math expression"
        )

    # Unsupported elements -> subtree fallback
    if element.element_type == ElementType.UNSUPPORTED:
        reason = ""
        if isinstance(element, UnsupportedElement) and element.unsupported_info:
            reason = element.unsupported_info.reason
        return CapabilityDecision(Capability.SUBTREE_FALLBACK, reason)

    return CapabilityDecision(Capability.SUBTREE_FALLBACK, "Unknown element type")


def classify_slide(slide: Slide) -> dict[int, CapabilityDecision]:
    """Classify all elements in a slide.

    Returns:
        Mapping of element index to its capability decision.
    """
    decisions: dict[int, CapabilityDecision] = {}
    for i, element in enumerate(slide.elements):
        decisions[i] = classify_element(element)
    return decisions


def should_fallback_slide(slide: Slide) -> bool:
    """Determine if the entire slide should be a fallback image.

    Returns True only if the slide has critical unsupported content
    that makes subtree fallback insufficient (e.g., complex transforms
    affecting the entire layout).

    Current heuristic: if more than 80% of elements are non-native,
    fall back the entire slide.
    """
    decisions = classify_slide(slide)
    total = len(decisions)
    if total == 0:
        return False

    unsupported_count = sum(
        1 for d in decisions.values() if d.capability != Capability.NATIVE
    )

    if unsupported_count / total > _SLIDE_FALLBACK_THRESHOLD:
        return True

    return False
