"""Tests for marpx.models module."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from marpx.models import (
    Background,
    Box,
    CodeBlockElement,
    ElementType,
    ImageElement,
    ListElement,
    ListItem,
    Paragraph,
    Presentation,
    RGBAColor,
    Slide,
    TableCell,
    TableElement,
    TableRow,
    TextElement,
    TextRun,
    TextStyle,
    UnsupportedElement,
    UnsupportedInfo,
)


# ---------------------------------------------------------------------------
# RGBAColor
# ---------------------------------------------------------------------------
class TestRGBAColor:
    """Tests for RGBAColor model validation."""

    def test_valid_color(self) -> None:
        c = RGBAColor(r=128, g=64, b=255, a=0.5)
        assert c.r == 128
        assert c.g == 64
        assert c.b == 255
        assert c.a == 0.5

    def test_default_alpha(self) -> None:
        c = RGBAColor(r=0, g=0, b=0)
        assert c.a == 1.0

    def test_bounds_min(self) -> None:
        c = RGBAColor(r=0, g=0, b=0, a=0.0)
        assert c.r == 0
        assert c.a == 0.0

    def test_bounds_max(self) -> None:
        c = RGBAColor(r=255, g=255, b=255, a=1.0)
        assert c.r == 255

    def test_r_too_high(self) -> None:
        with pytest.raises(ValidationError):
            RGBAColor(r=256, g=0, b=0)

    def test_r_negative(self) -> None:
        with pytest.raises(ValidationError):
            RGBAColor(r=-1, g=0, b=0)

    def test_g_too_high(self) -> None:
        with pytest.raises(ValidationError):
            RGBAColor(r=0, g=256, b=0)

    def test_b_too_high(self) -> None:
        with pytest.raises(ValidationError):
            RGBAColor(r=0, g=0, b=256)

    def test_alpha_too_high(self) -> None:
        with pytest.raises(ValidationError):
            RGBAColor(r=0, g=0, b=0, a=1.1)

    def test_alpha_negative(self) -> None:
        with pytest.raises(ValidationError):
            RGBAColor(r=0, g=0, b=0, a=-0.1)


# ---------------------------------------------------------------------------
# Box
# ---------------------------------------------------------------------------
class TestBox:
    """Tests for Box model."""

    def test_valid_box(self) -> None:
        b = Box(x=10.0, y=20.0, width=100.0, height=50.0)
        assert b.x == 10.0
        assert b.y == 20.0
        assert b.width == 100.0
        assert b.height == 50.0

    def test_zero_dimensions(self) -> None:
        b = Box(x=0, y=0, width=0, height=0)
        assert b.width == 0.0

    def test_float_coords(self) -> None:
        b = Box(x=1.5, y=2.7, width=100.123, height=50.456)
        assert b.x == 1.5


# ---------------------------------------------------------------------------
# SlideElement
# ---------------------------------------------------------------------------
class TestSlideElement:
    """Tests for SlideElement construction with various types."""

    def test_heading_element(self) -> None:
        el = TextElement(
            element_type=ElementType.HEADING,
            box=Box(x=0, y=0, width=100, height=50),
            heading_level=1,
            paragraphs=[Paragraph(runs=[TextRun(text="Title")])],
        )
        assert el.element_type == ElementType.HEADING
        assert el.heading_level == 1
        assert el.paragraphs[0].runs[0].text == "Title"

    def test_paragraph_element(self) -> None:
        el = TextElement(
            element_type=ElementType.PARAGRAPH,
            box=Box(x=0, y=0, width=100, height=30),
            paragraphs=[Paragraph(runs=[TextRun(text="Hello")])],
        )
        assert el.element_type == ElementType.PARAGRAPH

    def test_list_element(self) -> None:
        el = ListElement(
            element_type=ElementType.UNORDERED_LIST,
            box=Box(x=0, y=0, width=200, height=100),
            list_items=[
                ListItem(runs=[TextRun(text="Item 1")], level=0),
                ListItem(runs=[TextRun(text="Item 2")], level=1),
            ],
        )
        assert len(el.list_items) == 2
        assert el.list_items[1].level == 1

    def test_table_element(self) -> None:
        el = TableElement(
            element_type=ElementType.TABLE,
            box=Box(x=0, y=0, width=400, height=200),
            table_rows=[
                TableRow(
                    cells=[
                        TableCell(paragraphs=[Paragraph(runs=[TextRun(text="A")])]),
                        TableCell(paragraphs=[Paragraph(runs=[TextRun(text="B")])]),
                    ]
                ),
            ],
        )
        assert len(el.table_rows) == 1
        assert len(el.table_rows[0].cells) == 2

    def test_code_block_element(self) -> None:
        el = CodeBlockElement(
            element_type=ElementType.CODE_BLOCK,
            box=Box(x=0, y=0, width=300, height=150),
            code_language="python",
            code_background=RGBAColor(r=40, g=40, b=40),
        )
        assert el.code_language == "python"
        assert el.code_background is not None

    def test_unsupported_element(self) -> None:
        el = UnsupportedElement(
            element_type=ElementType.UNSUPPORTED,
            box=Box(x=0, y=0, width=100, height=100),
            unsupported_info=UnsupportedInfo(reason="SVG", tag_name="svg"),
        )
        assert el.element_type == ElementType.UNSUPPORTED
        assert el.unsupported_info is not None
        assert el.unsupported_info.tag_name == "svg"

    def test_image_element(self) -> None:
        el = ImageElement(
            element_type=ElementType.IMAGE,
            box=Box(x=10, y=10, width=300, height=200),
            image_src="https://example.com/img.png",
        )
        assert el.image_src == "https://example.com/img.png"

    def test_default_empty_lists(self) -> None:
        el = TextElement(
            element_type=ElementType.PARAGRAPH,
            box=Box(x=0, y=0, width=100, height=50),
        )
        assert el.paragraphs == []
        assert el.list_items == []
        assert el.table_rows == []

    def test_all_element_types_exist(self) -> None:
        expected = {
            "heading",
            "paragraph",
            "blockquote",
            "decorated_block",
            "unordered_list",
            "ordered_list",
            "code_block",
            "image",
            "table",
            "math",
            "unsupported",
        }
        actual = {e.value for e in ElementType}
        assert actual == expected


# ---------------------------------------------------------------------------
# ListItem
# ---------------------------------------------------------------------------
class TestListItem:
    """Tests for ListItem model."""

    def test_default_level(self) -> None:
        item = ListItem(runs=[TextRun(text="hello")])
        assert item.level == 0
        assert item.order_number is None

    def test_nested_level(self) -> None:
        item = ListItem(runs=[TextRun(text="sub")], level=2)
        assert item.level == 2

    def test_ordered_item(self) -> None:
        item = ListItem(
            runs=[TextRun(text="first")],
            level=0,
            order_number=1,
        )
        assert item.order_number == 1

    def test_preserves_list_style_and_spacing(self) -> None:
        item = ListItem(
            runs=[TextRun(text="roman item")],
            level=1,
            order_number=2,
            list_style_type="lower-roman",
            line_height_px=43.5,
            space_before_px=7.25,
        )
        assert item.list_style_type == "lower-roman"
        assert item.line_height_px == 43.5
        assert item.space_before_px == 7.25


class TestParagraph:
    """Tests for Paragraph model."""

    def test_preserves_list_marker_metadata(self) -> None:
        paragraph = Paragraph(
            runs=[TextRun(text="nested item")],
            list_level=1,
            list_ordered=True,
            list_style_type="lower-roman",
            order_number=2,
        )
        assert paragraph.list_style_type == "lower-roman"
        assert paragraph.order_number == 2


# ---------------------------------------------------------------------------
# Presentation
# ---------------------------------------------------------------------------
class TestPresentation:
    """Tests for Presentation model."""

    def test_empty_presentation(self) -> None:
        p = Presentation()
        assert len(p.slides) == 0
        assert p.default_width_px == 1280.0
        assert p.default_height_px == 720.0

    def test_multiple_slides(self) -> None:
        slides = [
            Slide(width_px=1280, height_px=720, slide_number=0),
            Slide(width_px=1280, height_px=720, slide_number=1),
            Slide(width_px=1280, height_px=720, slide_number=2),
        ]
        p = Presentation(slides=slides)
        assert len(p.slides) == 3

    def test_slide_with_background(self) -> None:
        s = Slide(
            width_px=1280,
            height_px=720,
            background=Background(color=RGBAColor(r=30, g=30, b=30)),
        )
        assert s.background.color is not None
        assert s.background.color.r == 30


# ---------------------------------------------------------------------------
# TextStyle / TextRun
# ---------------------------------------------------------------------------
class TestTextStyle:
    """Tests for TextStyle defaults."""

    def test_defaults(self) -> None:
        s = TextStyle()
        assert s.font_family == "Arial"
        assert s.font_size_px == 16.0
        assert s.bold is False
        assert s.italic is False
        assert s.underline is False
        assert s.color.r == 0
        assert s.background_color is None

    def test_text_run_with_link(self) -> None:
        tr = TextRun(text="click me", link_url="https://example.com")
        assert tr.link_url == "https://example.com"
