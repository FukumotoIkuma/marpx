"""Pipeline context and rendering metadata for the marpx conversion pipeline.

Separates rendering decisions (capability classification, fallback paths)
from the extracted data models, enabling a cleaner pipeline where each stage
produces metadata without mutating the shared Presentation model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from marpx.models import Presentation


@dataclass
class ElementRenderInfo:
    """Rendering decisions for a single element, separate from extracted data."""

    capability: str  # "native", "subtree_fallback", or "slide_fallback"
    reason: str = ""
    fallback_image_path: str | None = None


@dataclass
class SlideRenderInfo:
    """Rendering decisions for a slide."""

    is_fallback: bool = False
    fallback_image_path: str | None = None
    element_render_info: dict[int, ElementRenderInfo] = field(default_factory=dict)


@dataclass
class PipelineContext:
    """Context passed through pipeline stages.

    Holds paths, the extracted presentation, and per-slide/per-element
    rendering metadata produced by the classification and fallback stages.
    """

    markdown_path: Path
    output_path: Path
    temp_dir: Path
    html_path: Path | None = None
    presentation: Presentation | None = None
    slide_render_info: dict[int, SlideRenderInfo] = field(default_factory=dict)

    def get_slide_info(self, slide_index: int) -> SlideRenderInfo:
        """Return the SlideRenderInfo for *slide_index*, creating it if absent."""
        if slide_index not in self.slide_render_info:
            self.slide_render_info[slide_index] = SlideRenderInfo()
        return self.slide_render_info[slide_index]

    def get_element_info(
        self, slide_index: int, element_index: int
    ) -> ElementRenderInfo | None:
        """Return the ElementRenderInfo if it exists, else None."""
        slide_info = self.slide_render_info.get(slide_index)
        if slide_info is None:
            return None
        return slide_info.element_render_info.get(element_index)
