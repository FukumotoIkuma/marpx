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

    def test_transparent_table_cell_background_does_not_become_alpha_zero(
        self, tmp_path: Path, tmp_output_dir: Path
    ) -> None:
        md_path = tmp_path / "transparent-table-cell.md"
        md_path.write_text(
            """---
marp: true
---

<style scoped>
table { color: white; }
</style>

| A | B |
|---|---|
| 1 | 2 |
""",
            encoding="utf-8",
        )

        html_path = render_to_html(md_path, output_dir=tmp_output_dir)
        pres = extract_presentation_sync(html_path)
        slide = pres.slides[0]
        table = next(e for e in slide.elements if e.element_type == ElementType.TABLE)

        background = table.table_rows[0].cells[0].background
        assert background is None or background.a > 0

    def test_background_split_ratio_is_extracted(
        self, tmp_path: Path, tmp_output_dir: Path
    ) -> None:
        md_path = tmp_path / "background-split-ratio.md"
        md_path.write_text(
            """---
marp: true
---

![bg left:40%](https://picsum.photos/800/600)

# Slide
""",
            encoding="utf-8",
        )

        html_path = render_to_html(md_path, output_dir=tmp_output_dir)
        pres = extract_presentation_sync(html_path)
        slide = pres.slides[0]

        assert len(slide.background.images) == 1
        bg = slide.background.images[0]
        assert bg.split == "left"
        assert bg.split_ratio == pytest.approx(0.4)
        assert bg.box is not None
        assert bg.box.width == pytest.approx(slide.width_px * 0.4, abs=2)

    def test_multiple_background_images_keep_distinct_boxes(
        self, tmp_path: Path, tmp_output_dir: Path
    ) -> None:
        md_path = tmp_path / "multiple-backgrounds.md"
        md_path.write_text(
            """---
marp: true
---

![bg](https://picsum.photos/1280/720?random=1)
![bg](https://picsum.photos/1280/720?random=2)

# Slide
""",
            encoding="utf-8",
        )

        html_path = render_to_html(md_path, output_dir=tmp_output_dir)
        pres = extract_presentation_sync(html_path)
        slide = pres.slides[0]

        assert len(slide.background.images) == 2
        first, second = slide.background.images
        assert first.box is not None
        assert second.box is not None
        assert first.box.x == pytest.approx(0, abs=2)
        assert second.box.x > first.box.x
        assert first.box.width == pytest.approx(slide.width_px / 2, abs=2)
        assert second.box.width == pytest.approx(slide.width_px / 2, abs=2)

    def test_table_text_does_not_inherit_hidden_svg_opacity(
        self, tmp_path: Path, tmp_output_dir: Path
    ) -> None:
        md_path = tmp_path / "table-text-opacity.md"
        md_path.write_text(
            """---
marp: true
---

<style scoped>
th { color: white; background: linear-gradient(135deg, #3b82f6, #2563eb); }
</style>

| Feature | Free |
|---------|:----:|
| Users | 5 |
""",
            encoding="utf-8",
        )

        html_path = render_to_html(md_path, output_dir=tmp_output_dir)
        pres = extract_presentation_sync(html_path)
        slide = pres.slides[0]
        table = next(e for e in slide.elements if e.element_type == ElementType.TABLE)

        header_run = table.table_rows[0].cells[0].paragraphs[0].runs[0]
        assert header_run.style.color.a == pytest.approx(1.0)

    def test_table_cell_resolves_gradient_and_row_background_styles(
        self, tmp_path: Path, tmp_output_dir: Path
    ) -> None:
        md_path = tmp_path / "table-cell-style-resolution.md"
        md_path.write_text(
            """---
marp: true
---

<style scoped>
th { color: white; background: linear-gradient(135deg, #3b82f6, #2563eb); padding: 14px 16px; }
td { padding: 12px 16px; border-bottom: 1px solid #e2e8f0; }
tbody tr:nth-child(odd) { background: #f1f5f9; }
</style>

| Feature | Free |
|---------|:----:|
| Users | 5 |
""",
            encoding="utf-8",
        )

        html_path = render_to_html(md_path, output_dir=tmp_output_dir)
        pres = extract_presentation_sync(html_path)
        slide = pres.slides[0]
        table = next(e for e in slide.elements if e.element_type == ElementType.TABLE)

        header = table.table_rows[0].cells[0]
        body = table.table_rows[1].cells[0]

        assert header.background_gradient is not None
        assert header.padding.left_px == pytest.approx(16.0)
        assert body.background is not None
        assert body.background.r == 241
        assert body.background.g == 245
        assert body.background.b == 249
        assert body.border_bottom.width_px == pytest.approx(1.0)

    def test_parent_opacity_propagates_to_text_decoration_image_and_table(
        self, tmp_path: Path, tmp_output_dir: Path
    ) -> None:
        md_path = tmp_path / "opacity-propagation.md"
        md_path.write_text(
            """---
marp: true
---

<div style="opacity: 0.6">
  <p style="color: rgb(10, 20, 30)">Alpha text</p>
  <div style="background: rgba(255, 0, 0, 0.5); padding: 12px">Panel</div>
  <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR42mP4z8AAAwEBAMn+ku8AAAAASUVORK5CYII=" />
  <table>
    <tr><td style="background: rgba(0, 128, 0, 0.5)">Cell</td></tr>
  </table>
</div>
""",
            encoding="utf-8",
        )

        html_path = render_to_html(md_path, output_dir=tmp_output_dir)
        pres = extract_presentation_sync(html_path)
        slide = pres.slides[0]

        paragraph = next(
            e for e in slide.elements if e.element_type == ElementType.PARAGRAPH
        )
        panel = next(
            e for e in slide.elements if e.element_type == ElementType.DECORATED_BLOCK
        )
        image = next(e for e in slide.elements if e.element_type == ElementType.IMAGE)
        table = next(e for e in slide.elements if e.element_type == ElementType.TABLE)

        assert paragraph.paragraphs[0].runs[0].style.color.a == pytest.approx(0.6)
        assert panel.decoration is not None
        assert panel.decoration.background_color is not None
        assert panel.decoration.background_color.a == pytest.approx(0.3)
        assert image.image_opacity == pytest.approx(0.6)
        assert table.table_rows[0].cells[0].background is not None
        assert table.table_rows[0].cells[0].background.a == pytest.approx(0.3)


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

    def test_linear_gradient_box_and_text_are_not_marked_unsupported(
        self, tmp_path: Path, tmp_output_dir: Path
    ) -> None:
        md_path = tmp_path / "gradient-supported.md"
        md_path.write_text(
            """---
marp: true
---

<style scoped>
.dot {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  border-radius: 50%;
  color: white;
}
.hero-title {
  background: linear-gradient(135deg, #c7d2fe, #818cf8, #c084fc);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
</style>

<div class="dot">Q1</div>
<h1 class="hero-title">Gradient Heading</h1>
""",
            encoding="utf-8",
        )

        html_path = render_to_html(md_path, output_dir=tmp_output_dir)
        pres = extract_presentation_sync(html_path)
        slide = pres.slides[0]

        assert all(
            element.element_type != ElementType.UNSUPPORTED
            for element in slide.elements
        )

        dot = next(
            element
            for element in slide.elements
            if element.element_type == ElementType.DECORATED_BLOCK
        )
        heading = next(
            element
            for element in slide.elements
            if element.element_type == ElementType.HEADING
        )

        assert dot.decoration is not None
        assert dot.decoration.background_gradient is not None
        assert "".join(run.text for p in dot.paragraphs for run in p.runs) == "Q1"
        assert heading.paragraphs[0].runs[0].style.color.r == 199
        assert heading.paragraphs[0].runs[0].style.color.g == 210
        assert heading.paragraphs[0].runs[0].style.color.b == 254


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

    def test_heading_with_inline_spans_preserves_inter_run_space(
        self, tmp_path: Path, tmp_output_dir: Path
    ) -> None:
        md_path = tmp_path / "heading-inline-space.md"
        md_path.write_text(
            """# Slide

## <span style="color:#60a5fa;">marpx</span> <span style="color:#e2e8f0;">Kitchen Sink</span>
""",
            encoding="utf-8",
        )

        html_path = render_to_html(md_path, output_dir=tmp_output_dir)
        pres = extract_presentation_sync(html_path)
        slide = pres.slides[0]
        heading = next(
            e
            for e in slide.elements
            if e.element_type == ElementType.HEADING and e.heading_level == 2
        )

        assert (
            "".join(run.text for run in heading.paragraphs[0].runs)
            == "marpx Kitchen Sink"
        )

    def test_paragraph_trims_html_indentation_whitespace(
        self, tmp_path: Path, tmp_output_dir: Path
    ) -> None:
        md_path = tmp_path / "paragraph-indentation.md"
        md_path.write_text(
            """# Slide

<p style="text-align:right; color:#94a3b8; font-size:0.62em;">
  Header · Footer · Paginate · Speaker Notes · Background — all directives supported
</p>
""",
            encoding="utf-8",
        )

        html_path = render_to_html(md_path, output_dir=tmp_output_dir)
        pres = extract_presentation_sync(html_path)
        slide = pres.slides[0]
        paragraph = next(
            e for e in slide.elements if e.element_type == ElementType.PARAGRAPH
        )

        text = "".join(run.text for run in paragraph.paragraphs[0].runs)
        assert (
            text
            == "Header · Footer · Paginate · Speaker Notes · Background — all directives supported"
        )

    def test_paragraph_preserves_br_line_breaks(
        self, tmp_path: Path, tmp_output_dir: Path
    ) -> None:
        md_path = tmp_path / "paragraph-br.md"
        md_path.write_text(
            """# Slide

<p>
  <strong>Heading · List · Table · Code · Image · Badge · Quote</strong><br/>
  1 枚に全部載せ。これがネイティブ PowerPoint になります。
</p>
""",
            encoding="utf-8",
        )

        html_path = render_to_html(md_path, output_dir=tmp_output_dir)
        pres = extract_presentation_sync(html_path)
        slide = pres.slides[0]
        paragraph = next(
            e for e in slide.elements if e.element_type == ElementType.PARAGRAPH
        )

        text = "".join(run.text for run in paragraph.paragraphs[0].runs)
        assert text == (
            "Heading · List · Table · Code · Image · Badge · Quote\n"
            "1 枚に全部載せ。これがネイティブ PowerPoint になります。"
        )

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

    def test_code_block_preserves_pre_decoration(
        self, tmp_path: Path, tmp_output_dir: Path
    ) -> None:
        md_path = tmp_path / "decorated-code-block.md"
        md_path.write_text(
            """# Slide

<pre style="background:#f6f8fa; border:1px solid #d1d9e0; border-radius:6px; padding:16px; margin:0;"><code>alpha
beta</code></pre>
""",
            encoding="utf-8",
        )

        html_path = render_to_html(md_path, output_dir=tmp_output_dir)
        pres = extract_presentation_sync(html_path)
        slide = pres.slides[0]
        code = next(
            e for e in slide.elements if e.element_type == ElementType.CODE_BLOCK
        )

        assert code.decoration is not None
        assert code.decoration.border_radius_px == pytest.approx(6.0)
        assert code.decoration.background_color is not None
        assert code.decoration.background_color.r == 246
        assert code.decoration.background_color.g == 248
        assert code.decoration.background_color.b == 250
        assert code.content_box is not None
        assert code.content_box.x > code.box.x
        assert code.content_box.y > code.box.y

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

    def test_mark_stays_in_paragraph_runs(self, tmp_path: Path, tmp_output_dir: Path) -> None:
        md_path = tmp_path / "inline-mark.md"
        md_path.write_text(
            "# Slide\n\n<mark>This text is highlighted</mark> and continues normally.\n",
            encoding="utf-8",
        )

        html_path = render_to_html(md_path, output_dir=tmp_output_dir)
        pres = extract_presentation_sync(html_path)
        slide = pres.slides[0]

        paragraph = next(
            e for e in slide.elements if e.element_type == ElementType.PARAGRAPH
        )
        marked_run = next(
            run for run in paragraph.paragraphs[0].runs if run.text == "This text is highlighted"
        )

        assert marked_run.style.background_color is not None
        assert marked_run.style.background_color.a > 0
        assert not any(
            e.element_type == ElementType.DECORATED_BLOCK
            and e.paragraphs
            and e.paragraphs[0].runs[0].text == "This text is highlighted"
            for e in slide.elements
        )

    def test_twemoji_inline_images_fallback_to_alt_text(
        self, tmp_path: Path, tmp_output_dir: Path
    ) -> None:
        md_path = tmp_path / "twemoji-inline.md"
        md_path.write_text(
            "# Slide\n\nTarget: 🎯 Rocket: 🚀\n",
            encoding="utf-8",
        )

        html_path = render_to_html(md_path, output_dir=tmp_output_dir)
        pres = extract_presentation_sync(html_path)
        slide = pres.slides[0]

        paragraph = next(
            e for e in slide.elements if e.element_type == ElementType.PARAGRAPH
        )
        run_texts = [run.text for run in paragraph.paragraphs[0].runs]

        assert "🎯" in run_texts
        assert "🚀" in run_texts

    def test_inline_math_creates_math_elements_and_placeholder_runs(
        self, tmp_path: Path, tmp_output_dir: Path
    ) -> None:
        md_path = tmp_path / "inline-math.md"
        md_path.write_text(
            """---
marp: true
math: mathjax
---

# Slide

Inline: $E = mc^2$ and $\\sum_{i=1}^{n} i$
""",
            encoding="utf-8",
        )

        html_path = render_to_html(md_path, output_dir=tmp_output_dir)
        pres = extract_presentation_sync(html_path)
        slide = pres.slides[0]

        math_elements = [e for e in slide.elements if e.element_type == ElementType.MATH]
        assert len(math_elements) == 2
        assert all(
            e.unsupported_info and e.unsupported_info.tag_name == "mjx-container"
            for e in math_elements
        )

        paragraph = next(
            e for e in slide.elements if e.element_type == ElementType.PARAGRAPH
        )
        placeholder_runs = [
            run for run in paragraph.paragraphs[0].runs if run.style.color.a == 0.0
        ]
        assert len(placeholder_runs) == 2
        assert all(run.text for run in placeholder_runs)

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
        assert card.content_box is not None
        assert card.content_box.x > card.box.x
        assert card.content_box.y > card.box.y
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
        assert quote.content_box is not None
        assert quote.decoration.border_left.width_px > 0
        assert quote.decoration.padding.left_px > 0
        assert quote.content_box.x > quote.box.x
        assert quote.content_box.width < quote.box.width

    def test_nested_blockquote_preserves_nested_quote_and_paragraph_break(
        self, tmp_path: Path, tmp_output_dir: Path
    ) -> None:
        md_path = tmp_path / "nested-blockquote.md"
        md_path.write_text(
            """# Slide

> > line one
> >
> > -- **Jeff Atwood**, *Coding Horror*
""",
            encoding="utf-8",
        )

        html_path = render_to_html(md_path, output_dir=tmp_output_dir)
        pres = extract_presentation_sync(html_path)
        slide = pres.slides[0]
        quotes = [e for e in slide.elements if e.element_type == ElementType.BLOCKQUOTE]

        assert len(quotes) == 2
        outer, inner = quotes
        assert outer.paragraphs == []
        assert len(inner.paragraphs) == 2
        assert "".join(run.text for run in inner.paragraphs[1].runs).startswith(
            "-- Jeff Atwood"
        )

    def test_blockquote_strikethrough_is_extracted(
        self, tmp_path: Path, tmp_output_dir: Path
    ) -> None:
        md_path = tmp_path / "blockquote-strike.md"
        md_path.write_text(
            """# Slide

> Remember that ~~premature optimization~~ is the root of all evil.
""",
            encoding="utf-8",
        )

        html_path = render_to_html(md_path, output_dir=tmp_output_dir)
        pres = extract_presentation_sync(html_path)
        slide = pres.slides[0]
        quote = next(
            e for e in slide.elements if e.element_type == ElementType.BLOCKQUOTE
        )
        struck = next(
            run
            for run in quote.paragraphs[0].runs
            if run.text == "premature optimization"
        )
        assert struck.style.strike is True

    def test_nested_bold_inside_strikethrough_preserves_strike(
        self, tmp_path: Path, tmp_output_dir: Path
    ) -> None:
        md_path = tmp_path / "nested-strike-bold.md"
        md_path.write_text(
            """# Slide

Strikethrough with bold: <s>this is struck through with <strong>bold emphasis</strong> inside</s>
""",
            encoding="utf-8",
        )

        html_path = render_to_html(md_path, output_dir=tmp_output_dir)
        pres = extract_presentation_sync(html_path)
        slide = pres.slides[0]
        paragraph = next(
            e for e in slide.elements if e.element_type == ElementType.PARAGRAPH
        )
        bold_run = next(
            run for run in paragraph.paragraphs[0].runs if run.text == "bold emphasis"
        )

        assert bold_run.style.bold is True
        assert bold_run.style.strike is True

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
