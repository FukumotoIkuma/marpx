"""Orchestrate Marp Markdown to PPTX conversion pipeline."""

from __future__ import annotations

import logging
import shutil
import tempfile
from pathlib import Path

from marpx.capabilities import Capability, classify_slide, should_fallback_slide
from marpx.marp_renderer import render_to_html
from marpx.extractor import close_sync_browser, extract_presentation_sync
from marpx.fallback_renderer import render_fallbacks_sync
from marpx.pptx_builder.builder import build_pptx

logger = logging.getLogger(__name__)


class ConversionError(Exception):
    """Raised when the conversion pipeline fails."""


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

    try:
        # Step 1: Render Markdown to HTML
        logger.info("Step 1: Rendering Markdown to HTML...")
        html_path = render_to_html(
            markdown_path,
            output_dir=temp_dir,
            theme=theme,
        )
        logger.info("HTML generated: %s", html_path)

        # Step 2: Extract presentation data from HTML
        logger.info("Step 2: Extracting slide data with Playwright...")
        presentation = extract_presentation_sync(html_path)
        logger.info(
            "Extracted %d slides, default size: %.0fx%.0f",
            len(presentation.slides),
            presentation.default_width_px,
            presentation.default_height_px,
        )
        # Fallback rendering uses asyncio + async Playwright; close the shared
        # sync extractor browser first to avoid event-loop conflicts.
        close_sync_browser()

        # Step 2.5: Classify element capabilities
        for slide in presentation.slides:
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
            if should_fallback_slide(slide):
                logger.info(
                    "Slide %d: marked for full-slide fallback",
                    slide.slide_number,
                )
                if not prefer_editable:
                    slide.is_fallback = True

        # Step 3: Render fallback images for unsupported content
        logger.info("Step 3: Rendering fallback images...")
        fallback_dir = temp_dir / "fallbacks"
        presentation = render_fallbacks_sync(
            html_path, presentation, fallback_dir, fallback_mode
        )

        # Step 4: Build PPTX
        logger.info("Step 4: Building PPTX...")
        result = build_pptx(presentation, output_path)
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
