"""Shared helpers for pptx_builder sub-modules."""

from __future__ import annotations

import math

from lxml import etree
from pptx.dml.color import RGBColor
from pptx.oxml.ns import qn

from marpx.models import BoxShadow, RGBAColor
from marpx.utils import blend_alpha, px_to_emu


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


def _set_blip_alpha(blip, alpha: float) -> None:
    """Write alpha to an a:blip node for picture transparency."""
    for child in list(blip):
        if child.tag == qn("a:alphaModFix"):
            blip.remove(child)
    bounded_alpha = max(0.0, min(alpha, 1.0))
    if bounded_alpha >= 1.0:
        return
    alpha_node = etree.SubElement(blip, qn("a:alphaModFix"))
    alpha_node.set("amt", str(int(round(bounded_alpha * 100000))))


def _set_outer_shadow(sp_pr, shadow: BoxShadow, width_px: float, height_px: float) -> None:
    """Write an a:outerShdw effect to a shape properties node."""
    _set_shadow_effect(sp_pr, qn("a:outerShdw"), shadow, width_px, height_px)


def _set_inner_shadow(sp_pr, shadow: BoxShadow, width_px: float, height_px: float) -> None:
    """Write an a:innerShdw effect to a shape properties node."""
    _set_shadow_effect(sp_pr, qn("a:innerShdw"), shadow, width_px, height_px)


def _set_shadow_effect(sp_pr, tag: str, shadow: BoxShadow, width_px: float, height_px: float) -> None:
    """Write a shadow effect node to a shape properties node."""
    effect_lst = sp_pr.find(qn("a:effectLst"))
    if effect_lst is None:
        effect_lst = etree.SubElement(sp_pr, qn("a:effectLst"))
    for child in list(effect_lst):
        if child.tag == tag:
            effect_lst.remove(child)

    shadow_el = etree.SubElement(effect_lst, tag)
    shadow_el.set("blurRad", str(max(px_to_emu(shadow.blur_radius_px), 0)))
    dist_px = math.hypot(shadow.offset_x_px, shadow.offset_y_px)
    shadow_el.set("dist", str(max(px_to_emu(dist_px), 0)))
    angle_deg = math.degrees(math.atan2(shadow.offset_y_px, shadow.offset_x_px))
    if angle_deg < 0:
        angle_deg += 360
    shadow_el.set("dir", str(int(round(angle_deg * 60000))))
    shadow_el.set("rotWithShape", "0")

    if shadow.spread_px > 0 and width_px > 0 and height_px > 0:
        sx = int(round(((width_px + (shadow.spread_px * 2)) / width_px) * 100000))
        sy = int(round(((height_px + (shadow.spread_px * 2)) / height_px) * 100000))
        shadow_el.set("sx", str(max(sx, 100000)))
        shadow_el.set("sy", str(max(sy, 100000)))

    srgb = etree.SubElement(shadow_el, qn("a:srgbClr"))
    srgb.set("val", f"{shadow.color.r:02X}{shadow.color.g:02X}{shadow.color.b:02X}")
    if shadow.color.a < 1.0:
        etree.SubElement(srgb, qn("a:alpha")).set(
            "val", str(int(round(shadow.color.a * 100000)))
        )
