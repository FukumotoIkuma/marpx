"""Decoration shape rendering for pptx_builder."""
from __future__ import annotations

import logging
from pathlib import Path

from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
from pptx.oxml.ns import qn
from pptx.util import Emu

from marpx.models import Box, BoxDecoration, SlideElement
from marpx.utils import px_to_emu

from ._helpers import _to_rgb, _with_opacity

logger = logging.getLogger(__name__)


def _add_decoration_shape(slide, box: Box, decoration: BoxDecoration):
    """Render a generic decorated box and return it as the text container."""
    left = Emu(px_to_emu(box.x))
    top = Emu(px_to_emu(box.y))
    width = Emu(px_to_emu(box.width))
    height = Emu(px_to_emu(box.height))

    shape_type = (
        MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE
        if decoration.border_radius_px > 0
        else MSO_AUTO_SHAPE_TYPE.RECTANGLE
    )
    bg_shape = slide.shapes.add_shape(shape_type, left, top, width, height)
    _remove_theme_style(bg_shape)

    fill = bg_shape.fill
    if decoration.background_color and decoration.opacity > 0:
        fill_color = _with_opacity(decoration.background_color, decoration.opacity)
        fill.solid()
        fill.fore_color.rgb = _to_rgb(fill_color)
    else:
        fill.background()

    uniform_border = _detect_uniform_border(decoration)
    if uniform_border:
        border_color = _with_opacity(uniform_border.color, decoration.opacity)
        if border_color.a > 0:
            bg_shape.line.color.rgb = _to_rgb(border_color)
            bg_shape.line.width = Emu(px_to_emu(uniform_border.width_px))
        else:
            bg_shape.line.fill.background()
    else:
        bg_shape.line.fill.background()

    accent_border = decoration.border_left
    if (
        accent_border.width_px > 0
        and accent_border.color is not None
        and decoration.opacity > 0
        and _is_left_accent_only(decoration)
    ):
        accent_left, accent_top, accent_width, accent_height = (
            _resolve_left_accent_geometry(box, decoration)
        )
        accent_shape = slide.shapes.add_shape(
            MSO_AUTO_SHAPE_TYPE.RECTANGLE,
            accent_left,
            accent_top,
            accent_width,
            accent_height,
        )
        _remove_theme_style(accent_shape)
        accent_color = _with_opacity(accent_border.color, decoration.opacity)
        accent_shape.fill.solid()
        accent_shape.fill.fore_color.rgb = _to_rgb(accent_color)
        accent_shape.line.fill.background()

    return bg_shape


def _remove_theme_style(shape) -> None:
    """Remove theme style refs that can introduce unwanted effects like shadows."""
    style = shape._element.find(qn("p:style"))
    if style is not None:
        shape._element.remove(style)


def _detect_uniform_border(decoration: BoxDecoration):
    """Return a representative border side when all visible sides are equal."""
    sides = [
        decoration.border_top,
        decoration.border_right,
        decoration.border_bottom,
        decoration.border_left,
    ]
    visible = [
        side for side in sides
        if side.width_px > 0 and side.style and side.style != "none" and side.color
    ]
    if not visible:
        return None
    first = visible[0]
    if all(
        side.width_px == first.width_px
        and side.style == first.style
        and side.color == first.color
        for side in visible
    ) and len(visible) == 4:
        return first
    return None


def _is_left_accent_only(decoration: BoxDecoration) -> bool:
    """Return True when only the left border should be rendered as an accent bar."""
    other_sides = [
        decoration.border_top,
        decoration.border_right,
        decoration.border_bottom,
    ]
    return all(
        side.width_px == 0 or side.style == "none" or side.color is None
        for side in other_sides
    )


def _resolve_left_accent_geometry(
    box: Box,
    decoration: BoxDecoration,
) -> tuple[Emu, Emu, Emu, Emu]:
    """Match the visible straight segment of a left border on rounded boxes."""
    radius_px = max(decoration.border_radius_px, 0.0)
    vertical_inset_px = min(radius_px, box.height / 2)
    accent_height_px = max(box.height - (vertical_inset_px * 2), 1.0)

    return (
        Emu(px_to_emu(box.x)),
        Emu(px_to_emu(box.y + vertical_inset_px)),
        Emu(px_to_emu(decoration.border_left.width_px)),
        Emu(px_to_emu(accent_height_px)),
    )


def _add_code_block(slide, element: SlideElement) -> None:
    """Add a code block as textbox with background."""
    from .text import _apply_paragraph_layout, _apply_text_style, ALIGNMENT_MAP
    from pptx.enum.text import PP_ALIGN

    left = Emu(px_to_emu(element.box.x))
    top = Emu(px_to_emu(element.box.y))
    width = Emu(px_to_emu(element.box.width))
    height = Emu(px_to_emu(element.box.height))

    txbox = slide.shapes.add_textbox(left, top, width, height)
    tf = txbox.text_frame
    tf.word_wrap = True

    # Set background color
    if element.code_background:
        fill = txbox.fill
        fill.solid()
        fill.fore_color.rgb = _to_rgb(element.code_background)

    # Add code text with monospace font
    for i, para in enumerate(element.paragraphs):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.alignment = ALIGNMENT_MAP.get(para.alignment, PP_ALIGN.LEFT)
        _apply_paragraph_layout(p, para)

        for text_run in para.runs:
            r = p.add_run()
            r.text = text_run.text
            # Force monospace
            style = text_run.style.model_copy()
            style.font_family = "Courier New"
            _apply_text_style(r, style)


def _add_fallback_image(slide, element: SlideElement) -> None:
    """Add a fallback image for unsupported content."""
    if not element.unsupported_info or not element.unsupported_info.fallback_image_path:
        return

    left = Emu(px_to_emu(element.box.x))
    top = Emu(px_to_emu(element.box.y))
    width = Emu(px_to_emu(element.box.width))
    height = Emu(px_to_emu(element.box.height))

    image_path = Path(element.unsupported_info.fallback_image_path)
    if image_path.exists():
        slide.shapes.add_picture(str(image_path), left, top, width, height)
    else:
        logger.warning(
            "Fallback image not found: %s",
            element.unsupported_info.fallback_image_path,
        )
