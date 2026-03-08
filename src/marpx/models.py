"""Normalized presentation model for marpx.

All coordinates are slide-relative in px.
Unit conversion to EMU happens in the PPTX builder.
"""

from __future__ import annotations
from enum import Enum
from pydantic import BaseModel, Field


class ElementType(str, Enum):
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    BLOCKQUOTE = "blockquote"
    DECORATED_BLOCK = "decorated_block"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"
    CODE_BLOCK = "code_block"
    IMAGE = "image"
    TABLE = "table"
    MATH = "math"
    UNSUPPORTED = "unsupported"


class RGBAColor(BaseModel):
    r: int = Field(ge=0, le=255)
    g: int = Field(ge=0, le=255)
    b: int = Field(ge=0, le=255)
    a: float = Field(ge=0.0, le=1.0, default=1.0)


class Box(BaseModel):
    """Bounding box in slide-relative px."""

    x: float
    y: float
    width: float
    height: float


class TextStyle(BaseModel):
    font_family: str = "Arial"
    font_size_px: float = 16.0
    bold: bool = False
    italic: bool = False
    underline: bool = False
    color: RGBAColor = Field(default_factory=lambda: RGBAColor(r=0, g=0, b=0))
    background_color: RGBAColor | None = None


class TextRun(BaseModel):
    """A run of text with uniform style."""

    text: str
    style: TextStyle = Field(default_factory=TextStyle)
    link_url: str | None = None


class Paragraph(BaseModel):
    runs: list[TextRun] = Field(default_factory=list)
    alignment: str = "left"  # left, center, right, justify
    line_height_px: float | None = None
    space_before_px: float = 0.0
    space_after_px: float = 0.0
    list_level: int | None = None
    list_ordered: bool = False
    list_style_type: str | None = None
    order_number: int | None = None


class ListItem(BaseModel):
    """A list item with nesting level."""

    runs: list[TextRun] = Field(default_factory=list)
    level: int = 0  # 0-based nesting depth
    order_number: int | None = None  # for ordered lists
    list_style_type: str | None = None
    alignment: str = "left"
    line_height_px: float | None = None
    space_before_px: float = 0.0
    space_after_px: float = 0.0


class TableCell(BaseModel):
    paragraphs: list[Paragraph] = Field(default_factory=list)
    colspan: int = 1
    rowspan: int = 1
    is_header: bool = False
    background: RGBAColor | None = None
    background_gradient: str | None = None
    padding: BoxPadding = Field(default_factory=lambda: BoxPadding())
    border_top: BorderSide = Field(default_factory=lambda: BorderSide())
    border_right: BorderSide = Field(default_factory=lambda: BorderSide())
    border_bottom: BorderSide = Field(default_factory=lambda: BorderSide())
    border_left: BorderSide = Field(default_factory=lambda: BorderSide())
    width_px: float | None = None


class TableRow(BaseModel):
    cells: list[TableCell] = Field(default_factory=list)


class BackgroundImage(BaseModel):
    """Background image information extracted from Marp's advanced background structure."""

    url: str
    size: str = "cover"  # cover, contain
    position: str = "center"  # center, left, right, top, bottom
    split: str | None = None  # left, right, or None
    image_data: bytes | None = None


class Background(BaseModel):
    color: RGBAColor | None = None
    image_path: str | None = None  # for fallback image backgrounds
    images: list[BackgroundImage] = Field(default_factory=list)  # background images


class BoxPadding(BaseModel):
    top_px: float = 0.0
    right_px: float = 0.0
    bottom_px: float = 0.0
    left_px: float = 0.0


class BorderSide(BaseModel):
    width_px: float = 0.0
    style: str = "none"
    color: RGBAColor | None = None


class BoxDecoration(BaseModel):
    background_color: RGBAColor | None = None
    background_gradient: str | None = None
    border_top: BorderSide = Field(default_factory=BorderSide)
    border_right: BorderSide = Field(default_factory=BorderSide)
    border_bottom: BorderSide = Field(default_factory=BorderSide)
    border_left: BorderSide = Field(default_factory=BorderSide)
    border_radius_px: float = 0.0
    padding: BoxPadding = Field(default_factory=BoxPadding)
    opacity: float = 1.0


class UnsupportedInfo(BaseModel):
    """Metadata about why an element is unsupported."""

    reason: str
    tag_name: str = ""
    fallback_image_path: str | None = None
    svg_markup: str | None = None


class SlideElement(BaseModel):
    element_type: ElementType
    box: Box
    content_box: Box | None = None
    z_index: int = 0

    # Text content (for heading, paragraph, blockquote, code_block)
    paragraphs: list[Paragraph] = Field(default_factory=list)
    heading_level: int | None = None  # 1-6 for headings

    # List content
    list_items: list[ListItem] = Field(default_factory=list)

    # Image content
    image_src: str | None = None
    image_data: bytes | None = None
    image_natural_width_px: float | None = None
    image_natural_height_px: float | None = None
    object_fit: str | None = None
    object_position: str | None = None
    image_opacity: float = 1.0

    # Table content
    table_rows: list[TableRow] = Field(default_factory=list)

    # Code block specific
    code_language: str | None = None
    code_background: RGBAColor | None = None

    # Generic box decoration for rendered-layout capture
    decoration: BoxDecoration | None = None

    # Unsupported info
    unsupported_info: UnsupportedInfo | None = None


class Slide(BaseModel):
    width_px: float
    height_px: float
    elements: list[SlideElement] = Field(default_factory=list)
    background: Background = Field(default_factory=Background)
    slide_number: int = 0
    is_fallback: bool = False  # True if entire slide is fallback image
    fallback_image_path: str | None = None
    notes: str | None = None  # Speaker notes text

    # Marp directives
    header_text: str | None = None
    footer_text: str | None = None
    paginate: bool = False
    page_number: int | None = None
    page_total: int | None = None


class Presentation(BaseModel):
    slides: list[Slide] = Field(default_factory=list)
    default_width_px: float = 1280.0
    default_height_px: float = 720.0
