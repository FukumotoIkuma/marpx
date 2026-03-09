"""Shared fixtures and markers for marpx tests."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from marpx.extraction.js_bundle import ensure_extract_bundle


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "integration: requires Playwright and marp-cli")
    ensure_extract_bundle(dev=not bool(os.environ.get("CI")))


FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture()
def fixtures_dir() -> Path:
    """Return path to the test fixtures directory."""
    return FIXTURES_DIR


@pytest.fixture()
def simple_md(fixtures_dir: Path) -> Path:
    return fixtures_dir / "simple.md"


@pytest.fixture()
def nested_list_md(fixtures_dir: Path) -> Path:
    return fixtures_dir / "nested-list.md"


@pytest.fixture()
def table_md(fixtures_dir: Path) -> Path:
    return fixtures_dir / "table.md"


@pytest.fixture()
def complex_unsupported_md(fixtures_dir: Path) -> Path:
    return fixtures_dir / "complex-unsupported.md"


@pytest.fixture()
def rendered_layout_boxes_md(fixtures_dir: Path) -> Path:
    return fixtures_dir / "rendered-layout-boxes.md"


@pytest.fixture()
def rendered_layout_images_md(fixtures_dir: Path) -> Path:
    return fixtures_dir / "rendered-layout-images.md"


@pytest.fixture()
def quote_box_list_md(fixtures_dir: Path) -> Path:
    return fixtures_dir / "quote-box-list.md"


@pytest.fixture()
def decorated_raw_text_md(fixtures_dir: Path) -> Path:
    return fixtures_dir / "decorated-raw-text.md"


@pytest.fixture()
def multi_paragraph_md(fixtures_dir: Path) -> Path:
    return fixtures_dir / "multi-paragraph.md"


@pytest.fixture()
def tmp_output_dir(tmp_path: Path) -> Path:
    """Return a temporary directory for test outputs."""
    return tmp_path


@pytest.fixture(scope="session")
def session_output_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Return a shared temporary directory for cached rendered fixtures."""
    return tmp_path_factory.mktemp("session_outputs")
