"""Text rendering functions for pptx_builder."""

from __future__ import annotations

from lxml import etree
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_VERTICAL_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Pt

from marpx.models import (
    ElementType,
    SlideElement,
    TextRun,
    TextStyle,
)
from marpx.utils import (
    blend_alpha,
    px_to_emu,
    px_to_pt,
)

from ._helpers import _to_rgb
from .decoration import _add_decoration_shape

ALIGNMENT_MAP: dict[str, PP_ALIGN] = {
    "left": PP_ALIGN.LEFT,
    "center": PP_ALIGN.CENTER,
    "right": PP_ALIGN.RIGHT,
    "justify": PP_ALIGN.JUSTIFY,
    "start": PP_ALIGN.LEFT,
    "end": PP_ALIGN.RIGHT,
}

GROUPABLE_TEXT_TYPES: tuple[ElementType, ...] = (
    ElementType.HEADING,
    ElementType.PARAGRAPH,
    ElementType.BLOCKQUOTE,
    ElementType.UNORDERED_LIST,
    ElementType.ORDERED_LIST,
)


def _apply_text_style(run, style: TextStyle) -> None:
    """Apply TextStyle to a python-pptx run."""
    run.font.name = style.font_family
    run.font.size = Pt(px_to_pt(style.font_size_px))
    run.font.bold = style.bold
    run.font.italic = style.italic
    run.font.underline = style.underline
    r_pr = run._r.get_or_add_rPr()
    if style.strike:
        r_pr.set("strike", "sngStrike")
    elif "strike" in r_pr.attrib:
        del r_pr.attrib["strike"]
    if style.color.a < 1.0:
        run.font.color.rgb = RGBColor(style.color.r, style.color.g, style.color.b)
        solid_fill = r_pr.find(qn("a:solidFill"))
        if solid_fill is None:
            solid_fill = etree.SubElement(r_pr, qn("a:solidFill"))
        srgb = solid_fill.find(qn("a:srgbClr"))
        if srgb is None:
            srgb = etree.SubElement(solid_fill, qn("a:srgbClr"))
        srgb.set("val", f"{style.color.r:02X}{style.color.g:02X}{style.color.b:02X}")
        for child in list(srgb):
            if child.tag == qn("a:alpha"):
                srgb.remove(child)
        alpha = etree.SubElement(srgb, qn("a:alpha"))
        alpha.set("val", str(int(style.color.a * 100000)))
    else:
        run.font.color.rgb = _to_rgb(style.color)
    if style.background_color and style.background_color.a > 0:
        r_pr = run._r.get_or_add_rPr()
        existing = r_pr.find(qn("a:highlight"))
        if existing is not None:
            r_pr.remove(existing)
        highlight = etree.Element(qn("a:highlight"))
        bg = blend_alpha(style.background_color)
        color = etree.SubElement(highlight, qn("a:srgbClr"))
        color.set("val", f"{bg.r:02X}{bg.g:02X}{bg.b:02X}")
        insert_before = None
        for child in r_pr:
            if child.tag in {
                qn("a:latin"),
                qn("a:ea"),
                qn("a:cs"),
                qn("a:sym"),
                qn("a:hlinkClick"),
                qn("a:hlinkMouseOver"),
            }:
                insert_before = child
                break
        if insert_before is None:
            r_pr.append(highlight)
        else:
            insert_before.addprevious(highlight)


def _add_paragraph_runs(pptx_para, runs: list[TextRun]) -> None:
    """Add text runs to a python-pptx paragraph."""
    for i, text_run in enumerate(runs):
        if i == 0:
            r = pptx_para.runs[0] if pptx_para.runs else pptx_para.add_run()
        else:
            r = pptx_para.add_run()
        r.text = text_run.text
        _apply_text_style(r, text_run.style)
        if text_run.link_url:
            r.hyperlink.address = text_run.link_url


def _ordered_numbering_type(style_type: str | None) -> str:
    """Map CSS list-style-type to OOXML numbering type."""
    normalized = (style_type or "").lower()
    return {
        "decimal": "arabicPeriod",
        "decimal-leading-zero": "arabicPeriod",
        "lower-alpha": "alphaLcPeriod",
        "lower-latin": "alphaLcPeriod",
        "upper-alpha": "alphaUcPeriod",
        "upper-latin": "alphaUcPeriod",
        "lower-roman": "romanLcPeriod",
        "upper-roman": "romanUcPeriod",
    }.get(normalized, "arabicPeriod")


def _unordered_bullet_char(style_type: str | None) -> str:
    """Map CSS list-style-type to a bullet character."""
    normalized = (style_type or "").lower()
    return {
        "circle": "\u25e6",
        "square": "\u25aa",
    }.get(normalized, "\u2022")


def _configure_list_paragraph(
    pptx_para,
    level: int,
    ordered: bool,
    list_style_type: str | None = None,
    order_number: int | None = None,
) -> None:
    """Apply bullet or numbering settings to a paragraph."""
    pptx_para.level = level
    pPr = pptx_para._p.get_or_add_pPr()
    normalized_style = (list_style_type or "").lower()
    if normalized_style == "none":
        etree.SubElement(pPr, qn("a:buNone"))
        return
    if ordered:
        buAutoNum = etree.SubElement(pPr, qn("a:buAutoNum"))
        buAutoNum.set("type", _ordered_numbering_type(list_style_type))
        if order_number and order_number > 1:
            buAutoNum.set("startAt", str(order_number))
    else:
        buChar = etree.SubElement(pPr, qn("a:buChar"))
        buChar.set("char", _unordered_bullet_char(list_style_type))


def _iter_text_payloads(element: SlideElement):
    """Yield paragraph payloads for a groupable text element."""
    if element.element_type in (
        ElementType.HEADING,
        ElementType.PARAGRAPH,
        ElementType.BLOCKQUOTE,
        ElementType.DECORATED_BLOCK,
    ):
        for para in element.paragraphs:
            yield {
                "paragraph": para,
                "is_list": False,
                "ordered": False,
                "level": 0,
            }
        return

    if element.element_type in (
        ElementType.UNORDERED_LIST,
        ElementType.ORDERED_LIST,
    ):
        for item in element.list_items:
            yield {
                "paragraph": None,
                "runs": item.runs,
                "is_list": True,
                "ordered": element.element_type == ElementType.ORDERED_LIST,
                "level": item.level,
                "style_type": item.list_style_type,
                "order_number": item.order_number,
                "alignment": item.alignment,
                "line_height_px": item.line_height_px,
                "space_before_px": item.space_before_px,
                "space_after_px": item.space_after_px,
            }


def _append_payload_to_text_frame(text_frame, payload, index: int) -> None:
    """Append a paragraph payload to a text frame."""
    if index == 0:
        p = text_frame.paragraphs[0]
    else:
        p = text_frame.add_paragraph()

    if payload["is_list"]:
        _configure_list_paragraph(
            p,
            payload["level"],
            payload["ordered"],
            payload.get("style_type"),
            payload.get("order_number"),
        )
        p.alignment = ALIGNMENT_MAP.get(payload.get("alignment", "left"), PP_ALIGN.LEFT)
        _apply_spacing(
            p,
            payload.get("line_height_px"),
            payload.get("space_before_px", 0.0),
            payload.get("space_after_px", 0.0),
        )
        _add_paragraph_runs(p, payload["runs"])
        return

    para = payload["paragraph"]
    if para.list_level is not None:
        _configure_list_paragraph(
            p,
            para.list_level,
            para.list_ordered,
            para.list_style_type,
            para.order_number,
        )
    p.alignment = ALIGNMENT_MAP.get(para.alignment, PP_ALIGN.LEFT)
    _apply_paragraph_layout(p, para)
    _add_paragraph_runs(p, para.runs)


def _populate_text_frame(text_frame, elements: list[SlideElement]) -> None:
    """Populate a text frame from one or more text-bearing elements."""
    payload_index = 0
    for element in elements:
        for payload in _iter_text_payloads(element):
            _append_payload_to_text_frame(text_frame, payload, payload_index)
            payload_index += 1


def _resolve_textbox_geometry(element: SlideElement) -> tuple[Emu, Emu, Emu, Emu]:
    """Return the element's content box when available, else its outer box."""
    if element.content_box is not None:
        source_box = element.content_box
    elif element.decoration is not None:
        source_box = _derive_content_box_from_decoration(element)
    else:
        source_box = element.box
    left_px = source_box.x
    top_px = source_box.y
    width_px = max(source_box.width, 1)
    height_px = max(source_box.height, 1)
    return (
        Emu(px_to_emu(left_px)),
        Emu(px_to_emu(top_px)),
        Emu(px_to_emu(width_px)),
        Emu(px_to_emu(height_px)),
    )


def _derive_content_box_from_decoration(element: SlideElement):
    """Derive a content box from an outer box plus extracted border/padding."""
    decoration = element.decoration
    assert decoration is not None
    left_inset = decoration.border_left.width_px + decoration.padding.left_px
    top_inset = decoration.border_top.width_px + decoration.padding.top_px
    right_inset = decoration.border_right.width_px + decoration.padding.right_px
    bottom_inset = decoration.border_bottom.width_px + decoration.padding.bottom_px
    return element.box.model_copy(
        update={
            "x": element.box.x + left_inset,
            "y": element.box.y + top_inset,
            "width": max(element.box.width - left_inset - right_inset, 1),
            "height": max(element.box.height - top_inset - bottom_inset, 1),
        }
    )


def _set_text_frame_margins_zero(text_frame) -> None:
    """Use extracted box geometry as-is and disable PowerPoint default insets."""
    zero = Emu(0)
    text_frame.margin_top = zero
    text_frame.margin_right = zero
    text_frame.margin_bottom = zero
    text_frame.margin_left = zero


def _apply_paragraph_layout(pptx_para, para) -> None:
    """Apply paragraph-level layout such as line-height and spacing."""
    _apply_spacing(
        pptx_para,
        para.line_height_px,
        para.space_before_px,
        para.space_after_px,
    )


def _apply_spacing(
    pptx_para,
    line_height_px: float | None,
    space_before_px: float,
    space_after_px: float,
) -> None:
    """Apply line-height and paragraph spacing values."""
    if line_height_px and line_height_px > 0:
        pptx_para.line_spacing = Pt(px_to_pt(line_height_px))
    if space_before_px > 0:
        pptx_para.space_before = Pt(px_to_pt(space_before_px))
    if space_after_px > 0:
        pptx_para.space_after = Pt(px_to_pt(space_after_px))


def _add_textbox(slide, element: SlideElement) -> None:
    """Add a textbox or decorated text container."""
    if element.decoration:
        _add_decoration_shape(slide, element.box, element.decoration)
        if not element.paragraphs and not element.list_items:
            return
        left, top, width, height = _resolve_textbox_geometry(element)
        text_container = slide.shapes.add_textbox(left, top, width, height)
        text_container.fill.background()
        text_container.line.fill.background()
    else:
        left, top, width, height = _resolve_textbox_geometry(element)
        text_container = slide.shapes.add_textbox(left, top, width, height)

    tf = text_container.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_VERTICAL_ANCHOR.TOP
    _set_text_frame_margins_zero(tf)
    _populate_text_frame(tf, [element])
