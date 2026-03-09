"""Helpers for managing browser-side JS bundles in development."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

_JS_DIR = Path(__file__).parent
_EXTRACT_BUNDLE_DIR = _JS_DIR / "js"
_EXTRACT_BUNDLE_FILE = _JS_DIR / "extract_slides.bundle.js"


def _bundle_sources(bundle_dir: Path) -> list[Path]:
    """Return source files that should trigger a rebuild when changed."""
    return sorted(
        path
        for path in bundle_dir.iterdir()
        if path.is_file() and path.name != "node_modules"
    )


def _bundle_needs_rebuild(bundle_file: Path, bundle_dir: Path) -> bool:
    """Return True when the built bundle is missing or older than its sources."""
    if not bundle_file.exists():
        return True
    bundle_mtime = bundle_file.stat().st_mtime
    return any(
        src.stat().st_mtime > bundle_mtime for src in _bundle_sources(bundle_dir)
    )


def _run_dev_bundle_build(bundle_dir: Path) -> None:
    """Install dev deps if needed and rebuild the bundle."""
    if shutil.which("node") is None:
        raise RuntimeError("Node.js is required to rebuild extract_slides.bundle.js")
    if shutil.which("npm") is None:
        raise RuntimeError("npm is required to rebuild extract_slides.bundle.js")

    node_modules = bundle_dir / "node_modules"
    if not node_modules.exists():
        subprocess.run(
            ["npm", "ci", "--no-audit", "--no-fund"],
            cwd=str(bundle_dir),
            capture_output=True,
            text=True,
            check=True,
        )

    subprocess.run(
        ["npm", "run", "build"],
        cwd=str(bundle_dir),
        capture_output=True,
        text=True,
        check=True,
    )


def ensure_extract_bundle(*, dev: bool = False) -> None:
    """Ensure the extract-slides bundle exists and optionally rebuild in dev."""
    if not _EXTRACT_BUNDLE_DIR.exists():
        raise FileNotFoundError(f"Missing JS source directory: {_EXTRACT_BUNDLE_DIR}")

    if dev and _bundle_needs_rebuild(_EXTRACT_BUNDLE_FILE, _EXTRACT_BUNDLE_DIR):
        _run_dev_bundle_build(_EXTRACT_BUNDLE_DIR)

    if not _EXTRACT_BUNDLE_FILE.exists():
        raise FileNotFoundError(f"Missing JS bundle: {_EXTRACT_BUNDLE_FILE}")


def load_extract_bundle() -> str:
    """Load the current extract-slides bundle contents."""
    ensure_extract_bundle(dev=False)
    return _EXTRACT_BUNDLE_FILE.read_text(encoding="utf-8")
