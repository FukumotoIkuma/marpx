"""Shared helpers for pptx_builder sub-modules."""
from __future__ import annotations

from pptx.dml.color import RGBColor

from marpx.models import RGBAColor
from marpx.utils import blend_alpha


def _to_rgb(color: RGBAColor) -> RGBColor:
    """Convert RGBAColor to python-pptx RGBColor, blending alpha."""
    blended = blend_alpha(color)
    return RGBColor(blended.r, blended.g, blended.b)


def _with_opacity(color: RGBAColor, opacity: float) -> RGBAColor:
    """Apply an additional opacity multiplier to an RGBA color."""
    return RGBAColor(
        r=color.r,
        g=color.g,
        b=color.b,
        a=max(0.0, min(color.a * opacity, 1.0)),
    )
