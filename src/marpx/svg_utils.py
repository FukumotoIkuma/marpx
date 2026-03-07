"""Shared SVG rasterization helpers."""
from __future__ import annotations

import base64
import shutil
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path


class MissingDependencyError(RuntimeError):
    """Raised when an external tool required for rendering is unavailable."""


RSVG_INSTALL_HINT = (
    "Install it with `brew install librsvg` on macOS or "
    "`sudo apt-get install librsvg2-bin` on Debian/Ubuntu."
)


def _load_svg_bytes(src: str) -> tuple[list[str], bytes | None]:
    """Resolve an SVG source into an rsvg-convert command and optional stdin bytes."""
    cmd: list[str] = []
    svg_bytes: bytes | None = None

    if src.startswith("data:image/svg+xml"):
        header, data = src.split(",", 1)
        if ";base64" in header:
            svg_bytes = base64.b64decode(data)
        else:
            svg_bytes = urllib.parse.unquote_to_bytes(data)
    elif src.startswith("file://"):
        svg_path = Path(urllib.parse.unquote(urllib.parse.urlparse(src).path))
        cmd.append(str(svg_path))
    elif src.startswith(("http://", "https://")):
        req = urllib.request.Request(
            src,
            headers={"User-Agent": "marpx/0.1"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            svg_bytes = resp.read()
    else:
        cmd.append(str(Path(src)))

    return cmd, svg_bytes


def rasterize_svg_to_png(src: str | bytes) -> bytes:
    """Rasterize SVG bytes or a source path/URL into PNG bytes using rsvg-convert."""
    rsvg_convert = shutil.which("rsvg-convert")
    if rsvg_convert is None:
        raise MissingDependencyError(
            "SVG images require `rsvg-convert`, but it was not found in PATH. "
            f"{RSVG_INSTALL_HINT}"
        )

    cmd = [rsvg_convert, "--format", "png"]
    svg_bytes: bytes | None

    if isinstance(src, bytes):
        svg_bytes = src
    else:
        extra_args, svg_bytes = _load_svg_bytes(src)
        cmd.extend(extra_args)

    result = subprocess.run(
        cmd,
        input=svg_bytes,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        stderr = result.stderr.decode("utf-8", errors="replace").strip()
        raise MissingDependencyError(
            f"`rsvg-convert` failed while rasterizing SVG: {stderr}. "
            f"If the tool is missing or broken, {RSVG_INSTALL_HINT}"
        )
    return result.stdout
