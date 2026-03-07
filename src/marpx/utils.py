"""Utility functions for unit conversion, layout, and color handling."""

from __future__ import annotations

from collections.abc import Iterable

from marpx.models import Box, RGBAColor


# Constants
PX_PER_INCH = 96
EMU_PER_INCH = 914400
EMU_PER_PX = EMU_PER_INCH / PX_PER_INCH  # 9525
PT_PER_PX = 72 / PX_PER_INCH  # 0.75


def px_to_emu(px: float) -> int:
    """Convert pixels to English Metric Units."""
    return round(px * EMU_PER_PX)


def px_to_pt(px: float) -> float:
    """Convert pixels to points."""
    return px * PT_PER_PX


def boxes_share_column(
    first: Box,
    second: Box,
    *,
    x_tolerance_px: float = 8.0,
    width_tolerance_px: float = 32.0,
) -> bool:
    """Return True when two boxes are aligned as one text column."""
    return (
        abs(first.x - second.x) <= x_tolerance_px
        and abs(first.width - second.width) <= width_tolerance_px
    )


def boxes_have_horizontal_overlap(
    first: Box,
    second: Box,
    *,
    min_overlap_ratio: float = 0.5,
    min_overlap_px: float = 80.0,
) -> bool:
    """Return True when two boxes overlap enough horizontally to merge."""
    first_right = first.x + first.width
    second_right = second.x + second.width
    overlap = min(first_right, second_right) - max(first.x, second.x)
    min_width = min(first.width, second.width)
    return overlap >= max(min_width * min_overlap_ratio, min_overlap_px)


def boxes_have_mergeable_vertical_gap(
    first: Box,
    second: Box,
    *,
    min_gap_px: float = -4.0,
    max_gap_px: float = 48.0,
) -> bool:
    """Return True when two boxes are vertically close enough to merge."""
    first_bottom = first.y + first.height
    vertical_gap = second.y - first_bottom
    return min_gap_px <= vertical_gap <= max_gap_px


def union_boxes(boxes: Iterable[Box]) -> Box:
    """Return the union of one or more boxes."""
    box_list = list(boxes)
    if not box_list:
        raise ValueError("union_boxes requires at least one box")

    left = min(box.x for box in box_list)
    top = min(box.y for box in box_list)
    right = max(box.x + box.width for box in box_list)
    bottom = max(box.y + box.height for box in box_list)
    return Box(x=left, y=top, width=right - left, height=bottom - top)


def parse_css_color(css_color: str) -> RGBAColor:
    """Parse CSS color string to RGBAColor.

    Supports: rgb(), rgba(), hex (#rgb, #rrggbb, #rrggbbaa), named colors.
    """
    css_color = css_color.strip()

    if css_color.startswith("rgba("):
        parts = css_color[5:-1].split(",")
        return RGBAColor(
            r=int(parts[0].strip()),
            g=int(parts[1].strip()),
            b=int(parts[2].strip()),
            a=float(parts[3].strip()),
        )
    elif css_color.startswith("rgb("):
        parts = css_color[4:-1].split(",")
        return RGBAColor(
            r=int(parts[0].strip()),
            g=int(parts[1].strip()),
            b=int(parts[2].strip()),
        )
    elif css_color.startswith("#"):
        hex_str = css_color[1:]
        if len(hex_str) == 3:
            r = int(hex_str[0] * 2, 16)
            g = int(hex_str[1] * 2, 16)
            b = int(hex_str[2] * 2, 16)
            return RGBAColor(r=r, g=g, b=b)
        elif len(hex_str) == 6:
            r = int(hex_str[0:2], 16)
            g = int(hex_str[2:4], 16)
            b = int(hex_str[4:6], 16)
            return RGBAColor(r=r, g=g, b=b)
        elif len(hex_str) == 8:
            r = int(hex_str[0:2], 16)
            g = int(hex_str[2:4], 16)
            b = int(hex_str[4:6], 16)
            a = int(hex_str[6:8], 16) / 255.0
            return RGBAColor(r=r, g=g, b=b, a=a)

    # Named colors (common subset)
    named = {
        "black": RGBAColor(r=0, g=0, b=0),
        "white": RGBAColor(r=255, g=255, b=255),
        "red": RGBAColor(r=255, g=0, b=0),
        "green": RGBAColor(r=0, g=128, b=0),
        "blue": RGBAColor(r=0, g=0, b=255),
        "transparent": RGBAColor(r=0, g=0, b=0, a=0.0),
    }
    if css_color.lower() in named:
        return named[css_color.lower()]

    # Default fallback
    return RGBAColor(r=0, g=0, b=0)


def blend_alpha(color: RGBAColor, bg: RGBAColor | None = None) -> RGBAColor:
    """Blend RGBA color with background (default white) to produce opaque RGB.

    python-pptx doesn't support alpha, so we pre-blend.
    """
    if bg is None:
        bg = RGBAColor(r=255, g=255, b=255)

    a = color.a
    r = round(color.r * a + bg.r * (1 - a))
    g = round(color.g * a + bg.g * (1 - a))
    b = round(color.b * a + bg.b * (1 - a))
    return RGBAColor(r=r, g=g, b=b, a=1.0)
