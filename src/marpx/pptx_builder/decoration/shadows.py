"""Shadow rendering for decoration shapes."""

from __future__ import annotations

from pptx.util import Emu

from marpx.models import Box, BoxDecoration, BoxShadow, RGBAColor
from marpx.utils.common import px_to_emu

from .._helpers import (
    _set_fill_color,
    _set_inner_shadow,
    _set_line_color,
    _set_outer_shadow,
)
from .shapes import _apply_round_rect_radius, _remove_theme_style


def _create_outer_shadow_shapes(
    slide,
    box: Box,
    decoration: BoxDecoration,
    shape_type,
) -> None:
    """Render outer (non-inset) shadow shapes behind the main background shape."""
    for shadow in decoration.box_shadows:
        if shadow.inset or shadow.color.a <= 0:
            continue
        if _is_spread_outline_shadow(shadow):
            _add_spread_outline_shape(
                slide,
                box,
                decoration,
                shape_type,
                shadow,
            )
        else:
            _add_shadow_shape(
                slide,
                box,
                decoration,
                shape_type,
                shadow,
            )


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


def _is_spread_outline_shadow(shadow: BoxShadow) -> bool:
    """Return True for spread-only outer shadows that should render as an outline."""
    return (
        not shadow.inset
        and shadow.spread_px > 0
        and shadow.blur_radius_px <= 0
        and shadow.offset_x_px == 0
        and shadow.offset_y_px == 0
    )


def _add_spread_outline_shape(
    slide,
    box: Box,
    decoration: BoxDecoration,
    shape_type,
    shadow: BoxShadow,
):
    """Render a spread-only outer shadow as an expanded outline shape."""
    spread = shadow.spread_px
    outline_box = Box(
        x=box.x - spread,
        y=box.y - spread,
        width=box.width + (spread * 2),
        height=box.height + (spread * 2),
    )
    left = Emu(px_to_emu(outline_box.x))
    top = Emu(px_to_emu(outline_box.y))
    width = Emu(px_to_emu(outline_box.width))
    height = Emu(px_to_emu(outline_box.height))

    outline_shape = slide.shapes.add_shape(shape_type, left, top, width, height)
    _remove_theme_style(outline_shape)
    outline_shape.fill.background()
    if decoration.border_radius_px > 0:
        _apply_round_rect_radius(
            outline_shape,
            px_to_emu(outline_box.width),
            px_to_emu(outline_box.height),
            px_to_emu(decoration.border_radius_px + spread),
        )
    _set_line_color(outline_shape.line, shadow.color)
    outline_shape.line.width = Emu(px_to_emu(spread * 2))


def _create_inset_shadow_shapes(
    slide,
    box: Box,
    decoration: BoxDecoration,
    shape_type,
) -> None:
    """Render inset shadow shapes layered on top of the main background shape."""
    for shadow in decoration.box_shadows:
        if not shadow.inset or shadow.color.a <= 0:
            continue
        _add_shadow_shape(
            slide,
            box,
            decoration,
            shape_type,
            shadow,
            inset=True,
        )
