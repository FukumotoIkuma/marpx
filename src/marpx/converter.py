"""Orchestrate Marp Markdown to PPTX conversion pipeline."""

from __future__ import annotations

import logging
import shutil
import tempfile
from pathlib import Path

from marpx.capabilities import (
    Capability,
    classify_element,
    classify_slide,
    should_fallback_slide,
)
from marpx.marp_renderer import render_to_html
from marpx.extractor import SyncBrowserManager, extract_presentation_sync
from marpx.fallback_renderer import render_fallbacks_sync
from marpx.pipeline import ElementRenderInfo, PipelineContext, SlideRenderInfo
from marpx.pptx_builder.builder import build_pptx
from marpx.models import Presentation

logger = logging.getLogger(__name__)


class ConversionError(Exception):
    """Raised when the conversion pipeline fails."""


def _classify_presentation(
    presentation: Presentation,
    *,
    prefer_editable: bool = False,
) -> dict[int, SlideRenderInfo]:
    """Classify all elements in the presentation and return render info.

    This is a pure function that does NOT mutate the presentation model.
    It returns a mapping of slide index to SlideRenderInfo containing
    capability decisions for each element.

    Args:
        presentation: Extracted presentation data.
        prefer_editable: If True, skip full-slide fallback even when
            the heuristic recommends it.

    Returns:
        Mapping of slide index to SlideRenderInfo.
    """
    slide_render_info: dict[int, SlideRenderInfo] = {}

    for slide_idx, slide in enumerate(presentation.slides):
        decisions = classify_slide(slide)
        native_count = sum(
            1 for d in decisions.values() if d.capability == Capability.NATIVE
        )
        fallback_count = len(decisions) - native_count
        logger.info(
            "Slide %d: %d native, %d fallback elements",
            slide.slide_number,
            native_count,
            fallback_count,
        )

        element_info: dict[int, ElementRenderInfo] = {}
        for i, element in enumerate(slide.elements):
            decision = decisions.get(i) or classify_element(element)
            element_info[i] = ElementRenderInfo(
                capability=decision.capability.value,
                reason=decision.reason,
            )
            if decision.reason:
                logger.debug(
                    "Slide %d, element %d (%s): %s — %s",
                    slide.slide_number,
                    i,
                    element.element_type.value,
                    decision.capability.value,
                    decision.reason,
                )

        slide_info = SlideRenderInfo(element_render_info=element_info)

        if should_fallback_slide(slide):
            logger.info(
                "Slide %d: marked for full-slide fallback",
                slide.slide_number,
            )
            if not prefer_editable:
                slide_info.is_fallback = True

        slide_render_info[slide_idx] = slide_info

    return slide_render_info


def _apply_render_info_to_models(
    presentation: Presentation,
    slide_render_info: dict[int, SlideRenderInfo],
) -> None:
    """Write render info back to models for backward compatibility.

    Downstream components (builder, fallback_renderer) currently read
    ``element.capability`` and ``slide.is_fallback`` from the models.
    This bridge function keeps them working while we migrate to
    PipelineContext-based data flow.
    """
    for slide_idx, slide in enumerate(presentation.slides):
        slide_info = slide_render_info.get(slide_idx)
        if slide_info is None:
            continue

        if slide_info.is_fallback:
            slide.is_fallback = True

        for el_idx, element in enumerate(slide.elements):
            el_info = slide_info.element_render_info.get(el_idx)
            if el_info is not None:
                element.capability = el_info.capability


def convert(
    markdown_path: str | Path,
    output_path: str | Path,
    theme: str | None = None,
    fallback_mode: str = "subtree",
    prefer_editable: bool = False,
    keep_temp: bool = False,
    verbose: bool = False,
) -> Path:
    """Convert Marp Markdown to editable PPTX.

    Args:
        markdown_path: Path to the .md file.
        output_path: Path for the output .pptx file.
        theme: Optional Marp theme name or CSS path.
        fallback_mode: "subtree" or "slide" fallback for unsupported content.
        prefer_editable: If True, maximize editable shapes even for complex content.
        keep_temp: If True, don't delete temporary files.
        verbose: If True, enable detailed logging.

    Returns:
        Path to the generated PPTX file.
    """
    if verbose:
        logging.basicConfig(level=logging.DEBUG)

    markdown_path = Path(markdown_path).resolve()
    output_path = Path(output_path).resolve()

    if not markdown_path.exists():
        raise ConversionError(f"Input file not found: {markdown_path}")
    if fallback_mode not in {"subtree", "slide"}:
        raise ConversionError(
            f"Invalid fallback mode: {fallback_mode}. Use 'subtree' or 'slide'."
        )

    # Create temp directory for intermediate files
    temp_dir = Path(tempfile.mkdtemp(prefix="marpx_"))

    # Initialise pipeline context
    ctx = PipelineContext(
        markdown_path=markdown_path,
        output_path=output_path,
        temp_dir=temp_dir,
    )

    try:
        # Step 1: Render Markdown to HTML
        logger.info("Step 1: Rendering Markdown to HTML...")
        html_path = render_to_html(
            markdown_path,
            output_dir=temp_dir,
            theme=theme,
        )
        ctx.html_path = html_path
        logger.info("HTML generated: %s", html_path)

        # Step 2: Extract presentation data from HTML
        # Use SyncBrowserManager so the browser is closed automatically
        # before the fallback renderer starts its own async Playwright.
        logger.info("Step 2: Extracting slide data with Playwright...")
        with SyncBrowserManager() as browser:
            presentation = extract_presentation_sync(html_path, _browser=browser)
        ctx.presentation = presentation
        logger.info(
            "Extracted %d slides, default size: %.0fx%.0f",
            len(presentation.slides),
            presentation.default_width_px,
            presentation.default_height_px,
        )

        # Step 2.5: Classify element capabilities
        ctx.slide_render_info = _classify_presentation(
            presentation, prefer_editable=prefer_editable
        )

        # Write classifications back to models for backward compatibility
        _apply_render_info_to_models(presentation, ctx.slide_render_info)

        # Step 3: Render fallback images for unsupported content
        logger.info("Step 3: Rendering fallback images...")
        fallback_dir = temp_dir / "fallbacks"
        presentation = render_fallbacks_sync(
            html_path,
            presentation,
            fallback_dir,
            fallback_mode,
            slide_render_info=ctx.slide_render_info,
        )

        # Step 4: Build PPTX
        logger.info("Step 4: Building PPTX...")
        result = build_pptx(
            presentation,
            output_path,
            slide_render_info=ctx.slide_render_info,
        )
        logger.info("PPTX generated: %s", result)

        return result

    except ConversionError:
        raise
    except Exception as e:
        raise ConversionError(f"Conversion failed: {e}") from e
    finally:
        if not keep_temp:
            shutil.rmtree(temp_dir, ignore_errors=True)
            logger.debug("Cleaned up temp dir: %s", temp_dir)
        else:
            logger.info("Temp files kept at: %s", temp_dir)
