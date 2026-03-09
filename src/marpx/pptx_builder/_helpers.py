"""Shared helpers for pptx_builder sub-modules."""

from __future__ import annotations

import math
from typing import Any

from lxml import etree
from pptx.dml.color import RGBColor
from pptx.oxml.ns import qn

from marpx.gradient_utils import css_angle_to_ooxml_angle
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


_DEFAULT_FILL_TAGS: frozenset[str] = frozenset(
    {
        qn("a:solidFill"),
        qn("a:gradFill"),
        qn("a:noFill"),
        qn("a:pattFill"),
        qn("a:blipFill"),
    }
)


def _remove_existing_fills(
    parent,
    *,
    fill_tags: frozenset[str] | None = None,
) -> None:
    """Remove existing fill elements from a parent XML node.

    Parameters
    ----------
    parent:
        The lxml element whose fill children should be removed.
    fill_tags:
        Optional explicit set of qualified tag names to remove.  When
        *None* the default OOXML fill tags are used (solidFill, gradFill,
        noFill, pattFill, blipFill).
    """
    if fill_tags is None:
        fill_tags = _DEFAULT_FILL_TAGS
    for child in list(parent):
        if child.tag in fill_tags:
            parent.remove(child)


def _build_gradient_fill_xml(
    parent_node,
    parsed_gradient,
    *,
    extra_attrs: dict[str, Any] | None = None,
    extra_children: list | None = None,
) -> etree._Element:
    """Build an ``a:gradFill`` subtree and append it to *parent_node*.

    Parameters
    ----------
    parent_node:
        The lxml element that will receive the new ``a:gradFill`` child.
        Pass ``None`` to create a detached element (caller must attach it).
    parsed_gradient:
        A ``ParsedGradient`` object returned by ``parse_linear_gradient()``.
    extra_attrs:
        Optional dict of additional attributes to set on the ``a:gradFill``
        element (e.g. ``{"flip": "none"}``).  ``rotWithShape`` is always set
        to ``"1"`` and cannot be overridden here.
    extra_children:
        Optional list of lxml elements to append after ``a:lin`` (e.g. an
        ``a:tileRect`` element).

    Returns
    -------
    etree._Element
        The created ``a:gradFill`` element.
    """
    if parent_node is not None:
        grad_fill = etree.SubElement(parent_node, qn("a:gradFill"))
    else:
        grad_fill = etree.Element(qn("a:gradFill"))

    if extra_attrs:
        for attr_name, attr_val in extra_attrs.items():
            grad_fill.set(attr_name, attr_val)
    grad_fill.set("rotWithShape", "1")

    gs_lst = etree.SubElement(grad_fill, qn("a:gsLst"))
    for stop in parsed_gradient.stops:
        gs = etree.SubElement(gs_lst, qn("a:gs"))
        gs.set("pos", str(int(round(stop.position * 100000))))
        srgb = etree.SubElement(gs, qn("a:srgbClr"))
        srgb.set("val", f"{stop.color.r:02X}{stop.color.g:02X}{stop.color.b:02X}")
        if stop.color.a < 1.0:
            etree.SubElement(srgb, qn("a:alpha")).set(
                "val", str(int(round(stop.color.a * 100000)))
            )

    lin = etree.SubElement(grad_fill, qn("a:lin"))
    lin.set("ang", str(css_angle_to_ooxml_angle(parsed_gradient.angle_deg)))
    lin.set("scaled", "0")

    if extra_children:
        for child in extra_children:
            grad_fill.append(child)

    return grad_fill


def _set_outer_shadow(
    sp_pr, shadow: BoxShadow, width_px: float, height_px: float
) -> None:
    """Write an a:outerShdw effect to a shape properties node."""
    _set_shadow_effect(sp_pr, qn("a:outerShdw"), shadow, width_px, height_px)


def _set_inner_shadow(
    sp_pr, shadow: BoxShadow, width_px: float, height_px: float
) -> None:
    """Write an a:innerShdw effect to a shape properties node."""
    _set_shadow_effect(sp_pr, qn("a:innerShdw"), shadow, width_px, height_px)


def _set_shadow_effect(
    sp_pr, tag: str, shadow: BoxShadow, width_px: float, height_px: float
) -> None:
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
