"""Utilities for loading image bytes from various source types."""

from __future__ import annotations

import base64
import logging
import urllib.parse
import urllib.request
from pathlib import Path

logger = logging.getLogger(__name__)

_USER_AGENT = "marpx/0.2"


def resolve_image_bytes(src: str, image_data: bytes | None = None) -> bytes | None:
    """Load image bytes from a pre-supplied buffer, data URI, file URL, HTTP URL, or local path.

    Args:
        src: Image source string (data URI, file://, http/https URL, or local path).
        image_data: Pre-loaded bytes that take priority over ``src`` when provided.

    Returns:
        Raw image bytes, or ``None`` when the source cannot be resolved.
    """
    if image_data:
        return image_data

    if not src:
        return None

    if src.startswith("data:"):
        _header, data = src.split(",", 1)
        return base64.b64decode(data)

    if src.startswith("file://"):
        path = Path(urllib.parse.unquote(urllib.parse.urlparse(src).path))
        try:
            with open(path, "rb") as f:
                return f.read()
        except OSError as exc:
            logger.warning("Cannot read file %s: %s", path, exc)
            return None

    if src.startswith(("http://", "https://")):
        req = urllib.request.Request(src, headers={"User-Agent": _USER_AGENT})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read()

    # Local path
    path = Path(src)
    if path.exists():
        with open(path, "rb") as f:
            return f.read()

    return None
