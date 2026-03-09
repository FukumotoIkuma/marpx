"""Tests for marpx.js_bundle helpers."""

from __future__ import annotations

import os
import time
from pathlib import Path

from marpx.extraction.js_bundle import _bundle_needs_rebuild


def test_bundle_needs_rebuild_when_bundle_missing(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "extract_slides_js"
    bundle_dir.mkdir()
    (bundle_dir / "main.js").write_text("export {};\n", encoding="utf-8")

    assert _bundle_needs_rebuild(tmp_path / "missing.bundle.js", bundle_dir) is True


def test_bundle_needs_rebuild_when_source_is_newer(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "extract_slides_js"
    bundle_dir.mkdir()
    source = bundle_dir / "main.js"
    bundle = tmp_path / "extract_slides.bundle.js"
    source.write_text("export {};\n", encoding="utf-8")
    bundle.write_text("() => {};\n", encoding="utf-8")

    stale_time = time.time() - 10
    os.utime(bundle, (stale_time, stale_time))
    os.utime(source, None)

    assert _bundle_needs_rebuild(bundle, bundle_dir) is True


def test_bundle_does_not_need_rebuild_when_bundle_is_newer(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "extract_slides_js"
    bundle_dir.mkdir()
    source = bundle_dir / "main.js"
    bundle = tmp_path / "extract_slides.bundle.js"
    source.write_text("export {};\n", encoding="utf-8")
    bundle.write_text("() => {};\n", encoding="utf-8")

    stale_time = time.time() - 10
    os.utime(source, (stale_time, stale_time))
    os.utime(bundle, None)

    assert _bundle_needs_rebuild(bundle, bundle_dir) is False
