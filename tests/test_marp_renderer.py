"""Tests for marpx.marp_renderer module.

All tests require marp-cli and Node.js, so they are marked as integration tests.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from marpx.marp_renderer import (
    MarpRenderError,
    _inject_base_href,
    render_to_html,
)


class TestInjectBaseHref:
    """Unit tests for post-processing rendered HTML."""

    def test_inserts_base_tag_into_existing_head(self, tmp_path: Path) -> None:
        markdown_path = tmp_path / "deck.md"
        html = "<html><head><title>x</title></head><body></body></html>"

        result = _inject_base_href(html, markdown_path)

        assert '<base href="' in result
        assert f"{tmp_path.as_uri()}/" in result

    def test_replaces_existing_base_tag(self, tmp_path: Path) -> None:
        markdown_path = tmp_path / "deck.md"
        html = (
            '<html><head><base href="file:///wrong/">'
            "<title>x</title></head><body></body></html>"
        )

        result = _inject_base_href(html, markdown_path)

        assert result.count("<base ") == 1
        assert "file:///wrong/" not in result
        assert f"{tmp_path.as_uri()}/" in result


@pytest.mark.integration
class TestRenderToHtml:
    """Integration tests for Marp HTML rendering."""

    def test_simple_md_produces_html(
        self, simple_md: Path, tmp_output_dir: Path
    ) -> None:
        html_path = render_to_html(simple_md, output_dir=tmp_output_dir)
        assert html_path.exists()
        assert html_path.suffix == ".html"
        assert html_path.stat().st_size > 0

    def test_html_contains_section_tags(
        self, simple_md: Path, tmp_output_dir: Path
    ) -> None:
        html_path = render_to_html(simple_md, output_dir=tmp_output_dir)
        content = html_path.read_text(encoding="utf-8")
        assert "<section" in content

    def test_nonexistent_file_raises(self, tmp_output_dir: Path) -> None:
        with pytest.raises(MarpRenderError, match="not found"):
            render_to_html("/nonexistent/path/no.md", output_dir=tmp_output_dir)

    def test_table_md_produces_html(self, table_md: Path, tmp_output_dir: Path) -> None:
        html_path = render_to_html(table_md, output_dir=tmp_output_dir)
        assert html_path.exists()
        content = html_path.read_text(encoding="utf-8")
        assert "<table" in content

    def test_relative_image_gets_markdown_base_href(
        self, tmp_output_dir: Path, tmp_path: Path
    ) -> None:
        image_dir = tmp_path / "images"
        image_dir.mkdir()
        (image_dir / "chart-states.png").write_bytes(
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0"
            b"\x00\x00\x03\x01\x01\x00\xc9\xfe\x92\xef\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        markdown_path = tmp_path / "deck.md"
        markdown_path.write_text(
            "# Slide\n\n![w:1000](./images/chart-states.png)\n",
            encoding="utf-8",
        )

        html_path = render_to_html(markdown_path, output_dir=tmp_output_dir)
        content = html_path.read_text(encoding="utf-8")

        assert '<img src="./images/chart-states.png"' in content
        assert f'<base href="{tmp_path.as_uri()}/">' in content
