"""Shared helpers for pptx_builder sub-modules."""

from __future__ import annotations

from lxml import etree
from pptx.dml.color import RGBColor
from pptx.oxml.ns import qn

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


def _set_fill_color(fill, color: RGBAColor) -> None:
    """Apply RGBA color to a FillFormat using OOXML alpha when needed."""
    fill.solid()
    fill.fore_color.rgb = RGBColor(color.r, color.g, color.b)
    solid_fill = fill._xPr.find(qn("a:solidFill"))
    if solid_fill is None:
        return
    _set_srgb_alpha(solid_fill, color.a)


def _set_line_color(line, color: RGBAColor) -> None:
    """Apply RGBA color to a LineFormat using OOXML alpha when needed."""
    line.color.rgb = RGBColor(color.r, color.g, color.b)
    solid_fill = line._ln.find(qn("a:solidFill"))
    if solid_fill is None:
        return
    _set_srgb_alpha(solid_fill, color.a)


def _set_srgb_alpha(solid_fill, alpha: float) -> None:
    """Write alpha to an a:solidFill/a:srgbClr node."""
    srgb = solid_fill.find(qn("a:srgbClr"))
    if srgb is None:
        srgb = etree.SubElement(solid_fill, qn("a:srgbClr"))
    for child in list(srgb):
        if child.tag == qn("a:alpha"):
            srgb.remove(child)
    bounded_alpha = max(0.0, min(alpha, 1.0))
    if bounded_alpha >= 1.0:
        return
    alpha_node = etree.SubElement(srgb, qn("a:alpha"))
    alpha_node.set("val", str(int(round(bounded_alpha * 100000))))
