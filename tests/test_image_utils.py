"""Tests for marpx.image_utils."""
from __future__ import annotations

import base64
from pathlib import Path

from marpx.image_utils import resolve_image_bytes


def _tiny_png_bytes() -> bytes:
    return base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4"
        "nGP4z8BQDwAEgAF/pooBPQAAAABJRU5ErkJggg=="
    )


def test_resolve_image_bytes_prefers_image_data(tmp_path: Path) -> None:
    image_path = tmp_path / "sample.png"
    image_path.write_bytes(b"file-bytes")

    assert resolve_image_bytes(str(image_path), b"inline-bytes") == b"inline-bytes"


def test_resolve_image_bytes_from_data_uri() -> None:
    data = _tiny_png_bytes()
    encoded = base64.b64encode(data).decode("ascii")

    assert resolve_image_bytes(f"data:image/png;base64,{encoded}") == data


def test_resolve_image_bytes_from_local_path(tmp_path: Path) -> None:
    image_path = tmp_path / "sample.png"
    payload = _tiny_png_bytes()
    image_path.write_bytes(payload)

    assert resolve_image_bytes(str(image_path)) == payload


def test_resolve_image_bytes_from_file_url(tmp_path: Path) -> None:
    image_path = tmp_path / "sample file.png"
    payload = _tiny_png_bytes()
    image_path.write_bytes(payload)

    assert resolve_image_bytes(image_path.as_uri()) == payload


def test_resolve_image_bytes_missing_path_returns_none(tmp_path: Path) -> None:
    missing = tmp_path / "missing.png"

    assert resolve_image_bytes(str(missing)) is None
