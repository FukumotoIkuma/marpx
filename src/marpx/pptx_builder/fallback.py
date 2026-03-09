"""Fallback image placement for pptx_builder."""

from __future__ import annotations

import logging
from pathlib import Path

from pptx.util import Emu

from marpx.models import SlideElement
from marpx.utils.common import px_to_emu

logger = logging.getLogger(__name__)


def _add_fallback_image(
    slide,
    element: SlideElement,
    fallback_image_path: str | None = None,
) -> None:
    """Add a fallback image for unsupported content."""
    if not fallback_image_path:
        return

    left = Emu(px_to_emu(element.box.x))
    top = Emu(px_to_emu(element.box.y))
    width = Emu(px_to_emu(element.box.width))
    height = Emu(px_to_emu(element.box.height))

    image_path = Path(fallback_image_path)
    if image_path.exists():
        slide.shapes.add_picture(str(image_path), left, top, width, height)
    else:
        logger.warning(
            "Fallback image not found: %s",
            fallback_image_path,
        )
