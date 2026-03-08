"""Extract slide content from Marp-rendered HTML using Playwright."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from playwright.async_api import async_playwright

from marpx.models import (
    Background,
    BackgroundImage,
    BorderSide,
    Box,
    BoxDecoration,
    BoxPadding,
    ElementType,
    ListItem,
    Paragraph,
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
from marpx.utils import (
    boxes_have_mergeable_vertical_gap,
    boxes_share_column,
    parse_css_color,
    union_boxes,
)

logger = logging.getLogger(__name__)

_JS_DIR = Path(__file__).parent
_EXTRACT_NOTES_JS = (_JS_DIR / "extract_notes.js").read_text(encoding="utf-8")

TEXTBOX_MERGE_TYPES: tuple[ElementType, ...] = (
    ElementType.PARAGRAPH,
    ElementType.BLOCKQUOTE,
)


def _load_js_bundle(bundle_name: str) -> str:
    """Load a browser-evaluated JS bundle, auto-building if needed."""
    bundle_file = _JS_DIR / f"{bundle_name}.bundle.js"
    bundle_dir = _JS_DIR / f"{bundle_name}_js"

    if not bundle_dir.exists():
        raise FileNotFoundError(f"JS bundle directory not found: {bundle_dir}")

    # Check if rebuild is needed
    needs_build = not bundle_file.exists()
    if not needs_build:
        bundle_mtime = bundle_file.stat().st_mtime
        for src in bundle_dir.glob("*.js"):
            if src.name == "build.mjs":
                continue
            if src.stat().st_mtime > bundle_mtime:
                needs_build = True
                break

    if needs_build:
        import subprocess

        # Ensure esbuild is installed
        node_modules = bundle_dir / "node_modules"
        if not node_modules.exists():
            subprocess.run(
                ["npm", "install", "--no-audit", "--no-fund"],
                cwd=str(bundle_dir),
                capture_output=True,
                text=True,
                check=True,
            )

        result = subprocess.run(
            ["node", str(bundle_dir / "build.mjs")],
            cwd=str(bundle_dir),
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"Failed to build JS bundle '{bundle_name}': {result.stderr}"
            )
        if not bundle_file.exists():
            raise FileNotFoundError(
                f"Bundle file not created after build: {bundle_file}"
            )

    return bundle_file.read_text(encoding="utf-8")


EXTRACT_JS = _load_js_bundle("extract_slides")


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
        color=color,
        background_color=background_color,
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
        opacity=raw.get("opacity", 1.0),
    )


def _build_slide_element(raw: dict) -> SlideElement:
    """Convert raw JS element dict to SlideElement model."""
    etype = ElementType(raw["type"])
    box = Box(**raw["box"])
    content_box = Box(**raw["contentBox"]) if raw.get("contentBox") else None

    element = SlideElement(element_type=etype, box=box, content_box=content_box)
    element.z_index = raw.get("zIndex", 0) or 0

    if etype in (
        ElementType.HEADING,
        ElementType.PARAGRAPH,
        ElementType.BLOCKQUOTE,
    ):
        element.paragraphs = _build_paragraphs([raw])
        element.decoration = _build_decoration(raw.get("decoration"))

        if etype == ElementType.HEADING:
            element.heading_level = raw.get("headingLevel", 1)

    elif etype == ElementType.CODE_BLOCK:
        element.paragraphs = _build_paragraphs(raw.get("paragraphs", []))
        element.code_language = raw.get("codeLanguage")
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
        element.decoration = _build_decoration(raw.get("decoration"))

    elif etype == ElementType.TABLE:
        for row_raw in raw.get("tableRows", []):
            cells = []
            for cell_raw in row_raw.get("cells", []):
                colspan = cell_raw.get("colspan", 1)
                rowspan = cell_raw.get("rowspan", 1)

                cell_runs = _build_text_runs(cell_raw.get("runs", []))
                bg = None
                if cell_raw.get("backgroundColor"):
                    bg = parse_css_color(cell_raw["backgroundColor"])

                cells.append(
                    TableCell(
                        paragraphs=[Paragraph(runs=cell_runs)],
                        colspan=colspan,
                        rowspan=rowspan,
                        is_header=cell_raw.get("isHeader", False),
                        background=bg,
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

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Load the HTML
        await page.goto(file_url, wait_until="networkidle")

        # Wait for Marp rendering
        await page.wait_for_selector("section", timeout=10000)

        # Extract all slide data in one batch
        raw_slides = await page.evaluate(EXTRACT_JS)

        # Extract speaker notes (stored outside slide sections)
        raw_notes = await page.evaluate(_EXTRACT_NOTES_JS)

        await browser.close()

    if not raw_slides:
        logger.warning("No slides found in HTML")
        return Presentation()

    # Determine default slide size from first slide
    default_w = raw_slides[0].get("width", 1280)
    default_h = raw_slides[0].get("height", 720)

    slides = []
    for raw_slide in raw_slides:
        bg_color = None
        if raw_slide.get("background", {}).get("color"):
            bg_color = parse_css_color(raw_slide["background"]["color"])

        # Build background images list
        bg_images: list[BackgroundImage] = []
        for raw_bg_img in raw_slide.get("background", {}).get("images", []):
            bg_images.append(
                BackgroundImage(
                    url=raw_bg_img["url"],
                    size=raw_bg_img.get("size", "cover"),
                    position=raw_bg_img.get("position", "center"),
                    split=raw_bg_img.get("split"),
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
            background=Background(color=bg_color, images=bg_images),
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


def extract_presentation_sync(html_path: str | Path) -> Presentation:
    """Synchronous wrapper for extract_presentation."""
    return asyncio.run(extract_presentation(html_path))
