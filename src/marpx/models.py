"""Normalized presentation model for marpx.

All coordinates are slide-relative in px.
Unit conversion to EMU happens in the PPTX builder.
"""

from __future__ import annotations
import logging
from enum import Enum
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


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


class Point(BaseModel):
    x: float
    y: float


class TextStyle(BaseModel):
    font_family: str = "Arial"
    font_size_px: float = 16.0
    bold: bool = False
    italic: bool = False
    underline: bool = False
    strike: bool = False
    color: RGBAColor = Field(default_factory=lambda: RGBAColor(r=0, g=0, b=0))
    background_color: RGBAColor | None = None
    text_gradient: str | None = None


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
    split_ratio: float | None = Field(default=None, ge=0.0, le=1.0)
    box: Box | None = None
    image_data: bytes | None = None


class Background(BaseModel):
    color: RGBAColor | None = None
    background_gradient: str | None = None
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


class BoxShadow(BaseModel):
    offset_x_px: float = 0.0
    offset_y_px: float = 0.0
    blur_radius_px: float = 0.0
    spread_px: float = 0.0
    color: RGBAColor = Field(default_factory=lambda: RGBAColor(r=0, g=0, b=0, a=0.0))
    inset: bool = False


class ClipPath(BaseModel):
    """Clip path for element clipping (e.g., CSS polygon)."""

    type: str  # e.g., 'polygon'
    points: list[Point]  # polygon vertices in percentage (0-100 range)


class BoxDecoration(BaseModel):
    background_color: RGBAColor | None = None
    background_gradient: str | None = None
    border_top: BorderSide = Field(default_factory=BorderSide)
    border_right: BorderSide = Field(default_factory=BorderSide)
    border_bottom: BorderSide = Field(default_factory=BorderSide)
    border_left: BorderSide = Field(default_factory=BorderSide)
    border_radius_px: float = 0.0
    padding: BoxPadding = Field(default_factory=BoxPadding)
    box_shadows: list[BoxShadow] = Field(default_factory=list)
    opacity: float = 1.0
    clip_path: ClipPath | None = None


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
    vertical_align: str = "top"
    rotation_deg: float = 0.0
    rotation_3d_x_deg: float = 0.0
    rotation_3d_y_deg: float = 0.0
    rotation_3d_z_deg: float = 0.0
    projected_corners: list[Point] = Field(default_factory=list)

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

    # Capability classification result set by the converter pipeline.
    # Values: "native", "subtree_fallback", "slide_fallback", or None (unclassified).
    capability: str | None = None

    # ------------------------------------------------------------------
    # Factory classmethods
    #
    # Each factory accepts only the fields relevant to that element type
    # and automatically sets element_type.  Direct SlideElement(...)
    # construction still works for backward compatibility.
    # ------------------------------------------------------------------

    @classmethod
    def _common(
        cls,
        *,
        element_type: ElementType,
        box: Box,
        content_box: Box | None = None,
        z_index: int = 0,
        vertical_align: str = "top",
        rotation_deg: float = 0.0,
        rotation_3d_x_deg: float = 0.0,
        rotation_3d_y_deg: float = 0.0,
        rotation_3d_z_deg: float = 0.0,
        projected_corners: list[Point] | None = None,
        capability: str | None = None,
    ) -> dict:
        """Build the kwargs dict shared by every factory."""
        return dict(
            element_type=element_type,
            box=box,
            content_box=content_box,
            z_index=z_index,
            vertical_align=vertical_align,
            rotation_deg=rotation_deg,
            rotation_3d_x_deg=rotation_3d_x_deg,
            rotation_3d_y_deg=rotation_3d_y_deg,
            rotation_3d_z_deg=rotation_3d_z_deg,
            projected_corners=projected_corners or [],
            capability=capability,
        )

    @classmethod
    def make_heading(
        cls,
        *,
        box: Box,
        paragraphs: list[Paragraph],
        heading_level: int = 1,
        decoration: BoxDecoration | None = None,
        content_box: Box | None = None,
        z_index: int = 0,
        vertical_align: str = "top",
        rotation_deg: float = 0.0,
        rotation_3d_x_deg: float = 0.0,
        rotation_3d_y_deg: float = 0.0,
        rotation_3d_z_deg: float = 0.0,
        projected_corners: list[Point] | None = None,
        capability: str | None = None,
    ) -> "SlideElement":
        """Create a heading element (h1-h6)."""
        return cls(
            **cls._common(
                element_type=ElementType.HEADING,
                box=box,
                content_box=content_box,
                z_index=z_index,
                vertical_align=vertical_align,
                rotation_deg=rotation_deg,
                rotation_3d_x_deg=rotation_3d_x_deg,
                rotation_3d_y_deg=rotation_3d_y_deg,
                rotation_3d_z_deg=rotation_3d_z_deg,
                projected_corners=projected_corners,
                capability=capability,
            ),
            paragraphs=paragraphs,
            heading_level=heading_level,
            decoration=decoration,
        )

    @classmethod
    def make_paragraph(
        cls,
        *,
        element_type: ElementType = ElementType.PARAGRAPH,
        box: Box,
        paragraphs: list[Paragraph],
        decoration: BoxDecoration | None = None,
        content_box: Box | None = None,
        z_index: int = 0,
        vertical_align: str = "top",
        rotation_deg: float = 0.0,
        rotation_3d_x_deg: float = 0.0,
        rotation_3d_y_deg: float = 0.0,
        rotation_3d_z_deg: float = 0.0,
        projected_corners: list[Point] | None = None,
        capability: str | None = None,
    ) -> "SlideElement":
        """Create a paragraph or blockquote element."""
        return cls(
            **cls._common(
                element_type=element_type,
                box=box,
                content_box=content_box,
                z_index=z_index,
                vertical_align=vertical_align,
                rotation_deg=rotation_deg,
                rotation_3d_x_deg=rotation_3d_x_deg,
                rotation_3d_y_deg=rotation_3d_y_deg,
                rotation_3d_z_deg=rotation_3d_z_deg,
                projected_corners=projected_corners,
                capability=capability,
            ),
            paragraphs=paragraphs,
            decoration=decoration,
        )

    @classmethod
    def make_decorated_block(
        cls,
        *,
        box: Box,
        paragraphs: list[Paragraph],
        decoration: BoxDecoration | None = None,
        content_box: Box | None = None,
        z_index: int = 0,
        vertical_align: str = "top",
        rotation_deg: float = 0.0,
        rotation_3d_x_deg: float = 0.0,
        rotation_3d_y_deg: float = 0.0,
        rotation_3d_z_deg: float = 0.0,
        projected_corners: list[Point] | None = None,
        capability: str | None = None,
    ) -> "SlideElement":
        """Create a decorated_block element (e.g. blockquote with visual decoration)."""
        return cls(
            **cls._common(
                element_type=ElementType.DECORATED_BLOCK,
                box=box,
                content_box=content_box,
                z_index=z_index,
                vertical_align=vertical_align,
                rotation_deg=rotation_deg,
                rotation_3d_x_deg=rotation_3d_x_deg,
                rotation_3d_y_deg=rotation_3d_y_deg,
                rotation_3d_z_deg=rotation_3d_z_deg,
                projected_corners=projected_corners,
                capability=capability,
            ),
            paragraphs=paragraphs,
            decoration=decoration,
        )

    @classmethod
    def make_list(
        cls,
        *,
        element_type: ElementType,
        box: Box,
        list_items: list[ListItem],
        content_box: Box | None = None,
        z_index: int = 0,
        vertical_align: str = "top",
        rotation_deg: float = 0.0,
        rotation_3d_x_deg: float = 0.0,
        rotation_3d_y_deg: float = 0.0,
        rotation_3d_z_deg: float = 0.0,
        projected_corners: list[Point] | None = None,
        capability: str | None = None,
    ) -> "SlideElement":
        """Create an unordered_list or ordered_list element."""
        if element_type not in (ElementType.UNORDERED_LIST, ElementType.ORDERED_LIST):
            raise ValueError(
                f"make_list requires UNORDERED_LIST or ORDERED_LIST, got {element_type}"
            )
        return cls(
            **cls._common(
                element_type=element_type,
                box=box,
                content_box=content_box,
                z_index=z_index,
                vertical_align=vertical_align,
                rotation_deg=rotation_deg,
                rotation_3d_x_deg=rotation_3d_x_deg,
                rotation_3d_y_deg=rotation_3d_y_deg,
                rotation_3d_z_deg=rotation_3d_z_deg,
                projected_corners=projected_corners,
                capability=capability,
            ),
            list_items=list_items,
        )

    @classmethod
    def make_code_block(
        cls,
        *,
        box: Box,
        paragraphs: list[Paragraph],
        code_language: str | None = None,
        code_background: RGBAColor | None = None,
        decoration: BoxDecoration | None = None,
        content_box: Box | None = None,
        z_index: int = 0,
        vertical_align: str = "top",
        rotation_deg: float = 0.0,
        rotation_3d_x_deg: float = 0.0,
        rotation_3d_y_deg: float = 0.0,
        rotation_3d_z_deg: float = 0.0,
        projected_corners: list[Point] | None = None,
        capability: str | None = None,
    ) -> "SlideElement":
        """Create a code_block element."""
        return cls(
            **cls._common(
                element_type=ElementType.CODE_BLOCK,
                box=box,
                content_box=content_box,
                z_index=z_index,
                vertical_align=vertical_align,
                rotation_deg=rotation_deg,
                rotation_3d_x_deg=rotation_3d_x_deg,
                rotation_3d_y_deg=rotation_3d_y_deg,
                rotation_3d_z_deg=rotation_3d_z_deg,
                projected_corners=projected_corners,
                capability=capability,
            ),
            paragraphs=paragraphs,
            code_language=code_language,
            code_background=code_background,
            decoration=decoration,
        )

    @classmethod
    def make_image(
        cls,
        *,
        box: Box,
        image_src: str | None = None,
        image_data: bytes | None = None,
        image_natural_width_px: float | None = None,
        image_natural_height_px: float | None = None,
        object_fit: str | None = None,
        object_position: str | None = None,
        image_opacity: float = 1.0,
        decoration: BoxDecoration | None = None,
        content_box: Box | None = None,
        z_index: int = 0,
        vertical_align: str = "top",
        rotation_deg: float = 0.0,
        rotation_3d_x_deg: float = 0.0,
        rotation_3d_y_deg: float = 0.0,
        rotation_3d_z_deg: float = 0.0,
        projected_corners: list[Point] | None = None,
        capability: str | None = None,
    ) -> "SlideElement":
        """Create an image element."""
        return cls(
            **cls._common(
                element_type=ElementType.IMAGE,
                box=box,
                content_box=content_box,
                z_index=z_index,
                vertical_align=vertical_align,
                rotation_deg=rotation_deg,
                rotation_3d_x_deg=rotation_3d_x_deg,
                rotation_3d_y_deg=rotation_3d_y_deg,
                rotation_3d_z_deg=rotation_3d_z_deg,
                projected_corners=projected_corners,
                capability=capability,
            ),
            image_src=image_src,
            image_data=image_data,
            image_natural_width_px=image_natural_width_px,
            image_natural_height_px=image_natural_height_px,
            object_fit=object_fit,
            object_position=object_position,
            image_opacity=image_opacity,
            decoration=decoration,
        )

    @classmethod
    def make_table(
        cls,
        *,
        box: Box,
        table_rows: list[TableRow],
        decoration: BoxDecoration | None = None,
        content_box: Box | None = None,
        z_index: int = 0,
        vertical_align: str = "top",
        rotation_deg: float = 0.0,
        rotation_3d_x_deg: float = 0.0,
        rotation_3d_y_deg: float = 0.0,
        rotation_3d_z_deg: float = 0.0,
        projected_corners: list[Point] | None = None,
        capability: str | None = None,
    ) -> "SlideElement":
        """Create a table element."""
        return cls(
            **cls._common(
                element_type=ElementType.TABLE,
                box=box,
                content_box=content_box,
                z_index=z_index,
                vertical_align=vertical_align,
                rotation_deg=rotation_deg,
                rotation_3d_x_deg=rotation_3d_x_deg,
                rotation_3d_y_deg=rotation_3d_y_deg,
                rotation_3d_z_deg=rotation_3d_z_deg,
                projected_corners=projected_corners,
                capability=capability,
            ),
            table_rows=table_rows,
            decoration=decoration,
        )

    @classmethod
    def make_math(
        cls,
        *,
        box: Box,
        unsupported_info: UnsupportedInfo,
        content_box: Box | None = None,
        z_index: int = 0,
        vertical_align: str = "top",
        rotation_deg: float = 0.0,
        rotation_3d_x_deg: float = 0.0,
        rotation_3d_y_deg: float = 0.0,
        rotation_3d_z_deg: float = 0.0,
        projected_corners: list[Point] | None = None,
        capability: str | None = None,
    ) -> "SlideElement":
        """Create a math element."""
        return cls(
            **cls._common(
                element_type=ElementType.MATH,
                box=box,
                content_box=content_box,
                z_index=z_index,
                vertical_align=vertical_align,
                rotation_deg=rotation_deg,
                rotation_3d_x_deg=rotation_3d_x_deg,
                rotation_3d_y_deg=rotation_3d_y_deg,
                rotation_3d_z_deg=rotation_3d_z_deg,
                projected_corners=projected_corners,
                capability=capability,
            ),
            unsupported_info=unsupported_info,
        )

    @classmethod
    def make_unsupported(
        cls,
        *,
        box: Box,
        unsupported_info: UnsupportedInfo,
        content_box: Box | None = None,
        z_index: int = 0,
        vertical_align: str = "top",
        rotation_deg: float = 0.0,
        rotation_3d_x_deg: float = 0.0,
        rotation_3d_y_deg: float = 0.0,
        rotation_3d_z_deg: float = 0.0,
        projected_corners: list[Point] | None = None,
        capability: str | None = None,
    ) -> "SlideElement":
        """Create an unsupported element."""
        return cls(
            **cls._common(
                element_type=ElementType.UNSUPPORTED,
                box=box,
                content_box=content_box,
                z_index=z_index,
                vertical_align=vertical_align,
                rotation_deg=rotation_deg,
                rotation_3d_x_deg=rotation_3d_x_deg,
                rotation_3d_y_deg=rotation_3d_y_deg,
                rotation_3d_z_deg=rotation_3d_z_deg,
                projected_corners=projected_corners,
                capability=capability,
            ),
            unsupported_info=unsupported_info,
        )

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
