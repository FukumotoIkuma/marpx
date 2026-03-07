"""Tests for marpx.extractor module.

All tests require Playwright, so they are marked as integration tests.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from marpx.extractor import extract_presentation_sync
from marpx.marp_renderer import render_to_html
from marpx.models import ElementType


@pytest.fixture()
def simple_html(simple_md: Path, tmp_output_dir: Path) -> Path:
    """Render simple.md to HTML for extraction tests."""
    return render_to_html(simple_md, output_dir=tmp_output_dir)


@pytest.fixture()
def nested_list_html(nested_list_md: Path, tmp_output_dir: Path) -> Path:
    """Render nested-list.md to HTML."""
    return render_to_html(nested_list_md, output_dir=tmp_output_dir)


@pytest.fixture()
def table_html(table_md: Path, tmp_output_dir: Path) -> Path:
    """Render table.md to HTML."""
    return render_to_html(table_md, output_dir=tmp_output_dir)


@pytest.fixture()
def complex_html(complex_unsupported_md: Path, tmp_output_dir: Path) -> Path:
    """Render complex-unsupported.md to HTML."""
    return render_to_html(complex_unsupported_md, output_dir=tmp_output_dir)


@pytest.fixture()
def rendered_layout_boxes_html(
    rendered_layout_boxes_md: Path, tmp_output_dir: Path
) -> Path:
    """Render rendered-layout-boxes.md to HTML."""
    return render_to_html(rendered_layout_boxes_md, output_dir=tmp_output_dir)


@pytest.fixture()
def rendered_layout_images_html(
    rendered_layout_images_md: Path, tmp_output_dir: Path
) -> Path:
    """Render rendered-layout-images.md to HTML."""
    return render_to_html(rendered_layout_images_md, output_dir=tmp_output_dir)


@pytest.fixture()
def quote_box_list_html(quote_box_list_md: Path, tmp_output_dir: Path) -> Path:
    """Render quote-box-list.md to HTML."""
    return render_to_html(quote_box_list_md, output_dir=tmp_output_dir)


@pytest.fixture()
def decorated_raw_text_html(decorated_raw_text_md: Path, tmp_output_dir: Path) -> Path:
    """Render decorated-raw-text.md to HTML."""
    return render_to_html(decorated_raw_text_md, output_dir=tmp_output_dir)


@pytest.fixture()
def multi_paragraph_html(multi_paragraph_md: Path, tmp_output_dir: Path) -> Path:
    """Render multi-paragraph.md to HTML."""
    return render_to_html(multi_paragraph_md, output_dir=tmp_output_dir)


@pytest.mark.integration
class TestExtractSimple:
    """Tests for extracting simple.md presentation."""

    def test_slide_count(self, simple_html: Path) -> None:
        pres = extract_presentation_sync(simple_html)
        assert len(pres.slides) == 2

    def test_slide_dimensions(self, simple_html: Path) -> None:
        pres = extract_presentation_sync(simple_html)
        slide = pres.slides[0]
        # Marp default is 1280x720
        assert slide.width_px == pytest.approx(1280, abs=10)
        assert slide.height_px == pytest.approx(720, abs=10)

    def test_first_slide_has_heading(self, simple_html: Path) -> None:
        pres = extract_presentation_sync(simple_html)
        slide = pres.slides[0]
        heading_elements = [
            e for e in slide.elements if e.element_type == ElementType.HEADING
        ]
        assert len(heading_elements) >= 1
        # The heading should contain "Hello World"
        heading = heading_elements[0]
        text = "".join(r.text for p in heading.paragraphs for r in p.runs)
        assert "Hello World" in text

    def test_first_slide_has_paragraph(self, simple_html: Path) -> None:
        pres = extract_presentation_sync(simple_html)
        slide = pres.slides[0]
        para_elements = [
            e for e in slide.elements if e.element_type == ElementType.PARAGRAPH
        ]
        assert len(para_elements) >= 1

    def test_first_slide_has_list(self, simple_html: Path) -> None:
        pres = extract_presentation_sync(simple_html)
        slide = pres.slides[0]
        list_elements = [
            e for e in slide.elements if e.element_type == ElementType.UNORDERED_LIST
        ]
        assert len(list_elements) >= 1
        # Should have 3 bullet items
        assert len(list_elements[0].list_items) == 3


@pytest.mark.integration
class TestExtractNestedList:
    """Tests for extracting nested list presentation."""

    def test_nested_levels(self, nested_list_html: Path) -> None:
        pres = extract_presentation_sync(nested_list_html)
        slide = pres.slides[0]
        list_elements = [
            e for e in slide.elements if e.element_type == ElementType.UNORDERED_LIST
        ]
        assert len(list_elements) >= 1

        items = list_elements[0].list_items
        # Should have items at multiple levels
        levels = {item.level for item in items}
        assert len(levels) >= 2  # At least level 0 and 1

    def test_level_0_items(self, nested_list_html: Path) -> None:
        pres = extract_presentation_sync(nested_list_html)
        slide = pres.slides[0]
        list_elements = [
            e for e in slide.elements if e.element_type == ElementType.UNORDERED_LIST
        ]
        items = list_elements[0].list_items
        level_0 = [i for i in items if i.level == 0]
        assert len(level_0) == 2  # "Level 1 item A" and "Level 1 item B"

    def test_unordered_nested_list_preserves_marker_styles(
        self, nested_list_html: Path
    ) -> None:
        pres = extract_presentation_sync(nested_list_html)
        slide = pres.slides[0]
        list_element = next(
            e for e in slide.elements if e.element_type == ElementType.UNORDERED_LIST
        )

        assert list_element.list_items[0].list_style_type == "disc"
        assert any(item.list_style_type == "circle" for item in list_element.list_items)
        assert any(item.list_style_type == "square" for item in list_element.list_items)

    def test_ordered_nested_list_preserves_numbering_style_and_spacing(
        self, nested_list_html: Path
    ) -> None:
        pres = extract_presentation_sync(nested_list_html)
        slide = pres.slides[1]
        list_element = next(
            e for e in slide.elements if e.element_type == ElementType.ORDERED_LIST
        )

        assert list_element.list_items[0].list_style_type == "decimal"
        assert any(
            item.level == 1 and item.list_style_type == "lower-roman"
            for item in list_element.list_items
        )
        assert all(
            item.line_height_px and item.line_height_px > 0
            for item in list_element.list_items
        )
        assert any(item.space_before_px > 0 for item in list_element.list_items[1:])

    def test_inline_emphasis_in_list_item_preserves_surrounding_spaces(
        self, tmp_path: Path, tmp_output_dir: Path
    ) -> None:
        md_path = tmp_path / "list-inline-emphasis.md"
        md_path.write_text(
            "- First bullet\n- Second bullet with **emphasis** and trailing text\n",
            encoding="utf-8",
        )

        html_path = render_to_html(md_path, output_dir=tmp_output_dir)
        pres = extract_presentation_sync(html_path)
        slide = pres.slides[0]
        list_element = next(
            e for e in slide.elements if e.element_type == ElementType.UNORDERED_LIST
        )

        second_item = list_element.list_items[1]
        assert [run.text for run in second_item.runs] == [
            "Second bullet with ",
            "emphasis",
            " and trailing text",
        ]


@pytest.mark.integration
class TestExtractTable:
    """Tests for extracting table presentation."""

    def test_table_element_exists(self, table_html: Path) -> None:
        pres = extract_presentation_sync(table_html)
        slide = pres.slides[0]
        table_elements = [
            e for e in slide.elements if e.element_type == ElementType.TABLE
        ]
        assert len(table_elements) >= 1

    def test_table_row_count(self, table_html: Path) -> None:
        pres = extract_presentation_sync(table_html)
        slide = pres.slides[0]
        table_elements = [
            e for e in slide.elements if e.element_type == ElementType.TABLE
        ]
        table = table_elements[0]
        # 1 header + 3 data rows = 4 rows
        assert len(table.table_rows) == 4

    def test_table_cell_count(self, table_html: Path) -> None:
        pres = extract_presentation_sync(table_html)
        slide = pres.slides[0]
        table_elements = [
            e for e in slide.elements if e.element_type == ElementType.TABLE
        ]
        table = table_elements[0]
        # Each row should have 3 columns
        for row in table.table_rows:
            assert len(row.cells) == 3


@pytest.mark.integration
class TestExtractComplex:
    """Tests for extracting complex-unsupported.md."""

    def test_has_unsupported_elements(self, complex_html: Path) -> None:
        pres = extract_presentation_sync(complex_html)
        # Check across all slides for unsupported elements (SVG)
        unsupported = []
        for slide in pres.slides:
            unsupported.extend(
                e for e in slide.elements if e.element_type == ElementType.UNSUPPORTED
            )
        assert len(unsupported) >= 1

    def test_slide_count(self, complex_html: Path) -> None:
        pres = extract_presentation_sync(complex_html)
        assert len(pres.slides) == 3

    def test_inline_svg_unsupported_preserves_markup(self, complex_html: Path) -> None:
        pres = extract_presentation_sync(complex_html)
        slide = pres.slides[2]
        svg = next(
            e
            for e in slide.elements
            if e.element_type == ElementType.UNSUPPORTED
            and e.unsupported_info
            and e.unsupported_info.tag_name == "svg"
        )
        assert svg.unsupported_info is not None
        assert svg.unsupported_info.svg_markup is not None
        assert "<svg" in svg.unsupported_info.svg_markup
        assert "<circle" in svg.unsupported_info.svg_markup


@pytest.mark.integration
class TestRenderedLayoutCapture:
    """Tests for generic rendered-layout extraction."""

    def test_extracts_decorated_blocks(self, rendered_layout_boxes_html: Path) -> None:
        pres = extract_presentation_sync(rendered_layout_boxes_html)
        slide = pres.slides[0]
        decorated = [
            e for e in slide.elements if e.element_type == ElementType.DECORATED_BLOCK
        ]
        assert len(decorated) >= 3
        assert any(
            e.decoration and e.decoration.border_left.width_px > 0 for e in decorated
        )
        assert any(
            e.decoration and e.decoration.background_color is not None
            for e in decorated
        )
        quote_block = next(
            e for e in decorated if any(p.list_level == 0 for p in e.paragraphs)
        )
        assert any(p.list_level == 0 for p in quote_block.paragraphs)
        assert len(quote_block.paragraphs) >= 4

    def test_checklist_pseudo_content_is_preserved(
        self, rendered_layout_boxes_html: Path
    ) -> None:
        pres = extract_presentation_sync(rendered_layout_boxes_html)
        slide = pres.slides[0]
        lists = [
            e for e in slide.elements if e.element_type == ElementType.UNORDERED_LIST
        ]
        assert lists
        first_item_text = "".join(run.text for run in lists[0].list_items[0].runs)
        assert "☐ " in first_item_text

    def test_extracts_object_fit_metadata(
        self, rendered_layout_images_html: Path
    ) -> None:
        pres = extract_presentation_sync(rendered_layout_images_html)
        slide = pres.slides[0]
        images = [e for e in slide.elements if e.element_type == ElementType.IMAGE]
        assert len(images) == 2
        assert all(img.object_fit == "contain" for img in images)
        assert all(img.image_natural_width_px == 1 for img in images)
        assert all(img.image_natural_height_px == 1 for img in images)

    def test_quote_box_with_markdown_list_stays_decorated(
        self, quote_box_list_html: Path
    ) -> None:
        pres = extract_presentation_sync(quote_box_list_html)
        slide = pres.slides[0]
        decorated = [
            e for e in slide.elements if e.element_type == ElementType.DECORATED_BLOCK
        ]
        assert len(decorated) == 1
        quote_block = decorated[0]
        assert quote_block.decoration is not None
        assert quote_block.decoration.border_left.width_px > 0
        assert [p.list_level for p in quote_block.paragraphs] == [None, 0, 0, 0]
        assert "".join(run.text for run in quote_block.paragraphs[0].runs).startswith(
            "This highlighted note is only sample text"
        )
        assert quote_block.paragraphs[0].runs[0].style.bold is True
        assert quote_block.paragraphs[-1].runs[0].style.bold is True
        assert [p.list_style_type for p in quote_block.paragraphs[1:]] == [
            "disc",
            "disc",
            "disc",
        ]

    def test_decorated_raw_text_container_keeps_leading_paragraph(
        self, decorated_raw_text_html: Path
    ) -> None:
        pres = extract_presentation_sync(decorated_raw_text_html)
        slide = pres.slides[0]
        decorated = [
            e for e in slide.elements if e.element_type == ElementType.DECORATED_BLOCK
        ]
        assert len(decorated) == 1
        quote_block = decorated[0]
        assert len(quote_block.paragraphs) == 2
        first_text = "".join(run.text for run in quote_block.paragraphs[0].runs)
        second_text = "".join(run.text for run in quote_block.paragraphs[1].runs)
        assert quote_block.paragraphs[0].space_before_px == 0
        assert quote_block.paragraphs[0].space_after_px == 0
        assert first_text.startswith(
            "This callout contains neutral placeholder prose for layout testing."
        )
        assert not first_text.startswith(" ")
        assert not first_text.endswith(" ")
        assert "paragraph extraction" in first_text
        assert "Default mode is Example. Optional mode is Alternate." in second_text

    def test_code_block_preserves_newlines_and_indentation(
        self, tmp_path: Path, tmp_output_dir: Path
    ) -> None:
        md_path = tmp_path / "code-block.md"
        md_path.write_text(
            """# Slide

```python
from dataclasses import dataclass

@dataclass
class Sample:
    value: int
```
""",
            encoding="utf-8",
        )

        html_path = render_to_html(md_path, output_dir=tmp_output_dir)
        pres = extract_presentation_sync(html_path)
        slide = pres.slides[0]
        code_blocks = [
            e for e in slide.elements if e.element_type == ElementType.CODE_BLOCK
        ]

        assert len(code_blocks) == 1
        code = code_blocks[0]
        assert ["".join(run.text for run in p.runs) for p in code.paragraphs] == [
            "from dataclasses import dataclass",
            " ",
            "@dataclass",
            "class Sample:",
            "    value: int",
        ]

    def test_inline_code_stays_in_paragraph_runs(
        self, tmp_path: Path, tmp_output_dir: Path
    ) -> None:
        md_path = tmp_path / "inline-code.md"
        md_path.write_text(
            "# Slide\n\nThis uses `inline code` in a sentence.\n",
            encoding="utf-8",
        )

        html_path = render_to_html(md_path, output_dir=tmp_output_dir)
        pres = extract_presentation_sync(html_path)
        slide = pres.slides[0]
        paragraphs = [
            e for e in slide.elements if e.element_type == ElementType.PARAGRAPH
        ]
        assert paragraphs
        inline_run = next(
            run
            for paragraph in paragraphs
            for run in paragraph.paragraphs[0].runs
            if run.text == "inline code"
        )
        assert inline_run.style.font_family == "Courier New"
        assert inline_run.style.color.a == 1.0
        assert inline_run.style.background_color is not None
        assert inline_run.style.background_color.r == 129
        assert inline_run.style.background_color.g == 139
        assert inline_run.style.background_color.b == 152
        assert inline_run.style.background_color.a == 0.12
        assert not any(
            e.element_type == ElementType.DECORATED_BLOCK
            and e.paragraphs
            and e.paragraphs[0].runs[0].text == "inline code"
            for e in slide.elements
        )

    def test_inline_code_is_not_extracted_as_overlay_decorated_element(
        self, tmp_path: Path, tmp_output_dir: Path
    ) -> None:
        md_path = tmp_path / "inline-code-overlay.md"
        md_path.write_text(
            "# Slide\n\nThis uses `inline code` in a sentence.\n",
            encoding="utf-8",
        )

        html_path = render_to_html(md_path, output_dir=tmp_output_dir)
        pres = extract_presentation_sync(html_path)
        slide = pres.slides[0]

        paragraph = next(
            e for e in slide.elements if e.element_type == ElementType.PARAGRAPH
        )

        inline_run = next(
            run for run in paragraph.paragraphs[0].runs if run.text == "inline code"
        )
        assert inline_run.style.color.a == 1.0
        assert inline_run.style.background_color is not None
        assert inline_run.style.background_color.r == 129
        assert inline_run.style.background_color.g == 139
        assert inline_run.style.background_color.b == 152
        assert inline_run.style.background_color.a == 0.12
        assert not any(
            e.element_type == ElementType.DECORATED_BLOCK
            and e.decoration
            and e.paragraphs
            and e.paragraphs[0].runs[0].text == "inline code"
            for e in slide.elements
        )

    def test_decorated_badge_is_extracted_as_separate_element(
        self, tmp_path: Path, tmp_output_dir: Path
    ) -> None:
        md_path = tmp_path / "badge-card.md"
        md_path.write_text(
            """---
marp: true
style: |
  .card {
    background: #eef4ff;
    border: 1px solid #bfd3ff;
    border-radius: 16px;
    padding: 18px 20px;
  }
  .badge {
    display: inline-block;
    padding: 0.14em 0.5em;
    border-radius: 999px;
    background: #dbeafe;
    color: #1d4ed8;
    font-size: 0.76em;
    font-weight: 700;
  }
---

<div class="card">
  <div class="badge">Good</div>
  <p>Body text under the badge.</p>
</div>
""",
            encoding="utf-8",
        )

        html_path = render_to_html(md_path, output_dir=tmp_output_dir)
        pres = extract_presentation_sync(html_path)
        slide = pres.slides[0]

        shape_only_card = next(
            e
            for e in slide.elements
            if e.element_type == ElementType.DECORATED_BLOCK
            and e.decoration
            and e.decoration.border_radius_px == pytest.approx(16.0)
            and not e.paragraphs
        )
        badge = next(
            e
            for e in slide.elements
            if e.element_type == ElementType.DECORATED_BLOCK
            and e.decoration
            and e.decoration.border_radius_px > 100
        )
        body = next(
            e for e in slide.elements if e.element_type == ElementType.PARAGRAPH
        )

        assert shape_only_card.box.width > badge.box.width
        assert badge.paragraphs[0].runs[0].text == "Good"
        assert body.paragraphs[0].runs[0].text == "Body text under the badge."

    def test_decorated_card_with_table_is_shape_only_and_keeps_children(
        self, tmp_path: Path, tmp_output_dir: Path
    ) -> None:
        md_path = tmp_path / "card-table.md"
        md_path.write_text(
            """---
marp: true
style: |
  .card {
    background: #eef4ff;
    border: 1px solid #bfd3ff;
    border-radius: 16px;
    padding: 18px 20px;
  }
---

<div class="card">
  <h3>Left Stack</h3>
  <p>A short paragraph sits above a small table.</p>
  <table>
    <tr><th>Key</th><th>Value</th></tr>
    <tr><td>alpha</td><td>12</td></tr>
  </table>
</div>
""",
            encoding="utf-8",
        )

        html_path = render_to_html(md_path, output_dir=tmp_output_dir)
        pres = extract_presentation_sync(html_path)
        slide = pres.slides[0]

        card = next(
            e
            for e in slide.elements
            if e.element_type == ElementType.DECORATED_BLOCK
            and e.decoration
            and e.decoration.border_radius_px == pytest.approx(16.0)
            and not e.paragraphs
        )
        heading = next(
            e for e in slide.elements if e.element_type == ElementType.HEADING
        )
        paragraph = next(
            e for e in slide.elements if e.element_type == ElementType.PARAGRAPH
        )
        table = next(e for e in slide.elements if e.element_type == ElementType.TABLE)

        assert card.box.width >= table.box.width
        assert heading.paragraphs[0].runs[0].text == "Left Stack"
        assert "A short paragraph" in paragraph.paragraphs[0].runs[0].text

    def test_decorated_card_with_image_is_shape_only_and_keeps_image_child(
        self, tmp_path: Path, tmp_output_dir: Path
    ) -> None:
        image_path = tmp_path / "sample.png"
        image_path.write_bytes(
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0"
            b"\x00\x00\x03\x01\x01\x00\xc9\xfe\x92\xef\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        md_path = tmp_path / "card-image.md"
        md_path.write_text(
            f"""---
marp: true
style: |
  .card {{
    background: #eef4ff;
    border: 1px solid #bfd3ff;
    border-radius: 16px;
    padding: 18px 20px;
  }}
---

<div class="card">
  <p>Chart preview</p>
  <img src="{image_path.as_posix()}" alt="Chart" style="width:100%; height:120px; object-fit:contain;" />
</div>
""",
            encoding="utf-8",
        )

        html_path = render_to_html(md_path, output_dir=tmp_output_dir)
        pres = extract_presentation_sync(html_path)
        slide = pres.slides[0]

        card = next(
            e
            for e in slide.elements
            if e.element_type == ElementType.DECORATED_BLOCK
            and e.decoration
            and e.decoration.border_radius_px == pytest.approx(16.0)
            and not e.paragraphs
        )
        paragraph = next(
            e for e in slide.elements if e.element_type == ElementType.PARAGRAPH
        )
        image = next(e for e in slide.elements if e.element_type == ElementType.IMAGE)

        assert paragraph.paragraphs[0].runs[0].text == "Chart preview"
        assert card.box.width >= image.box.width

    def test_figure_captions_and_image_decoration_are_extracted(
        self, tmp_path: Path, tmp_output_dir: Path
    ) -> None:
        md_path = tmp_path / "figure.md"
        md_path.write_text(
            """---
marp: true
style: |
  .compare-row {
    display: flex;
    gap: 20px;
  }
  .compare-row img {
    width: 100%;
    height: 220px;
    object-fit: contain;
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 12px;
  }
  .compare-row figcaption {
    font-size: 0.7em;
    text-align: center;
    margin-top: 8px;
  }
---

# Slide

<div class="compare-row">
  <figure>
    <img src="./images/chart-wave-raw.png" alt="Sample image A" />
    <figcaption>Image A within the same container size</figcaption>
  </figure>
</div>
""",
            encoding="utf-8",
        )

        html_path = render_to_html(md_path, output_dir=tmp_output_dir)
        pres = extract_presentation_sync(html_path)
        slide = pres.slides[0]

        images = [e for e in slide.elements if e.element_type == ElementType.IMAGE]
        paragraphs = [
            e for e in slide.elements if e.element_type == ElementType.PARAGRAPH
        ]

        assert len(images) == 1
        assert images[0].decoration is not None
        assert images[0].decoration.border_top.width_px > 0
        assert images[0].decoration.border_radius_px > 0
        assert any(
            "Image A within the same container size"
            in "".join(run.text for run in p.paragraphs[0].runs)
            for p in paragraphs
        )

    def test_single_image_panel_is_extracted_as_framed_image(
        self, tmp_path: Path, tmp_output_dir: Path
    ) -> None:
        md_path = tmp_path / "panel-image.md"
        md_path.write_text(
            """---
marp: true
style: |
  .panel {
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 14px;
    padding: 14px 18px;
  }
---

# Slide

<div class="panel">
  <img src="./images/diagram-network.svg" alt="Framed SVG" style="width:100%; height:420px; object-fit:contain;" />
</div>
""",
            encoding="utf-8",
        )

        html_path = render_to_html(md_path, output_dir=tmp_output_dir)
        pres = extract_presentation_sync(html_path)
        slide = pres.slides[0]
        images = [e for e in slide.elements if e.element_type == ElementType.IMAGE]

        assert len(images) == 1
        assert images[0].decoration is not None
        assert images[0].decoration.border_top.width_px > 0
        assert images[0].decoration.padding.left_px > 0

    def test_markdown_blockquote_extracts_decoration(
        self, tmp_path: Path, tmp_output_dir: Path
    ) -> None:
        md_path = tmp_path / "blockquote.md"
        md_path.write_text(
            "# Slide\n\n> Sample blockquote text\n",
            encoding="utf-8",
        )

        html_path = render_to_html(md_path, output_dir=tmp_output_dir)
        pres = extract_presentation_sync(html_path)
        slide = pres.slides[0]
        quotes = [e for e in slide.elements if e.element_type == ElementType.BLOCKQUOTE]

        assert len(quotes) == 1
        quote = quotes[0]
        assert quote.decoration is not None
        assert quote.decoration.border_left.width_px > 0
        assert quote.decoration.padding.left_px > 0

    def test_extracts_element_z_index(self, tmp_path: Path) -> None:
        html_path = tmp_path / "zindex.html"
        html_path.write_text(
            """<!doctype html>
<html>
<body>
  <section id="1" style="position: relative; width: 1280px; height: 720px;">
    <p style="position:absolute; left:100px; top:100px; z-index: 1;">Low</p>
    <p style="position:absolute; left:120px; top:120px; z-index: 9;">High</p>
  </section>
</body>
</html>
""",
            encoding="utf-8",
        )
        pres = extract_presentation_sync(html_path)
        slide = pres.slides[0]
        paragraphs = [
            e for e in slide.elements if e.element_type == ElementType.PARAGRAPH
        ]

        assert [e.z_index for e in paragraphs] == [1, 9]

    def test_paragraph_wrapped_image_is_extracted_as_image(
        self, tmp_path: Path
    ) -> None:
        html_path = tmp_path / "wrapped-image.html"
        html_path.write_text(
            """<!doctype html>
<html>
<body>
  <section id="1" style="width: 1280px; height: 720px;">
    <p><img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4nGP4z8BQDwAEgAF/pooBPQAAAABJRU5ErkJggg==" style="width: 100px;" /></p>
  </section>
</body>
</html>
""",
            encoding="utf-8",
        )

        pres = extract_presentation_sync(html_path)
        slide = pres.slides[0]

        images = [e for e in slide.elements if e.element_type == ElementType.IMAGE]
        paragraphs = [
            e for e in slide.elements if e.element_type == ElementType.PARAGRAPH
        ]
        assert len(images) == 1
        assert not paragraphs


@pytest.mark.integration
class TestParagraphGrouping:
    """Tests for grouping adjacent paragraphs into one textbox element."""

    def test_adjacent_paragraphs_become_single_element(
        self, multi_paragraph_html: Path
    ) -> None:
        pres = extract_presentation_sync(multi_paragraph_html)
        slide = pres.slides[0]
        paragraphs = [
            e for e in slide.elements if e.element_type == ElementType.PARAGRAPH
        ]
        assert len(paragraphs) == 1
        assert len(paragraphs[0].paragraphs) == 2
