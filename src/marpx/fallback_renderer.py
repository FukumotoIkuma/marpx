"""Render fallback images for unsupported content using Playwright screenshots."""

from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from pathlib import Path

from playwright.async_api import async_playwright

from marpx.models import (
    ElementType,
    Presentation,
    SlideElement,
    UnsupportedInfo,
)
from marpx.svg_utils import rasterize_svg_to_png

logger = logging.getLogger(__name__)
_SVG_FALLBACK_SCALE = 2.0

_BESPOKE_UI_HIDE_CSS = """
.bespoke-marp-osc,
.bespoke-progress-parent,
.bespoke-marp-presenter-container,
.bespoke-marp-presenter-osc,
[data-bespoke-view="presenter"] .bespoke-marp-parent,
[data-bespoke-view="next"] .bespoke-marp-parent {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
}
""".strip()


def _needs_subtree_fallback(element: SlideElement) -> bool:
    """Return True when an element requires a subtree (element-level) fallback.

    Uses the capability field when set by the converter pipeline; falls back to
    the legacy element_type check when capability is None (backward compatibility
    for callers that construct SlideElement objects directly without running the
    full pipeline).
    """
    if element.capability is not None:
        return element.capability == "subtree_fallback"
    # Backward-compatible legacy check
    return element.element_type in (ElementType.UNSUPPORTED, ElementType.MATH)


def _is_inline_svg_element(element: SlideElement) -> bool:
    """Return True when the fallback element carries inline SVG markup."""
    info = element.unsupported_info
    return bool(
        _needs_subtree_fallback(element)
        and info
        and info.svg_markup
    )


def _write_inline_svg_fallback(
    slide_index: int,
    element_index: int,
    element: SlideElement,
    output_dir: Path,
) -> Path:
    """Rasterize stored SVG markup directly instead of screenshotting the page."""
    output_path = output_dir / f"slide_{slide_index}_el_{element_index}_fallback.png"
    svg_markup = (
        element.unsupported_info.svg_markup if element.unsupported_info else ""
    ) or ""
    sized_svg = _resize_svg_markup(svg_markup, element.box.width, element.box.height)
    output_path.write_bytes(
        rasterize_svg_to_png(
            sized_svg,
            width_px=element.box.width,
            height_px=element.box.height,
            scale=_SVG_FALLBACK_SCALE,
        )
    )
    logger.info("Element fallback rasterized from inline SVG: %s", output_path)
    return output_path


def _resize_svg_markup(svg_markup: str, width_px: float, height_px: float) -> bytes:
    """Normalize SVG dimensions to the measured element box before rasterizing."""
    if not svg_markup:
        return b""

    root = ET.fromstring(svg_markup)
    width = max(width_px, 1.0)
    height = max(height_px, 1.0)
    root.set("width", f"{width:.3f}px")
    root.set("height", f"{height:.3f}px")

    style = root.get("style", "")
    style_parts = [
        part.strip()
        for part in style.split(";")
        if part.strip()
        and not part.strip().startswith("width:")
        and not part.strip().startswith("height:")
    ]
    style_parts.append(f"width:{width:.3f}px")
    style_parts.append(f"height:{height:.3f}px")
    root.set("style", ";".join(style_parts))
    return ET.tostring(root, encoding="utf-8")


def _is_content_section(
    *,
    parent_tag: str | None,
    parent_has_marpit: bool,
    advanced_background_role: str | None,
) -> bool:
    """Match the extractor's slide-section selection rules."""
    if advanced_background_role in {"background", "pseudo"}:
        return False
    if parent_has_marpit:
        return True
    return parent_tag in {"BODY", "DIV"}


async def _get_slide_sections(page) -> list:
    """Return the section elements that correspond to logical slides."""
    id_sections = await page.query_selector_all("section[id]")
    if id_sections:
        return id_sections

    sections = await page.query_selector_all("section")
    content_sections = []
    fallback_sections = []

    for section in sections:
        parent_tag = await section.evaluate(
            "el => el.parentElement ? el.parentElement.tagName : null"
        )
        parent_has_marpit = await section.evaluate(
            "el => !!(el.parentElement && el.parentElement.classList.contains('marpit'))"
        )
        advanced_background_role = await section.get_attribute(
            "data-marpit-advanced-background"
        )
        if _is_content_section(
            parent_tag=parent_tag,
            parent_has_marpit=parent_has_marpit,
            advanced_background_role=advanced_background_role,
        ):
            content_sections.append(section)
        elif advanced_background_role is None:
            fallback_sections.append(section)

    return content_sections or fallback_sections or sections


async def _screenshot_slide(
    page,
    slide_index: int,
    output_dir: Path,
) -> Path:
    """Take a screenshot of an entire slide section."""
    output_path = output_dir / f"slide_{slide_index}_fallback.png"

    top_sections = await _get_slide_sections(page)

    if slide_index < len(top_sections):
        section = top_sections[slide_index]
        await section.screenshot(path=str(output_path))
        logger.info("Slide %d fallback screenshot: %s", slide_index, output_path)
        return output_path

    logger.warning("Could not find section for slide %d", slide_index)
    return output_path


async def _hide_bespoke_ui(page) -> None:
    """Hide Marp/Bespoke viewer UI so fallback screenshots capture slide content only."""
    await page.add_style_tag(content=_BESPOKE_UI_HIDE_CSS)


async def _wait_for_mathjax(page) -> None:
    """Wait until MathJax containers have rendered their SVG output."""
    await page.wait_for_function(
        """() => {
            const math = Array.from(document.querySelectorAll('mjx-container'));
            return math.length === 0 || math.every((el) => !!el.querySelector('svg'));
        }""",
        timeout=10000,
    )


async def _navigate_to_slide(page, slide_index: int) -> None:
    """Use Marp/Bespoke slide controls to navigate to the requested slide."""
    await page.evaluate(
        """(targetIndex) => {
            const prev = document.querySelector('button[title="Previous slide"]');
            const next = document.querySelector('button[title="Next slide"]');
            const waitFrame = () =>
                new Promise((resolve) =>
                    requestAnimationFrame(() => requestAnimationFrame(resolve))
                );

            return (async () => {
                if (!prev || !next) return;
                while (!prev.disabled) {
                    prev.click();
                    await waitFrame();
                }
                for (let index = 0; index < targetIndex; index += 1) {
                    if (next.disabled) break;
                    next.click();
                    await waitFrame();
                }
            })();
        }""",
        slide_index,
    )


async def _screenshot_element(
    page,
    slide_index: int,
    element_index: int,
    element: SlideElement,
    output_dir: Path,
) -> Path:
    """Take a screenshot of a specific unsupported element region."""
    output_path = output_dir / f"slide_{slide_index}_el_{element_index}_fallback.png"

    top_sections = await _get_slide_sections(page)

    if slide_index < len(top_sections):
        section = top_sections[slide_index]
        section_box = await section.bounding_box()

        if section_box:
            # Calculate absolute position for the element
            clip = {
                "x": section_box["x"] + element.box.x,
                "y": section_box["y"] + element.box.y,
                "width": max(element.box.width, 1),
                "height": max(element.box.height, 1),
            }
            await page.screenshot(path=str(output_path), clip=clip)
            logger.info("Element fallback screenshot: %s", output_path)
            return output_path

    logger.warning("Could not screenshot element at slide %d", slide_index)
    return output_path


async def render_fallbacks(
    html_path: str | Path,
    presentation: Presentation,
    output_dir: str | Path,
    fallback_mode: str = "subtree",
) -> Presentation:
    """Render fallback images for unsupported content.

    Args:
        html_path: Path to the Marp HTML file.
        presentation: Extracted presentation model.
        output_dir: Directory for fallback images.
        fallback_mode: "subtree" for element-level, "slide" for slide-level fallback.

    Returns:
        Updated Presentation with fallback image paths set.
    """
    html_path = Path(html_path).resolve()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Check if any fallbacks are needed
    needs_fallback = False
    for slide in presentation.slides:
        if slide.is_fallback and not slide.fallback_image_path:
            needs_fallback = True
            break
        for el in slide.elements:
            if _needs_subtree_fallback(el):
                needs_fallback = True
                break
        if needs_fallback:
            break

    if not needs_fallback:
        logger.info("No unsupported elements found, skipping fallback rendering")
        return presentation

    file_url = html_path.as_uri()

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            device_scale_factor=2
        )  # 2x DPI for crisp rendering
        await page.goto(file_url, wait_until="networkidle")
        await page.wait_for_selector("section", timeout=10000)
        await _hide_bespoke_ui(page)
        await _wait_for_mathjax(page)

        for slide_idx, slide in enumerate(presentation.slides):
            has_unsupported = any(
                _needs_subtree_fallback(el) for el in slide.elements
            )

            if not has_unsupported and not slide.is_fallback:
                continue

            if slide.is_fallback or fallback_mode == "slide":
                # Take screenshot of entire slide
                await _navigate_to_slide(page, slide_idx)
                img_path = await _screenshot_slide(page, slide_idx, output_dir)
                slide.is_fallback = True
                slide.fallback_image_path = str(img_path)
                # Remove individual elements since we're using slide-level fallback
                slide.elements = []
            else:
                # subtree mode: screenshot individual unsupported elements
                for el_idx, element in enumerate(slide.elements):
                    if _needs_subtree_fallback(element):
                        if _is_inline_svg_element(element):
                            img_path = _write_inline_svg_fallback(
                                slide_idx, el_idx, element, output_dir
                            )
                        else:
                            await _navigate_to_slide(page, slide_idx)
                            img_path = await _screenshot_element(
                                page, slide_idx, el_idx, element, output_dir
                            )
                        if element.unsupported_info is None:
                            tag_name = (
                                "mjx-container"
                                if element.element_type == ElementType.MATH
                                else ""
                            )
                            reason = (
                                "Math expression"
                                if element.element_type == ElementType.MATH
                                else "Unsupported element"
                            )
                            element.unsupported_info = UnsupportedInfo(
                                reason=reason,
                                tag_name=tag_name,
                            )
                        element.unsupported_info.fallback_image_path = str(img_path)

        await browser.close()

    return presentation


def render_fallbacks_sync(
    html_path: str | Path,
    presentation: Presentation,
    output_dir: str | Path,
    fallback_mode: str = "subtree",
) -> Presentation:
    """Synchronous wrapper for render_fallbacks."""
    from marpx.async_utils import run_coroutine_sync

    return run_coroutine_sync(
        render_fallbacks(html_path, presentation, output_dir, fallback_mode)
    )
