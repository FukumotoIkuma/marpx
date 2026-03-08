"""Extract slide content from Marp-rendered HTML using Playwright."""

from __future__ import annotations

import atexit
import logging
from pathlib import Path

from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright

from marpx.models import (
    Background,
    BackgroundImage,
    BorderSide,
    Box,
    BoxDecoration,
    BoxShadow,
    BoxPadding,
    ElementType,
    ListItem,
    Paragraph,
    Point,
    Presentation,
    Slide,
    SlideElement,
    TableCell,
    TableRow,
    TextRun,
    TextStyle,
    UnsupportedInfo,
)
from marpx.fonts import safe_font_family
from marpx.js_bundle import load_extract_bundle
from marpx.utils import (
    boxes_have_mergeable_vertical_gap,
    boxes_share_column,
    parse_css_color,
    union_boxes,
)

logger = logging.getLogger(__name__)
_JS_DIR = Path(__file__).parent
_EXTRACT_NOTES_JS = (_JS_DIR / "extract_notes.js").read_text(encoding="utf-8")
_SYNC_PLAYWRIGHT = None
_SYNC_BROWSER = None

TEXTBOX_MERGE_TYPES: tuple[ElementType, ...] = (
    ElementType.PARAGRAPH,
    ElementType.BLOCKQUOTE,
)


def _build_text_style(raw_style: dict) -> TextStyle:
    """Convert raw JS style dict to TextStyle model."""
    color = parse_css_color(raw_style.get("color", "rgb(0,0,0)"))
    background_color = None
    raw_bg = raw_style.get("backgroundColor")
    if raw_bg:
        parsed_bg = parse_css_color(raw_bg)
        if parsed_bg.a > 0:
            background_color = parsed_bg
    return TextStyle(
        font_family=safe_font_family(raw_style.get("fontFamily", "Arial")),
        font_size_px=raw_style.get("fontSizePx", 16.0),
        bold=raw_style.get("bold", False),
        italic=raw_style.get("italic", False),
        underline=raw_style.get("underline", False),
        strike=raw_style.get("strike", False),
        color=color,
        background_color=background_color,
        text_gradient=raw_style.get("textGradient"),
    )


def _build_text_runs(raw_runs: list[dict]) -> list[TextRun]:
    """Convert raw JS runs to TextRun models."""
    runs = []
    for raw in raw_runs:
        runs.append(
            TextRun(
                text=raw["text"],
                style=_build_text_style(raw.get("style", {})),
                link_url=raw.get("linkUrl"),
            )
        )
    return runs


def _build_paragraphs(raw_paragraphs: list[dict]) -> list[Paragraph]:
    """Convert raw JS paragraph dicts to Paragraph models."""
    paragraphs = []
    for raw in raw_paragraphs:
        paragraphs.append(
            Paragraph(
                runs=_build_text_runs(raw.get("runs", [])),
                alignment=raw.get("alignment", "left"),
                line_height_px=raw.get("lineHeightPx"),
                space_before_px=raw.get("spaceBeforePx", 0.0),
                space_after_px=raw.get("spaceAfterPx", 0.0),
                list_level=raw.get("listLevel"),
                list_ordered=raw.get("listOrdered", False),
                list_style_type=raw.get("listStyleType"),
                order_number=raw.get("orderNumber"),
            )
        )
    return paragraphs


def _build_border_side(raw_side: dict | None) -> BorderSide:
    """Convert raw border side dict to BorderSide."""
    if not raw_side:
        return BorderSide()
    color = None
    if raw_side.get("color"):
        color = parse_css_color(raw_side["color"])
    return BorderSide(
        width_px=raw_side.get("widthPx", 0.0),
        style=raw_side.get("style", "none"),
        color=color,
    )


def _build_decoration(raw: dict | None) -> BoxDecoration | None:
    """Convert raw JS decoration dict to BoxDecoration."""
    if not raw:
        return None
    background_color = None
    raw_bg = raw.get("backgroundColor")
    if raw_bg:
        parsed_bg = parse_css_color(raw_bg)
        if parsed_bg.a > 0:
            background_color = parsed_bg
    raw_padding = raw.get("padding", {})
    return BoxDecoration(
        background_color=background_color,
        background_gradient=raw.get("backgroundGradient"),
        border_top=_build_border_side(raw.get("borderTop")),
        border_right=_build_border_side(raw.get("borderRight")),
        border_bottom=_build_border_side(raw.get("borderBottom")),
        border_left=_build_border_side(raw.get("borderLeft")),
        border_radius_px=raw.get("borderRadiusPx", 0.0),
        padding=BoxPadding(
            top_px=raw_padding.get("topPx", 0.0),
            right_px=raw_padding.get("rightPx", 0.0),
            bottom_px=raw_padding.get("bottomPx", 0.0),
            left_px=raw_padding.get("leftPx", 0.0),
        ),
        box_shadows=[
            BoxShadow(
                offset_x_px=shadow.get("offsetXPx", 0.0),
                offset_y_px=shadow.get("offsetYPx", 0.0),
                blur_radius_px=shadow.get("blurRadiusPx", 0.0),
                spread_px=shadow.get("spreadPx", 0.0),
                color=parse_css_color(shadow.get("color", "rgba(0,0,0,0)")),
                inset=shadow.get("inset", False),
            )
            for shadow in raw.get("boxShadows", [])
        ],
        opacity=raw.get("opacity", 1.0),
    )


def _build_slide_element(raw: dict) -> SlideElement:
    """Convert raw JS element dict to SlideElement model."""
    etype = ElementType(raw["type"])
    box = Box(**raw["box"])
    content_box = Box(**raw["contentBox"]) if raw.get("contentBox") else None

    element = SlideElement(element_type=etype, box=box, content_box=content_box)
    element.z_index = raw.get("zIndex", 0) or 0
    element.vertical_align = raw.get("verticalAlign", "top")
    element.rotation_deg = raw.get("rotationDeg", 0.0) or 0.0
    element.rotation_3d_x_deg = raw.get("rotation3dXDeg", 0.0) or 0.0
    element.rotation_3d_y_deg = raw.get("rotation3dYDeg", 0.0) or 0.0
    element.rotation_3d_z_deg = raw.get("rotation3dZDeg", 0.0) or 0.0
    element.projected_corners = [
        Point(**corner) for corner in raw.get("projectedCorners", [])
    ]

    if etype in (
        ElementType.HEADING,
        ElementType.PARAGRAPH,
        ElementType.BLOCKQUOTE,
    ):
        if "paragraphs" in raw:
            element.paragraphs = _build_paragraphs(raw.get("paragraphs", []))
        else:
            element.paragraphs = _build_paragraphs([raw])
        element.decoration = _build_decoration(raw.get("decoration"))

        if etype == ElementType.HEADING:
            element.heading_level = raw.get("headingLevel", 1)

    elif etype == ElementType.CODE_BLOCK:
        element.paragraphs = _build_paragraphs(raw.get("paragraphs", []))
        element.code_language = raw.get("codeLanguage")
        element.decoration = _build_decoration(raw.get("decoration"))
        if raw.get("codeBackground"):
            element.code_background = parse_css_color(raw["codeBackground"])

    elif etype == ElementType.DECORATED_BLOCK:
        element.paragraphs = _build_paragraphs(raw.get("paragraphs", []))
        element.decoration = _build_decoration(raw.get("decoration"))

    elif etype in (ElementType.UNORDERED_LIST, ElementType.ORDERED_LIST):
        for item_raw in raw.get("listItems", []):
            runs = _build_text_runs(item_raw.get("runs", []))
            element.list_items.append(
                ListItem(
                    runs=runs,
                    level=item_raw.get("level", 0),
                    order_number=item_raw.get("orderNumber"),
                    list_style_type=item_raw.get("listStyleType"),
                    alignment=item_raw.get("alignment", "left"),
                    line_height_px=item_raw.get("lineHeightPx"),
                    space_before_px=item_raw.get("spaceBeforePx", 0.0),
                    space_after_px=item_raw.get("spaceAfterPx", 0.0),
                )
            )

    elif etype == ElementType.IMAGE:
        element.image_src = raw.get("imageSrc")
        element.image_natural_width_px = raw.get("imageNaturalWidthPx")
        element.image_natural_height_px = raw.get("imageNaturalHeightPx")
        element.object_fit = raw.get("objectFit")
        element.object_position = raw.get("objectPosition")
        element.image_opacity = raw.get("imageOpacity", 1.0)
        element.decoration = _build_decoration(raw.get("decoration"))

    elif etype == ElementType.TABLE:
        element.decoration = _build_decoration(raw.get("decoration"))
        for row_raw in raw.get("tableRows", []):
            cells = []
            for cell_raw in row_raw.get("cells", []):
                colspan = cell_raw.get("colspan", 1)
                rowspan = cell_raw.get("rowspan", 1)

                cell_runs = _build_text_runs(cell_raw.get("runs", []))
                bg = None
                if cell_raw.get("backgroundColor"):
                    parsed_bg = parse_css_color(cell_raw["backgroundColor"])
                    if parsed_bg.a > 0:
                        bg = parsed_bg
                raw_padding = cell_raw.get("padding", {})

                cells.append(
                    TableCell(
                        paragraphs=[Paragraph(runs=cell_runs)],
                        colspan=colspan,
                        rowspan=rowspan,
                        is_header=cell_raw.get("isHeader", False),
                        background=bg,
                        background_gradient=cell_raw.get("backgroundGradient"),
                        padding=BoxPadding(
                            top_px=raw_padding.get("topPx", 0.0),
                            right_px=raw_padding.get("rightPx", 0.0),
                            bottom_px=raw_padding.get("bottomPx", 0.0),
                            left_px=raw_padding.get("leftPx", 0.0),
                        ),
                        border_top=_build_border_side(cell_raw.get("borderTop")),
                        border_right=_build_border_side(cell_raw.get("borderRight")),
                        border_bottom=_build_border_side(cell_raw.get("borderBottom")),
                        border_left=_build_border_side(cell_raw.get("borderLeft")),
                        width_px=cell_raw.get("widthPx"),
                    )
                )
            element.table_rows.append(TableRow(cells=cells))

    elif etype == ElementType.MATH:
        info = raw.get("unsupportedInfo", {})
        element.unsupported_info = UnsupportedInfo(
            reason=info.get("reason", "Math expression"),
            tag_name=info.get("tagName", "mjx-container"),
            svg_markup=info.get("svgMarkup"),
        )

    elif etype == ElementType.UNSUPPORTED:
        info = raw.get("unsupportedInfo", {})
        element.unsupported_info = UnsupportedInfo(
            reason=info.get("reason", "Unknown"),
            tag_name=info.get("tagName", ""),
            svg_markup=info.get("svgMarkup"),
        )

    return element


def _build_presentation_from_raw(
    raw_slides: list[dict], raw_notes: dict[str, str]
) -> Presentation:
    """Convert raw extracted slide payloads into a Presentation model."""
    if not raw_slides:
        logger.warning("No slides found in HTML")
        return Presentation()

    default_w = raw_slides[0].get("width", 1280)
    default_h = raw_slides[0].get("height", 720)

    slides = []
    for raw_slide in raw_slides:
        bg_color = None
        if raw_slide.get("background", {}).get("color"):
            bg_color = parse_css_color(raw_slide["background"]["color"])

        bg_images: list[BackgroundImage] = []
        for raw_bg_img in raw_slide.get("background", {}).get("images", []):
            bg_images.append(
                BackgroundImage(
                    url=raw_bg_img["url"],
                    size=raw_bg_img.get("size", "cover"),
                    position=raw_bg_img.get("position", "center"),
                    split=raw_bg_img.get("split"),
                    split_ratio=raw_bg_img.get("splitRatio"),
                    box=Box(**raw_bg_img["box"]) if raw_bg_img.get("box") else None,
                )
            )

        elements = []
        for raw_el in raw_slide.get("elements", []):
            try:
                elements.append(_build_slide_element(raw_el))
            except Exception as e:
                logger.warning("Failed to build element: %s", e)
        elements = _merge_same_type_paragraphs(elements)

        slide_number = raw_slide.get("slideNumber", 0)
        note_text = raw_notes.get(str(slide_number))
        directives = raw_slide.get("directives", {})

        slide = Slide(
            width_px=raw_slide.get("width", default_w),
            height_px=raw_slide.get("height", default_h),
            elements=elements,
            background=Background(
                color=bg_color,
                background_gradient=raw_slide.get("background", {}).get(
                    "backgroundGradient"
                ),
                images=bg_images,
            ),
            slide_number=slide_number,
            notes=note_text if note_text else None,
            header_text=directives.get("headerText") or None,
            footer_text=directives.get("footerText") or None,
            paginate=directives.get("paginate", False),
            page_number=directives.get("pageNumber"),
            page_total=directives.get("pageTotal"),
        )
        slides.append(slide)

    return Presentation(
        slides=slides,
        default_width_px=default_w,
        default_height_px=default_h,
    )


def _close_sync_browser() -> None:
    """Close the shared sync Playwright browser if it exists."""
    global _SYNC_BROWSER, _SYNC_PLAYWRIGHT
    if _SYNC_BROWSER is not None:
        _SYNC_BROWSER.close()
        _SYNC_BROWSER = None
    if _SYNC_PLAYWRIGHT is not None:
        _SYNC_PLAYWRIGHT.stop()
        _SYNC_PLAYWRIGHT = None


def close_sync_browser() -> None:
    """Public wrapper to close the shared sync Playwright browser."""
    _close_sync_browser()


def _get_sync_browser():
    """Return a shared sync Chromium browser for repeated sync extraction calls."""
    global _SYNC_BROWSER, _SYNC_PLAYWRIGHT
    if _SYNC_BROWSER is None:
        _SYNC_PLAYWRIGHT = sync_playwright().start()
        _SYNC_BROWSER = _SYNC_PLAYWRIGHT.chromium.launch()
    return _SYNC_BROWSER


atexit.register(_close_sync_browser)


def _should_merge_same_type_paragraphs(
    first: SlideElement, second: SlideElement
) -> bool:
    """Return True when adjacent extracted text elements should merge."""
    return (
        first.element_type == second.element_type
        and first.element_type in TEXTBOX_MERGE_TYPES
        and first.decoration is None
        and second.decoration is None
        and boxes_share_column(first.box, second.box)
        and boxes_have_mergeable_vertical_gap(first.box, second.box)
    )


def _merge_same_type_paragraphs(elements: list[SlideElement]) -> list[SlideElement]:
    """Merge adjacent paragraph-like elements into a single textbox element.

    This keeps multiple Markdown paragraphs in one PowerPoint textbox while
    preserving paragraph breaks inside the text frame.
    """
    if not elements:
        return []

    merged: list[SlideElement] = []
    current = elements[0].model_copy(deep=True)

    for element in elements[1:]:
        if _should_merge_same_type_paragraphs(current, element):
            current.paragraphs.extend(element.paragraphs)
            current.box = union_boxes([current.box, element.box])
            continue

        merged.append(current)
        current = element.model_copy(deep=True)

    merged.append(current)
    return merged


async def extract_presentation(html_path: str | Path) -> Presentation:
    """Extract presentation data from Marp HTML using Playwright.

    Args:
        html_path: Path to the Marp-generated HTML file.

    Returns:
        Normalized Presentation model with all slides and elements.
    """
    html_path = Path(html_path).resolve()
    file_url = html_path.as_uri()
    extract_js = load_extract_bundle()

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Load the HTML
        await page.goto(file_url, wait_until="networkidle")

        # Wait for Marp rendering
        await page.wait_for_selector("section", timeout=10000)

        # Extract all slide data in one batch
        raw_slides = await page.evaluate(extract_js)

        # Extract speaker notes (stored outside slide sections)
        raw_notes = await page.evaluate(_EXTRACT_NOTES_JS)

        await browser.close()

    return _build_presentation_from_raw(raw_slides, raw_notes)


def extract_presentation_sync(html_path: str | Path) -> Presentation:
    """Synchronous wrapper for extract_presentation."""
    html_path = Path(html_path).resolve()
    file_url = html_path.as_uri()
    extract_js = load_extract_bundle()
    browser = _get_sync_browser()
    page = browser.new_page()
    try:
        page.goto(file_url, wait_until="networkidle")
        page.wait_for_selector("section", timeout=10000)
        raw_slides = page.evaluate(extract_js)
        raw_notes = page.evaluate(_EXTRACT_NOTES_JS)
    finally:
        page.close()
    return _build_presentation_from_raw(raw_slides, raw_notes)
