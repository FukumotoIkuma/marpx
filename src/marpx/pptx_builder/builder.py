"""Main build_pptx() function and slide background helper."""

from __future__ import annotations

import io
import logging
from pathlib import Path

from pptx import Presentation as PptxPresentation
from pptx.util import Emu

from marpx.models import Background, ElementType, Presentation
from marpx.utils import px_to_emu

from ._helpers import _set_fill_color
from .background import _add_background_image
from .decoration import _add_code_block, _add_fallback_image
from marpx.gradient_utils import render_gradient_png
from .directives import _add_footer, _add_header, _add_page_number
from .image import MissingDependencyError, _add_image
from .table import _add_table
from .text import _add_textbox
from .text_grouping import (
    _add_grouped_textbox,
    _group_adjacent_text_elements,
    _is_groupable_text_element,
)

logger = logging.getLogger(__name__)


def _set_slide_background(
    pptx_slide, background: Background, slide_width_px: float, slide_height_px: float
) -> None:
    """Set solid background color on a slide."""
    if background.background_gradient:
        gradient_bytes = render_gradient_png(
            background.background_gradient,
            max(int(round(slide_width_px)), 1),
            max(int(round(slide_height_px)), 1),
        )
        if gradient_bytes:
            pptx_slide.shapes.add_picture(
                io.BytesIO(gradient_bytes),
                Emu(0),
                Emu(0),
                Emu(px_to_emu(slide_width_px)),
                Emu(px_to_emu(slide_height_px)),
            )
            return
    if background.color and background.color.a > 0:
        bg = pptx_slide.background
        fill = bg.fill
        _set_fill_color(fill, background.color)


def build_pptx(presentation: Presentation, output_path: str | Path) -> Path:
    """Build a PPTX file from a Presentation model.

    Args:
        presentation: Normalized presentation data.
        output_path: Path for the output .pptx file.

    Returns:
        Path to the generated PPTX file.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    pptx = PptxPresentation()
    if presentation.slides:
        slide_sizes = {
            (round(slide.width_px, 4), round(slide.height_px, 4))
            for slide in presentation.slides
        }
        if len(slide_sizes) > 1:
            raise ValueError(
                "PowerPoint does not support mixed slide sizes in one deck."
            )
        first_slide = presentation.slides[0]
        pptx.slide_width = Emu(px_to_emu(first_slide.width_px))
        pptx.slide_height = Emu(px_to_emu(first_slide.height_px))

    for slide_data in presentation.slides:
        # Add blank slide
        layout = pptx.slide_layouts[6]  # Blank layout
        pptx_slide = pptx.slides.add_slide(layout)

        # Handle full-slide fallback
        is_full_slide_fallback = bool(
            slide_data.is_fallback and slide_data.fallback_image_path
        )
        if is_full_slide_fallback:
            img_path = Path(slide_data.fallback_image_path)
            if img_path.exists():
                pptx_slide.shapes.add_picture(
                    str(img_path),
                    Emu(0),
                    Emu(0),
                    Emu(px_to_emu(slide_data.width_px)),
                    Emu(px_to_emu(slide_data.height_px)),
                )
        else:
            # Set background
            _set_slide_background(
                pptx_slide,
                slide_data.background,
                slide_data.width_px,
                slide_data.height_px,
            )

            # Add background images (behind content)
            if slide_data.background.images:
                slide_w_emu = px_to_emu(slide_data.width_px)
                slide_h_emu = px_to_emu(slide_data.height_px)
                for bg_image in slide_data.background.images:
                    try:
                        _add_background_image(
                            pptx_slide,
                            bg_image,
                            slide_w_emu,
                            slide_h_emu,
                        )
                    except Exception as e:
                        logger.warning("Failed to add background image: %s", e)
                        logger.debug(
                            "Failed to process background: %s", e, exc_info=True
                        )

            # Add elements sorted by z-index, grouping adjacent plain text content
            skipped_count = 0
            sorted_elements = sorted(slide_data.elements, key=lambda e: e.z_index)
            for group in _group_adjacent_text_elements(sorted_elements):
                if len(group) > 1 and all(
                    _is_groupable_text_element(el) for el in group
                ):
                    _add_grouped_textbox(pptx_slide, group)
                    continue

                element = group[0]
                try:
                    # Capability-driven dispatch.
                    # The converter pipeline always sets element.capability
                    # via classify_element(), so we dispatch solely on it.
                    if element.capability == "subtree_fallback":
                        _add_fallback_image(pptx_slide, element)
                    elif element.capability == "native":
                        if element.element_type in (
                            ElementType.HEADING,
                            ElementType.PARAGRAPH,
                            ElementType.BLOCKQUOTE,
                            ElementType.DECORATED_BLOCK,
                            ElementType.UNORDERED_LIST,
                            ElementType.ORDERED_LIST,
                        ):
                            _add_textbox(pptx_slide, element)
                        elif element.element_type == ElementType.IMAGE:
                            _add_image(pptx_slide, element)
                        elif element.element_type == ElementType.TABLE:
                            _add_table(pptx_slide, element)
                        elif element.element_type == ElementType.CODE_BLOCK:
                            _add_code_block(pptx_slide, element)
                except MissingDependencyError:
                    raise
                except Exception as e:
                    logger.warning(
                        "Failed to add element %s: %s",
                        element.element_type.value,
                        e,
                    )
                    logger.debug("Failed to build element: %s", e, exc_info=True)
                    skipped_count += 1

            if skipped_count:
                slide_index = presentation.slides.index(slide_data)
                logger.info(
                    "Slide %d: skipped %d element(s)",
                    slide_index + 1,
                    skipped_count,
                )

            # Add directives (header, footer, page number)
            slide_w_emu = px_to_emu(slide_data.width_px)
            slide_h_emu = px_to_emu(slide_data.height_px)

            if slide_data.header_text:
                _add_header(pptx_slide, slide_data.header_text, slide_w_emu)

            if slide_data.footer_text:
                _add_footer(
                    pptx_slide, slide_data.footer_text, slide_w_emu, slide_h_emu
                )

            if slide_data.paginate and slide_data.page_number is not None:
                _add_page_number(
                    pptx_slide,
                    slide_data.page_number,
                    slide_data.page_total,
                    slide_w_emu,
                    slide_h_emu,
                )

        # Add speaker notes
        if slide_data.notes:
            notes_slide = pptx_slide.notes_slide
            notes_tf = notes_slide.notes_text_frame
            notes_tf.text = slide_data.notes

    pptx.save(str(output_path))
    logger.info("PPTX saved: %s", output_path)
    return output_path
