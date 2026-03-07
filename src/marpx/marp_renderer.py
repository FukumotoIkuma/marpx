"""Render Marp Markdown to HTML using marp-cli."""

from __future__ import annotations

import logging
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

# Pin marp-cli version for reproducibility
MARP_CLI_PACKAGE = "@marp-team/marp-cli@4.2.3"


class MarpRenderError(Exception):
    """Raised when marp-cli fails to render."""


def find_npx() -> str:
    """Find npx executable."""
    npx = shutil.which("npx")
    if npx is None:
        raise MarpRenderError("npx not found. Please install Node.js (>=18) and npm.")
    return npx


def _document_base_href(markdown_path: Path) -> str:
    """Return a file:// base URL that resolves relative assets from the Markdown dir."""
    return f"{markdown_path.parent.resolve().as_uri().rstrip('/')}/"


def _inject_base_href(html: str, markdown_path: Path) -> str:
    """Insert or replace a <base> tag so relative asset URLs resolve from the source .md."""
    base_tag = f'<base href="{_document_base_href(markdown_path)}">'

    if re.search(r"<base\b", html, flags=re.IGNORECASE):
        return re.sub(
            r"<base\b[^>]*>",
            base_tag,
            html,
            count=1,
            flags=re.IGNORECASE,
        )

    if re.search(r"</head>", html, flags=re.IGNORECASE):
        return re.sub(
            r"</head>",
            f"  {base_tag}\n</head>",
            html,
            count=1,
            flags=re.IGNORECASE,
        )

    if re.search(r"<html\b[^>]*>", html, flags=re.IGNORECASE):
        return re.sub(
            r"<html\b[^>]*>",
            lambda match: f"{match.group(0)}\n<head>\n  {base_tag}\n</head>",
            html,
            count=1,
            flags=re.IGNORECASE,
        )

    return f"<head>\n  {base_tag}\n</head>\n{html}"


def render_to_html(
    markdown_path: str | Path,
    output_dir: str | Path | None = None,
    theme: str | None = None,
    keep_temp: bool = False,
) -> Path:
    """Convert Marp Markdown to HTML.

    Args:
        markdown_path: Path to the .md file.
        output_dir: Directory for output. If None, uses a temp directory.
        theme: Optional Marp theme name or CSS path.
        keep_temp: If True, don't clean up temp directory.

    Returns:
        Path to the generated HTML file.

    Raises:
        MarpRenderError: If rendering fails.
    """
    markdown_path = Path(markdown_path).resolve()
    if not markdown_path.exists():
        raise MarpRenderError(f"Markdown file not found: {markdown_path}")

    # Determine output directory
    if output_dir is None:
        output_dir = Path(tempfile.mkdtemp(prefix="marpx_"))
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    html_path = output_dir / f"{markdown_path.stem}.html"

    npx = find_npx()
    cmd = [
        npx,
        MARP_CLI_PACKAGE,
        str(markdown_path),
        "--html",
        "--output",
        str(html_path),
    ]

    if theme:
        cmd.extend(["--theme", theme])

    logger.info("Running marp-cli: %s", " ".join(cmd))

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        raise MarpRenderError("marp-cli timed out after 60 seconds")
    except FileNotFoundError:
        raise MarpRenderError(f"Failed to execute: {npx}")

    if result.returncode != 0:
        stderr = result.stderr.strip()
        raise MarpRenderError(f"marp-cli failed (exit {result.returncode}): {stderr}")

    if not html_path.exists():
        raise MarpRenderError(f"marp-cli did not produce expected output: {html_path}")

    html_content = html_path.read_text(encoding="utf-8")
    html_path.write_text(
        _inject_base_href(html_content, markdown_path),
        encoding="utf-8",
    )

    logger.info("HTML generated: %s", html_path)
    return html_path
