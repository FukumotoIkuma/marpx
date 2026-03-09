"""Pipeline-scoped render information for the conversion pipeline.

These data structures carry rendering decisions (capability classification,
fallback image paths) that are determined during the pipeline but do NOT
belong on the domain models themselves.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from marpx.capabilities import Capability


@dataclass
class ElementRenderInfo:
    """Rendering decision for a single element within a slide."""

    capability: Capability
    fallback_image_path: str | None = None


@dataclass
class SlideRenderInfo:
    """Rendering decisions for an entire slide."""

    is_fallback: bool = False
    fallback_image_path: str | None = None
    element_info: dict[int, ElementRenderInfo] = field(default_factory=dict)
