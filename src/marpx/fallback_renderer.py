"""Render fallback images for unsupported content using Playwright screenshots."""
from __future__ import annotations

import asyncio
import logging
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


def _is_inline_svg_element(element: SlideElement) -> bool:
    """Return True when the unsupported element carries inline SVG markup."""
    info = element.unsupported_info
    return bool(
        element.element_type == ElementType.UNSUPPORTED
        and info
        and info.tag_name == "svg"
        and info.svg_markup
    )


def _write_inline_svg_fallback(
    slide_index: int,
    element_index: int,
    element: SlideElement,
    output_dir: Path,
) -> Path:
    """Rasterize inline SVG markup directly instead of screenshotting the page."""
    output_path = output_dir / f"slide_{slide_index}_el_{element_index}_fallback.png"
    svg_markup = (element.unsupported_info.svg_markup if element.unsupported_info else "") or ""
    output_path.write_bytes(rasterize_svg_to_png(svg_markup.encode("utf-8")))
    logger.info("Element fallback rasterized from inline SVG: %s", output_path)
    return output_path


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
            if el.element_type in (ElementType.UNSUPPORTED, ElementType.MATH):
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
        page = await browser.new_page(device_scale_factor=2)  # 2x DPI for crisp rendering
        await page.goto(file_url, wait_until="networkidle")
        await page.wait_for_selector("section", timeout=10000)

        for slide_idx, slide in enumerate(presentation.slides):
            has_unsupported = any(
                el.element_type in (ElementType.UNSUPPORTED, ElementType.MATH)
                for el in slide.elements
            )

            if not has_unsupported and not slide.is_fallback:
                continue

            if slide.is_fallback or fallback_mode == "slide":
                # Take screenshot of entire slide
                img_path = await _screenshot_slide(page, slide_idx, output_dir)
                slide.is_fallback = True
                slide.fallback_image_path = str(img_path)
                # Remove individual elements since we're using slide-level fallback
                slide.elements = []
            else:
                # subtree mode: screenshot individual unsupported elements
                for el_idx, element in enumerate(slide.elements):
                    if element.element_type in (ElementType.UNSUPPORTED, ElementType.MATH):
                        if _is_inline_svg_element(element):
                            img_path = _write_inline_svg_fallback(
                                slide_idx, el_idx, element, output_dir
                            )
                        else:
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
    return asyncio.run(render_fallbacks(html_path, presentation, output_dir, fallback_mode))
