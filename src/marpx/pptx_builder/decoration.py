"""Decoration shape rendering for pptx_builder."""

from __future__ import annotations

import io
import logging
from pathlib import Path

from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
from pptx.oxml.ns import qn
from pptx.util import Emu

from marpx.gradient_utils import render_linear_gradient_png
from marpx.models import Box, BoxDecoration, BoxShadow, RGBAColor, SlideElement
from marpx.utils import px_to_emu

from ._helpers import (
    _set_fill_color,
    _set_inner_shadow,
    _set_line_color,
    _set_outer_shadow,
    _with_opacity,
)

logger = logging.getLogger(__name__)


def _round_rect_adjustment(
    width: int | float, height: int | float, radius: int | float
) -> float:
    """Return normalized roundRect adjustment matching CSS border-radius."""
    min_dim = min(float(width), float(height))
    if min_dim <= 0:
        return 0.0
    return max(0.0, min(float(radius) / min_dim, 0.5))


def _apply_round_rect_radius(
    shape, width: int | float, height: int | float, radius: int | float
) -> None:
    """Apply a CSS-like corner radius to a rounded rectangle auto shape."""
    if radius <= 0 or width <= 0 or height <= 0:
        return
    if getattr(shape, "adjustments", None) and len(shape.adjustments) > 0:
        shape.adjustments[0] = _round_rect_adjustment(width, height, radius)


def _apply_round_rect_radius_to_geom(
    prst_geom, width: int | float, height: int | float, radius: int | float
) -> None:
    """Apply a CSS-like corner radius to a preset geometry node."""
    if radius <= 0 or width <= 0 or height <= 0:
        return
    adj = int(round(_round_rect_adjustment(width, height, radius) * 100000))
    prst_geom.rewrite_guides([("adj", adj)])


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

    for shadow in decoration.box_shadows:
        if shadow.inset or shadow.color.a <= 0:
            continue
        _add_shadow_shape(slide, box, decoration, shape_type, shadow)

    bg_shape = None
    if decoration.background_gradient:
        gradient_bytes = render_linear_gradient_png(
            decoration.background_gradient,
            max(int(round(box.width)), 1),
            max(int(round(box.height)), 1),
            decoration.border_radius_px,
        )
        if gradient_bytes:
            bg_shape = slide.shapes.add_picture(
                io.BytesIO(gradient_bytes), left, top, width, height
            )

    if bg_shape is None:
        bg_shape = slide.shapes.add_shape(shape_type, left, top, width, height)
        _remove_theme_style(bg_shape)
        if decoration.border_radius_px > 0:
            _apply_round_rect_radius(
                bg_shape,
                px_to_emu(box.width),
                px_to_emu(box.height),
                px_to_emu(decoration.border_radius_px),
            )

        fill = bg_shape.fill
        if decoration.background_color and decoration.opacity > 0:
            fill_color = _with_opacity(decoration.background_color, decoration.opacity)
            _set_fill_color(fill, fill_color)
        else:
            fill.background()

    uniform_border = _detect_uniform_border(decoration)
    if uniform_border:
        border_color = _with_opacity(uniform_border.color, decoration.opacity)
        if border_color.a > 0:
            if hasattr(bg_shape, "line"):
                _set_line_color(bg_shape.line, border_color)
                bg_shape.line.width = Emu(px_to_emu(uniform_border.width_px))
            else:
                border_shape = slide.shapes.add_shape(
                    shape_type, left, top, width, height
                )
                _remove_theme_style(border_shape)
                border_shape.fill.background()
                if decoration.border_radius_px > 0:
                    _apply_round_rect_radius(
                        border_shape,
                        px_to_emu(box.width),
                        px_to_emu(box.height),
                        px_to_emu(decoration.border_radius_px),
                    )
                _set_line_color(border_shape.line, border_color)
                border_shape.line.width = Emu(px_to_emu(uniform_border.width_px))
        else:
            if hasattr(bg_shape, "line"):
                bg_shape.line.fill.background()
    elif hasattr(bg_shape, "line"):
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
        _set_fill_color(accent_shape.fill, accent_color)
        accent_shape.line.fill.background()

    for shadow in decoration.box_shadows:
        if not shadow.inset or shadow.color.a <= 0:
            continue
        _add_shadow_shape(slide, box, decoration, shape_type, shadow, inset=True)

    return bg_shape


def _add_shadow_shape(
    slide,
    box: Box,
    decoration: BoxDecoration,
    shape_type,
    shadow: BoxShadow,
    *,
    inset: bool = False,
):
    """Render a shadow-only helper shape behind a decoration."""
    left = Emu(px_to_emu(box.x))
    top = Emu(px_to_emu(box.y))
    width = Emu(px_to_emu(box.width))
    height = Emu(px_to_emu(box.height))
    shadow_shape = slide.shapes.add_shape(shape_type, left, top, width, height)
    _remove_theme_style(shadow_shape)
    _set_fill_color(shadow_shape.fill, RGBAColor(r=255, g=255, b=255, a=0.0))
    shadow_shape.line.fill.background()
    if decoration.border_radius_px > 0:
        _apply_round_rect_radius(
            shadow_shape,
            px_to_emu(box.width),
            px_to_emu(box.height),
            px_to_emu(decoration.border_radius_px),
        )
    if inset:
        _set_inner_shadow(shadow_shape._element.spPr, shadow, box.width, box.height)
    else:
        _set_outer_shadow(shadow_shape._element.spPr, shadow, box.width, box.height)


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
        side
        for side in sides
        if side.width_px > 0 and side.style and side.style != "none" and side.color
    ]
    if not visible:
        return None
    first = visible[0]
    if (
        all(
            side.width_px == first.width_px
            and side.style == first.style
            and side.color == first.color
            for side in visible
        )
        and len(visible) == 4
    ):
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
    from .text import (
        _apply_paragraph_layout,
        _apply_text_style,
        _resolve_textbox_geometry,
        _set_text_frame_margins_zero,
        ALIGNMENT_MAP,
    )
    from pptx.enum.text import PP_ALIGN

    if element.decoration:
        _add_decoration_shape(slide, element.box, element.decoration)

    left, top, width, height = _resolve_textbox_geometry(element)

    txbox = slide.shapes.add_textbox(left, top, width, height)
    tf = txbox.text_frame
    tf.word_wrap = True
    _set_text_frame_margins_zero(tf)
    txbox.line.fill.background()

    if element.decoration:
        txbox.fill.background()
    elif element.code_background:
        fill = txbox.fill
        _set_fill_color(fill, element.code_background)
    else:
        txbox.fill.background()

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
