"""Tests for marpx.extractor module.

All tests require Playwright, so they are marked as integration tests.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from marpx.extraction.extractor import extract_presentation_sync
from marpx.extraction.marp_renderer import render_to_html
from marpx.models import ElementType, MathRun

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="module")
def simple_html(session_output_dir: Path) -> Path:
    """Render simple.md to HTML for extraction tests."""
    return render_to_html(FIXTURES_DIR / "simple.md", output_dir=session_output_dir)


@pytest.fixture(scope="module")
def nested_list_html(session_output_dir: Path) -> Path:
    """Render nested-list.md to HTML."""
    return render_to_html(
        FIXTURES_DIR / "nested-list.md", output_dir=session_output_dir
    )


@pytest.fixture(scope="module")
def table_html(session_output_dir: Path) -> Path:
    """Render table.md to HTML."""
    return render_to_html(FIXTURES_DIR / "table.md", output_dir=session_output_dir)


@pytest.fixture(scope="module")
def complex_html(session_output_dir: Path) -> Path:
    """Render complex-unsupported.md to HTML."""
    return render_to_html(
        FIXTURES_DIR / "complex-unsupported.md", output_dir=session_output_dir
    )


@pytest.fixture(scope="module")
def rendered_layout_boxes_html(session_output_dir: Path) -> Path:
    """Render rendered-layout-boxes.md to HTML."""
    return render_to_html(
        FIXTURES_DIR / "rendered-layout-boxes.md", output_dir=session_output_dir
    )


@pytest.fixture(scope="module")
def rendered_layout_images_html(session_output_dir: Path) -> Path:
    """Render rendered-layout-images.md to HTML."""
    return render_to_html(
        FIXTURES_DIR / "rendered-layout-images.md", output_dir=session_output_dir
    )


@pytest.fixture(scope="module")
def quote_box_list_html(session_output_dir: Path) -> Path:
    """Render quote-box-list.md to HTML."""
    return render_to_html(
        FIXTURES_DIR / "quote-box-list.md", output_dir=session_output_dir
    )


@pytest.fixture(scope="module")
def decorated_raw_text_html(session_output_dir: Path) -> Path:
    """Render decorated-raw-text.md to HTML."""
    return render_to_html(
        FIXTURES_DIR / "decorated-raw-text.md", output_dir=session_output_dir
    )


@pytest.fixture(scope="module")
def multi_paragraph_html(session_output_dir: Path) -> Path:
    """Render multi-paragraph.md to HTML."""
    return render_to_html(
        FIXTURES_DIR / "multi-paragraph.md", output_dir=session_output_dir
    )


@pytest.fixture(scope="module")
def simple_pres(simple_html: Path):
    return extract_presentation_sync(simple_html)


@pytest.fixture(scope="module")
def nested_list_pres(nested_list_html: Path):
    return extract_presentation_sync(nested_list_html)


@pytest.fixture(scope="module")
def table_pres(table_html: Path):
    return extract_presentation_sync(table_html)


@pytest.fixture(scope="module")
def complex_pres(complex_html: Path):
    return extract_presentation_sync(complex_html)


@pytest.fixture(scope="module")
def rendered_layout_boxes_pres(rendered_layout_boxes_html: Path):
    return extract_presentation_sync(rendered_layout_boxes_html)


@pytest.fixture(scope="module")
def rendered_layout_images_pres(rendered_layout_images_html: Path):
    return extract_presentation_sync(rendered_layout_images_html)


@pytest.fixture(scope="module")
def quote_box_list_pres(quote_box_list_html: Path):
    return extract_presentation_sync(quote_box_list_html)


@pytest.fixture(scope="module")
def decorated_raw_text_pres(decorated_raw_text_html: Path):
    return extract_presentation_sync(decorated_raw_text_html)


@pytest.fixture(scope="module")
def multi_paragraph_pres(multi_paragraph_html: Path):
    return extract_presentation_sync(multi_paragraph_html)


# ---------------------------------------------------------------------------
# Batched fixture files: render once, share across many tests
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def inline_text_html(session_output_dir: Path) -> Path:
    """Render inline-text-features.md to HTML."""
    return render_to_html(
        FIXTURES_DIR / "inline-text-features.md", output_dir=session_output_dir
    )


@pytest.fixture(scope="module")
def inline_text_pres(inline_text_html: Path):
    return extract_presentation_sync(inline_text_html)


@pytest.fixture(scope="module")
def decoration_html(session_output_dir: Path) -> Path:
    """Render decoration-features.md to HTML."""
    return render_to_html(
        FIXTURES_DIR / "decoration-features.md", output_dir=session_output_dir
    )


@pytest.fixture(scope="module")
def decoration_pres(decoration_html: Path):
    return extract_presentation_sync(decoration_html)


@pytest.fixture(scope="module")
def gradient_html(session_output_dir: Path) -> Path:
    """Render gradient-features.md to HTML."""
    return render_to_html(
        FIXTURES_DIR / "gradient-features.md", output_dir=session_output_dir
    )


@pytest.fixture(scope="module")
def gradient_pres(gradient_html: Path):
    return extract_presentation_sync(gradient_html)


@pytest.fixture(scope="module")
def decomposition_html(session_output_dir: Path) -> Path:
    """Render decomposition-features.md to HTML."""
    return render_to_html(
        FIXTURES_DIR / "decomposition-features.md", output_dir=session_output_dir
    )


@pytest.fixture(scope="module")
def decomposition_pres(decomposition_html: Path):
    return extract_presentation_sync(decomposition_html)


@pytest.fixture(scope="module")
def math_features_html(session_output_dir: Path) -> Path:
    """Render math-features.md to HTML."""
    return render_to_html(
        FIXTURES_DIR / "math-features.md", output_dir=session_output_dir
    )


@pytest.fixture(scope="module")
def math_features_pres(math_features_html: Path):
    return extract_presentation_sync(math_features_html)


@pytest.fixture(scope="module")
def table_features_html(session_output_dir: Path) -> Path:
    """Render table-features.md to HTML."""
    return render_to_html(
        FIXTURES_DIR / "table-features.md", output_dir=session_output_dir
    )


@pytest.fixture(scope="module")
def table_features_pres(table_features_html: Path):
    return extract_presentation_sync(table_features_html)


@pytest.mark.integration
class TestExtractSimple:
    """Tests for extracting simple.md presentation."""

    def test_slide_count(self, simple_pres) -> None:
        pres = simple_pres
        assert len(pres.slides) == 2

    def test_slide_dimensions(self, simple_pres) -> None:
        pres = simple_pres
        slide = pres.slides[0]
        # Marp default is 1280x720
        assert slide.width_px == pytest.approx(1280, abs=10)
        assert slide.height_px == pytest.approx(720, abs=10)

    def test_first_slide_has_heading(self, simple_pres) -> None:
        pres = simple_pres
        slide = pres.slides[0]
        heading_elements = [
            e for e in slide.elements if e.element_type == ElementType.HEADING
        ]
        assert len(heading_elements) >= 1
        # The heading should contain "Hello World"
        heading = heading_elements[0]
        text = "".join(r.text for p in heading.paragraphs for r in p.runs)
        assert "Hello World" in text

    def test_first_slide_has_paragraph(self, simple_pres) -> None:
        pres = simple_pres
        slide = pres.slides[0]
        para_elements = [
            e for e in slide.elements if e.element_type == ElementType.PARAGRAPH
        ]
        assert len(para_elements) >= 1

    def test_first_slide_has_list(self, simple_pres) -> None:
        pres = simple_pres
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

    def test_nested_levels(self, nested_list_pres) -> None:
        pres = nested_list_pres
        slide = pres.slides[0]
        list_elements = [
            e for e in slide.elements if e.element_type == ElementType.UNORDERED_LIST
        ]
        assert len(list_elements) >= 1

        items = list_elements[0].list_items
        # Should have items at multiple levels
        levels = {item.level for item in items}
        assert len(levels) >= 2  # At least level 0 and 1

    def test_level_0_items(self, nested_list_pres) -> None:
        pres = nested_list_pres
        slide = pres.slides[0]
        list_elements = [
            e for e in slide.elements if e.element_type == ElementType.UNORDERED_LIST
        ]
        items = list_elements[0].list_items
        level_0 = [i for i in items if i.level == 0]
        assert len(level_0) == 2  # "Level 1 item A" and "Level 1 item B"

    def test_unordered_nested_list_preserves_marker_styles(
        self, nested_list_pres
    ) -> None:
        pres = nested_list_pres
        slide = pres.slides[0]
        list_element = next(
            e for e in slide.elements if e.element_type == ElementType.UNORDERED_LIST
        )

        assert list_element.list_items[0].list_style_type == "disc"
        assert any(item.list_style_type == "circle" for item in list_element.list_items)
        assert any(item.list_style_type == "square" for item in list_element.list_items)

    def test_ordered_nested_list_preserves_numbering_style_and_spacing(
        self, nested_list_pres
    ) -> None:
        pres = nested_list_pres
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
        self, inline_text_pres
    ) -> None:
        slide = inline_text_pres.slides[11]
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

    def test_table_element_exists(self, table_pres) -> None:
        pres = table_pres
        slide = pres.slides[0]
        table_elements = [
            e for e in slide.elements if e.element_type == ElementType.TABLE
        ]
        assert len(table_elements) >= 1

    def test_table_row_count(self, table_pres) -> None:
        pres = table_pres
        slide = pres.slides[0]
        table_elements = [
            e for e in slide.elements if e.element_type == ElementType.TABLE
        ]
        table = table_elements[0]
        # 1 header + 3 data rows = 4 rows
        assert len(table.table_rows) == 4

    def test_table_cell_count(self, table_pres) -> None:
        pres = table_pres
        slide = pres.slides[0]
        table_elements = [
            e for e in slide.elements if e.element_type == ElementType.TABLE
        ]
        table = table_elements[0]
        # Each row should have 3 columns
        for row in table.table_rows:
            assert len(row.cells) == 3

    def test_transparent_table_cell_background_does_not_become_alpha_zero(
        self, table_features_pres
    ) -> None:
        slide = table_features_pres.slides[0]
        table = next(e for e in slide.elements if e.element_type == ElementType.TABLE)

        background = table.table_rows[0].cells[0].background
        assert background is None or background.a > 0

    def test_background_split_ratio_is_extracted(self, table_features_pres) -> None:
        slide = table_features_pres.slides[1]

        assert len(slide.background.images) == 1
        bg = slide.background.images[0]
        assert bg.split == "left"
        assert bg.split_ratio == pytest.approx(0.4)
        assert bg.box is not None
        assert bg.box.width == pytest.approx(slide.width_px * 0.4, abs=2)

    def test_multiple_background_images_keep_distinct_boxes(
        self, table_features_pres
    ) -> None:
        slide = table_features_pres.slides[2]

        assert len(slide.background.images) == 2
        first, second = slide.background.images
        assert first.box is not None
        assert second.box is not None
        assert first.box.x == pytest.approx(0, abs=2)
        assert second.box.x > first.box.x
        assert first.box.width == pytest.approx(slide.width_px / 2, abs=2)
        assert second.box.width == pytest.approx(slide.width_px / 2, abs=2)

    def test_table_text_does_not_inherit_hidden_svg_opacity(
        self, table_features_pres
    ) -> None:
        slide = table_features_pres.slides[3]
        table = next(e for e in slide.elements if e.element_type == ElementType.TABLE)

        header_run = table.table_rows[0].cells[0].paragraphs[0].runs[0]
        assert header_run.style.color.a == pytest.approx(1.0)

    def test_table_cell_resolves_gradient_and_row_background_styles(
        self, table_features_pres
    ) -> None:
        slide = table_features_pres.slides[4]
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
        self, table_features_pres
    ) -> None:
        slide = table_features_pres.slides[5]

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

    def test_has_unsupported_elements(self, complex_pres) -> None:
        pres = complex_pres
        # Check across all slides for unsupported elements (SVG)
        unsupported = []
        for slide in pres.slides:
            unsupported.extend(
                e for e in slide.elements if e.element_type == ElementType.UNSUPPORTED
            )
        assert len(unsupported) >= 1

    def test_slide_count(self, complex_pres) -> None:
        pres = complex_pres
        assert len(pres.slides) == 3

    def test_inline_svg_unsupported_preserves_markup(self, complex_pres) -> None:
        pres = complex_pres
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

    def test_linear_gradient_box_stays_native_but_gradient_text_falls_back(
        self, gradient_pres
    ) -> None:
        slide = gradient_pres.slides[4]

        dot = next(
            element
            for element in slide.elements
            if element.element_type == ElementType.DECORATED_BLOCK
        )
        assert dot.decoration is not None
        assert dot.decoration.background_gradient is not None
        assert "".join(run.text for p in dot.paragraphs for run in p.runs) == "Q1"
        heading = next(
            element
            for element in slide.elements
            if element.element_type == ElementType.HEADING
        )
        gradient_run = heading.paragraphs[0].runs[0]
        assert gradient_run.text == "Gradient Heading"
        assert gradient_run.style.text_gradient is not None
        assert "linear-gradient(" in gradient_run.style.text_gradient


@pytest.mark.integration
class TestRenderedLayoutCapture:
    """Tests for generic rendered-layout extraction."""

    def test_extracts_decorated_blocks(self, rendered_layout_boxes_pres) -> None:
        pres = rendered_layout_boxes_pres
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
        self, rendered_layout_boxes_pres
    ) -> None:
        pres = rendered_layout_boxes_pres
        slide = pres.slides[0]
        lists = [
            e for e in slide.elements if e.element_type == ElementType.UNORDERED_LIST
        ]
        assert lists
        first_item_text = "".join(run.text for run in lists[0].list_items[0].runs)
        assert "☐ " in first_item_text

    def test_extracts_object_fit_metadata(self, rendered_layout_images_pres) -> None:
        pres = rendered_layout_images_pres
        slide = pres.slides[0]
        images = [e for e in slide.elements if e.element_type == ElementType.IMAGE]
        assert len(images) == 2
        assert all(img.object_fit == "contain" for img in images)
        assert all(img.image_natural_width_px == 1 for img in images)
        assert all(img.image_natural_height_px == 1 for img in images)

    def test_quote_box_with_markdown_list_stays_decorated(
        self, quote_box_list_pres
    ) -> None:
        pres = quote_box_list_pres
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
        self, decorated_raw_text_pres
    ) -> None:
        pres = decorated_raw_text_pres
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
        self, inline_text_pres
    ) -> None:
        slide = inline_text_pres.slides[0]
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
        self, inline_text_pres
    ) -> None:
        slide = inline_text_pres.slides[1]
        paragraph = next(
            e for e in slide.elements if e.element_type == ElementType.PARAGRAPH
        )

        text = "".join(run.text for run in paragraph.paragraphs[0].runs)
        assert (
            text
            == "Header · Footer · Paginate · Speaker Notes · Background — all directives supported"
        )

    def test_paragraph_preserves_br_line_breaks(self, inline_text_pres) -> None:
        slide = inline_text_pres.slides[2]
        paragraph = next(
            e for e in slide.elements if e.element_type == ElementType.PARAGRAPH
        )

        text = "".join(run.text for run in paragraph.paragraphs[0].runs)
        assert text == (
            "Heading · List · Table · Code · Image · Badge · Quote\n"
            "1 枚に全部載せ。これがネイティブ PowerPoint になります。"
        )

    def test_code_block_preserves_newlines_and_indentation(
        self, inline_text_pres
    ) -> None:
        slide = inline_text_pres.slides[3]
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

    def test_code_block_preserves_pre_decoration(self, decoration_pres) -> None:
        slide = decoration_pres.slides[0]
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

    def test_inline_code_stays_in_paragraph_runs(self, inline_text_pres) -> None:
        slide = inline_text_pres.slides[4]
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
        self, inline_text_pres
    ) -> None:
        slide = inline_text_pres.slides[4]

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

    def test_mark_stays_in_paragraph_runs(self, inline_text_pres) -> None:
        slide = inline_text_pres.slides[5]

        paragraph = next(
            e for e in slide.elements if e.element_type == ElementType.PARAGRAPH
        )
        marked_run = next(
            run
            for run in paragraph.paragraphs[0].runs
            if run.text == "This text is highlighted"
        )

        assert marked_run.style.background_color is not None
        assert marked_run.style.background_color.a > 0
        assert not any(
            e.element_type == ElementType.DECORATED_BLOCK
            and e.paragraphs
            and e.paragraphs[0].runs[0].text == "This text is highlighted"
            for e in slide.elements
        )

    def test_twemoji_inline_images_fallback_to_alt_text(self, inline_text_pres) -> None:
        slide = inline_text_pres.slides[6]

        paragraph = next(
            e for e in slide.elements if e.element_type == ElementType.PARAGRAPH
        )
        run_texts = [run.text for run in paragraph.paragraphs[0].runs]

        assert "🎯" in run_texts
        assert "🚀" in run_texts

    def test_inline_math_creates_math_runs_in_paragraph(
        self, math_features_pres
    ) -> None:
        slide = math_features_pres.slides[0]

        # Inline math should NOT produce separate MATH elements
        math_elements = [
            e for e in slide.elements if e.element_type == ElementType.MATH
        ]
        assert len(math_elements) == 0

        # The paragraph should contain MathRun objects for inline math
        paragraph = next(
            e for e in slide.elements if e.element_type == ElementType.PARAGRAPH
        )
        runs = paragraph.paragraphs[0].runs
        math_runs = [run for run in runs if isinstance(run, MathRun)]
        assert len(math_runs) == 2
        latex_sources = [mr.latex_source for mr in math_runs]
        assert "E = mc^2" in latex_sources
        assert r"\sum_{i=1}^{n} i" in latex_sources

    def test_inline_math_produces_no_separate_elements(
        self, math_features_pres
    ) -> None:
        slide = math_features_pres.slides[0]

        # No separate MATH or UNSUPPORTED elements for inline math
        math_elements = [
            e for e in slide.elements if e.element_type == ElementType.MATH
        ]
        assert len(math_elements) == 0

        unsupported_elements = [
            e for e in slide.elements if e.element_type == ElementType.UNSUPPORTED
        ]
        assert len(unsupported_elements) == 0

        # Paragraph exists and contains MathRun objects
        paragraph_elements = [
            e for e in slide.elements if e.element_type == ElementType.PARAGRAPH
        ]
        assert len(paragraph_elements) == 1

        runs = paragraph_elements[0].paragraphs[0].runs
        math_runs = [run for run in runs if isinstance(run, MathRun)]
        assert len(math_runs) == 2

    def test_absolute_block_pseudo_elements_are_extracted(
        self, decomposition_pres
    ) -> None:
        slide = decomposition_pres.slides[8]
        pseudo_blocks = [
            e for e in slide.elements if e.element_type == ElementType.DECORATED_BLOCK
        ]

        assert any(
            e.decoration
            and e.decoration.background_gradient is not None
            and not e.paragraphs
            for e in pseudo_blocks
        )
        assert any(
            "".join(run.text for p in e.paragraphs for run in p.runs) == '"'
            for e in pseudo_blocks
        )
        quote_paragraph = next(
            e for e in slide.elements if e.element_type == ElementType.PARAGRAPH
        )
        assert (
            "".join(run.text for p in quote_paragraph.paragraphs for run in p.runs)
            == "Quoted text"
        )
        badge = next(
            e
            for e in pseudo_blocks
            if "".join(run.text for p in e.paragraphs for run in p.runs) == "POPULAR"
        )
        assert badge.decoration is not None
        assert badge.decoration.background_color is not None

    def test_box_shadow_is_extracted_into_decoration(self, decoration_pres) -> None:
        slide = decoration_pres.slides[1]
        card = next(
            e
            for e in slide.elements
            if e.element_type == ElementType.DECORATED_BLOCK
            and any(
                "".join(run.text for run in p.runs) == "Shadow card"
                for p in e.paragraphs
            )
        )

        assert card.decoration is not None
        assert len(card.decoration.box_shadows) == 2
        inset_shadow = next(
            shadow for shadow in card.decoration.box_shadows if shadow.inset
        )
        assert inset_shadow.offset_x_px == pytest.approx(0.0)
        assert inset_shadow.offset_y_px == pytest.approx(2.0)
        assert inset_shadow.blur_radius_px == pytest.approx(8.0)
        assert inset_shadow.color.r == 15
        assert inset_shadow.color.g == 23
        assert inset_shadow.color.b == 42
        assert inset_shadow.color.a == pytest.approx(0.08)

        outer_shadow = next(
            shadow for shadow in card.decoration.box_shadows if not shadow.inset
        )
        assert outer_shadow.offset_x_px == pytest.approx(0.0)
        assert outer_shadow.offset_y_px == pytest.approx(8.0)
        assert outer_shadow.blur_radius_px == pytest.approx(32.0)
        assert outer_shadow.color.r == 59
        assert outer_shadow.color.g == 130
        assert outer_shadow.color.b == 246
        assert outer_shadow.color.a == pytest.approx(0.15)

    def test_scaled_block_scales_text_and_decoration_metrics(
        self, decoration_pres
    ) -> None:
        slide = decoration_pres.slides[2]
        card = next(
            e
            for e in slide.elements
            if e.element_type == ElementType.DECORATED_BLOCK
            and any(
                "".join(run.text for run in p.runs) == "Scaled text"
                for p in e.paragraphs
            )
        )

        assert card.decoration is not None
        assert card.decoration.border_top.width_px == pytest.approx(2.5)
        assert card.decoration.border_radius_px == pytest.approx(10.0)
        assert card.decoration.padding.top_px == pytest.approx(12.5)
        assert card.decoration.padding.left_px == pytest.approx(25.0)
        run = card.paragraphs[0].runs[0]
        assert run.style.font_size_px == pytest.approx(25.0)
        assert card.paragraphs[0].line_height_px == pytest.approx(30.0)

    def test_complex_3d_transform_is_kept_on_native_route(
        self, decoration_pres
    ) -> None:
        slide = decoration_pres.slides[3]
        assert all(e.element_type != ElementType.UNSUPPORTED for e in slide.elements)
        floating = next(
            e for e in slide.elements if e.element_type == ElementType.DECORATED_BLOCK
        )
        assert floating.decoration is not None
        assert floating.box.width > 0
        assert floating.rotation_3d_x_deg == pytest.approx(4.0, abs=1.0)
        assert floating.rotation_3d_y_deg == pytest.approx(8.0, abs=1.0)
        assert len(floating.projected_corners) == 4

    def test_decorated_block_does_not_duplicate_container_background_as_run_highlight(
        self, decoration_pres
    ) -> None:
        slide = decoration_pres.slides[4]
        badge = next(
            e
            for e in slide.elements
            if e.element_type == ElementType.DECORATED_BLOCK
            and any(
                "".join(run.text for run in p.runs) == "Now in Public Beta"
                for p in e.paragraphs
            )
        )

        assert badge.decoration is not None
        assert badge.decoration.background_color is not None
        run = badge.paragraphs[0].runs[0]
        assert run.style.background_color is None

    def test_rounded_overflow_container_becomes_unsupported(
        self, decoration_pres
    ) -> None:
        slide = decoration_pres.slides[5]
        unsupported = next(
            e for e in slide.elements if e.element_type == ElementType.UNSUPPORTED
        )
        assert unsupported.unsupported_info is not None
        assert unsupported.unsupported_info.reason == "Overflow clipping container"

    def test_rounded_overflow_table_stays_native(self, decoration_pres) -> None:
        slide = decoration_pres.slides[6]
        assert any(e.element_type == ElementType.TABLE for e in slide.elements)
        assert all(e.element_type != ElementType.UNSUPPORTED for e in slide.elements)

    def test_inline_gradient_text_stays_native_run(self, gradient_pres) -> None:
        slide = gradient_pres.slides[0]

        paragraph = next(
            e for e in slide.elements if e.element_type == ElementType.PARAGRAPH
        )
        gradient_run = next(
            run for run in paragraph.paragraphs[0].runs if "gradient text" in run.text
        )
        assert gradient_run.style.text_gradient is not None
        assert "linear-gradient(" in gradient_run.style.text_gradient
        assert all(e.element_type != ElementType.UNSUPPORTED for e in slide.elements)

    def test_block_gradient_text_inside_decorated_block_stays_native(
        self, gradient_pres
    ) -> None:
        slide = gradient_pres.slides[1]

        card = next(
            e for e in slide.elements if e.element_type == ElementType.DECORATED_BLOCK
        )
        texts = ["".join(run.text for run in para.runs) for para in card.paragraphs]
        assert "2.4M" in texts[0]
        assert card.paragraphs[0].runs[0].style.text_gradient is not None
        assert any("Monthly Active Users" in text for text in texts)
        assert all(e.element_type != ElementType.UNSUPPORTED for e in slide.elements)

    def test_decorated_block_with_nested_decorated_child_decomposes(
        self, decomposition_pres
    ) -> None:
        slide = decomposition_pres.slides[0]

        decorated = [
            e for e in slide.elements if e.element_type == ElementType.DECORATED_BLOCK
        ]
        assert len(decorated) >= 2
        parent = max(decorated, key=lambda e: e.box.width * e.box.height)
        child = min(decorated, key=lambda e: e.box.width * e.box.height)
        assert parent.paragraphs == []
        assert child.decoration is not None
        assert child.decoration.background_color is not None
        assert "".join(run.text for p in child.paragraphs for run in p.runs) == "1"
        assert any(
            e.element_type == ElementType.PARAGRAPH
            and any("Upload" in run.text for p in e.paragraphs for run in p.runs)
            for e in slide.elements
        )

    def test_leaf_block_text_is_extracted_as_paragraph(self, decoration_pres) -> None:
        slide = decoration_pres.slides[11]

        paragraph = next(
            e for e in slide.elements if e.element_type == ElementType.PARAGRAPH
        )
        assert (
            "".join(run.text for p in paragraph.paragraphs for run in p.runs)
            == "Upload"
        )

    def test_flex_centered_decorated_text_sets_middle_vertical_align(
        self, decoration_pres
    ) -> None:
        slide = decoration_pres.slides[9]

        num = next(
            e for e in slide.elements if e.element_type == ElementType.DECORATED_BLOCK
        )
        assert num.vertical_align == "middle"
        assert num.paragraphs[0].alignment == "center"

    def test_flex_column_centered_child_blocks_inherit_center_alignment(
        self, decoration_pres
    ) -> None:
        slide = decoration_pres.slides[10]

        floating = next(
            e for e in slide.elements if e.element_type == ElementType.DECORATED_BLOCK
        )
        assert floating.vertical_align == "middle"
        assert ["".join(r.text for r in p.runs) for p in floating.paragraphs] == [
            "🤖",
            "AI Engine v3",
        ]
        assert all(paragraph.alignment == "center" for paragraph in floating.paragraphs)

    def test_decoration_only_leaf_block_is_extracted(self, decoration_pres) -> None:
        slide = decoration_pres.slides[8]
        bar = next(
            e for e in slide.elements if e.element_type == ElementType.DECORATED_BLOCK
        )
        assert bar.decoration is not None
        assert bar.decoration.background_gradient is not None
        assert bar.paragraphs == []

    def test_decorated_block_with_grandchild_decorated_blocks_decomposes(
        self, decomposition_pres
    ) -> None:
        slide = decomposition_pres.slides[1]

        decorated = [
            e for e in slide.elements if e.element_type == ElementType.DECORATED_BLOCK
        ]
        assert len(decorated) >= 3
        panel = max(decorated, key=lambda e: e.box.width * e.box.height)
        bars = [
            e
            for e in decorated
            if e is not panel and e.decoration and e.decoration.background_gradient
        ]
        assert panel.paragraphs == []
        assert len(bars) == 2
        assert all(bar.paragraphs == [] for bar in bars)
        assert any(
            e.element_type == ElementType.HEADING
            or (
                e.element_type == ElementType.PARAGRAPH
                and any(
                    "Revenue by Month" in run.text
                    for p in e.paragraphs
                    for run in p.runs
                )
            )
            for e in slide.elements
        )

    def test_presentational_list_recurses_into_children(
        self, decomposition_pres
    ) -> None:
        slide = decomposition_pres.slides[2]

        texts = [
            "".join(run.text for p in e.paragraphs for run in p.runs)
            for e in slide.elements
            if e.element_type == ElementType.PARAGRAPH
        ]
        assert "Conversion" in texts

    def test_presentational_list_rows_with_decoration_extract_as_blocks(
        self, decomposition_pres
    ) -> None:
        slide = decomposition_pres.slides[3]

        decorated = [
            e for e in slide.elements if e.element_type == ElementType.DECORATED_BLOCK
        ]
        panel = max(decorated, key=lambda e: e.box.width * e.box.height)
        rows = [
            e
            for e in decorated
            if e is not panel
            and e.decoration
            and e.decoration.border_bottom.width_px > 0
        ]

        assert panel.paragraphs == []
        assert len(rows) == 2
        assert all(row.paragraphs == [] for row in rows)

        headings = [
            "".join(run.text for p in e.paragraphs for run in p.runs)
            for e in slide.elements
            if e.element_type == ElementType.HEADING
        ]
        paragraphs = [
            "".join(run.text for p in e.paragraphs for run in p.runs)
            for e in slide.elements
            if e.element_type == ElementType.PARAGRAPH
        ]
        assert "Top Metrics" in headings
        assert "Conversion" in paragraphs
        assert "12.4%" in paragraphs
        assert "Bounce Rate" in paragraphs
        assert "23.1%" in paragraphs

    def test_backdrop_filter_block_stays_native(self, decoration_pres) -> None:
        slide = decoration_pres.slides[7]
        panel = next(
            e
            for e in slide.elements
            if e.element_type == ElementType.DECORATED_BLOCK
            and any(
                "".join(run.text for run in p.runs) == "Glass panel"
                for p in e.paragraphs
            )
        )
        assert panel.decoration is not None
        assert panel.decoration.background_color is not None
        assert all(e.element_type != ElementType.UNSUPPORTED for e in slide.elements)

    def test_slide_linear_gradient_background_is_extracted(self, gradient_pres) -> None:
        slide = gradient_pres.slides[2]

        assert slide.background.background_gradient is not None
        assert slide.background.background_gradient.startswith("linear-gradient(")

    def test_slide_radial_gradient_background_is_extracted(self, gradient_pres) -> None:
        slide = gradient_pres.slides[3]

        assert slide.background.background_gradient is not None
        assert slide.background.background_gradient.startswith("radial-gradient(")

    def test_decorated_badge_is_extracted_as_separate_element(
        self, decomposition_pres
    ) -> None:
        slide = decomposition_pres.slides[4]

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
        self, decomposition_pres
    ) -> None:
        slide = decomposition_pres.slides[5]

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
        self, decomposition_pres
    ) -> None:
        slide = decomposition_pres.slides[6]

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
        self, decomposition_pres
    ) -> None:
        slide = decomposition_pres.slides[7]
        images = [e for e in slide.elements if e.element_type == ElementType.IMAGE]

        assert len(images) == 1
        assert images[0].decoration is not None
        assert images[0].decoration.border_top.width_px > 0
        assert images[0].decoration.padding.left_px > 0

    def test_markdown_blockquote_extracts_decoration(self, inline_text_pres) -> None:
        slide = inline_text_pres.slides[7]
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
        self, inline_text_pres
    ) -> None:
        slide = inline_text_pres.slides[8]
        quotes = [e for e in slide.elements if e.element_type == ElementType.BLOCKQUOTE]

        assert len(quotes) == 2
        outer, inner = quotes
        assert outer.paragraphs == []
        assert len(inner.paragraphs) == 2
        assert "".join(run.text for run in inner.paragraphs[1].runs).startswith(
            "-- Jeff Atwood"
        )

    def test_blockquote_strikethrough_is_extracted(self, inline_text_pres) -> None:
        slide = inline_text_pres.slides[9]
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
        self, inline_text_pres
    ) -> None:
        slide = inline_text_pres.slides[10]
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
        self, multi_paragraph_pres
    ) -> None:
        pres = multi_paragraph_pres
        slide = pres.slides[0]
        paragraphs = [
            e for e in slide.elements if e.element_type == ElementType.PARAGRAPH
        ]
        assert len(paragraphs) == 1
        assert len(paragraphs[0].paragraphs) == 2


@pytest.fixture(scope="module")
def section_pseudo_html(session_output_dir: Path) -> Path:
    """Render section-pseudo-elements.md to HTML."""
    return render_to_html(
        FIXTURES_DIR / "section-pseudo-elements.md", output_dir=session_output_dir
    )


@pytest.fixture(scope="module")
def section_pseudo_pres(section_pseudo_html: Path):
    return extract_presentation_sync(section_pseudo_html)


@pytest.mark.integration
class TestSectionPseudoElements:
    """Tests for extracting CSS pseudo-elements (::before/::after) on section elements."""

    def test_pseudo_elements_extracted(self, section_pseudo_pres) -> None:
        """Section-level ::before/::after should appear as DECORATED_BLOCK elements."""
        pres = section_pseudo_pres
        slide = pres.slides[0]
        decorated = [
            e for e in slide.elements if e.element_type == ElementType.DECORATED_BLOCK
        ]
        # Both ::before and ::after pseudo-elements should be extracted
        assert len(decorated) >= 2, (
            f"Expected at least 2 decorated blocks for ::before/::after, "
            f"got {len(decorated)}. Element types: "
            f"{[e.element_type for e in slide.elements]}"
        )

    def test_pseudo_element_has_decoration(self, section_pseudo_pres) -> None:
        """Extracted pseudo-elements should carry decoration metadata."""
        pres = section_pseudo_pres
        slide = pres.slides[0]
        decorated = [
            e for e in slide.elements if e.element_type == ElementType.DECORATED_BLOCK
        ]
        # At least one should have a non-null decoration with background color
        decorated_with_bg = [
            e for e in decorated if e.decoration and e.decoration.background_color
        ]
        assert len(decorated_with_bg) >= 1, (
            "Expected at least one pseudo-element with background color decoration"
        )

    def test_pseudo_element_has_nonzero_dimensions(self, section_pseudo_pres) -> None:
        """Extracted pseudo-elements should have non-zero width and height."""
        pres = section_pseudo_pres
        slide = pres.slides[0]
        decorated = [
            e for e in slide.elements if e.element_type == ElementType.DECORATED_BLOCK
        ]
        for elem in decorated:
            assert elem.box.width > 0, "Pseudo-element width should be > 0"
            assert elem.box.height > 0, "Pseudo-element height should be > 0"


# ---------------------------------------------------------------------------
# Clip-path polygon extraction
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def clip_path_html(session_output_dir: Path) -> Path:
    """Render clip-path.md to HTML."""
    return render_to_html(FIXTURES_DIR / "clip-path.md", output_dir=session_output_dir)


@pytest.fixture(scope="module")
def clip_path_pres(clip_path_html: Path):
    """Extract presentation from clip-path fixture."""
    return extract_presentation_sync(clip_path_html)


@pytest.mark.integration
class TestClipPathPolygon:
    """Tests for CSS clip-path: polygon(...) extraction."""

    def test_clip_path_polygon_extracted(self, clip_path_pres) -> None:
        """At least one element should have a clip_path with type='polygon'."""
        pres = clip_path_pres
        slide = pres.slides[0]
        clipped = [e for e in slide.elements if e.decoration and e.decoration.clip_path]
        assert len(clipped) >= 1, (
            "Expected at least one element with clip_path decoration"
        )
        for elem in clipped:
            assert elem.decoration.clip_path.type == "polygon"

    def test_clip_path_polygon_points(self, clip_path_pres) -> None:
        """Triangle polygon should have exactly 3 points."""
        pres = clip_path_pres
        slide = pres.slides[0]
        clipped = [e for e in slide.elements if e.decoration and e.decoration.clip_path]
        assert len(clipped) >= 1
        cp = clipped[0].decoration.clip_path
        assert len(cp.points) == 3, (
            f"Expected 3 points for triangle polygon, got {len(cp.points)}"
        )


@pytest.mark.integration
class TestCssFilterThreshold:
    """Tests for CSS filter threshold-based detection.

    Minor visual adjustments (e.g. brightness(1.02)) should be treated as
    negligible and NOT trigger fallback to screenshot images.
    """

    def test_negligible_filter_stays_native(
        self, tmp_path: Path, tmp_output_dir: Path
    ) -> None:
        """brightness(1.02) saturate(1.1) are within thresholds – no fallback."""
        md_path = tmp_path / "negligible-filter.md"
        md_path.write_text(
            """---
marp: true
style: |
  .subtle {
    filter: brightness(1.02) saturate(1.1);
    padding: 24px;
  }
---

# Slide

<div class="subtle">Subtle adjustment</div>
""",
            encoding="utf-8",
        )
        html_path = render_to_html(md_path, output_dir=tmp_output_dir)
        pres = extract_presentation_sync(html_path)
        slide = pres.slides[0]
        unsupported = [
            e for e in slide.elements if e.element_type == ElementType.UNSUPPORTED
        ]
        assert len(unsupported) == 0, (
            "Negligible CSS filter should NOT trigger fallback"
        )

    def test_significant_blur_triggers_fallback(
        self, tmp_path: Path, tmp_output_dir: Path
    ) -> None:
        """blur(5px) should always trigger fallback."""
        md_path = tmp_path / "blur-filter.md"
        md_path.write_text(
            """---
marp: true
style: |
  .blurred {
    filter: blur(5px);
    padding: 24px;
  }
---

# Slide

<div class="blurred">Blurred text</div>
""",
            encoding="utf-8",
        )
        html_path = render_to_html(md_path, output_dir=tmp_output_dir)
        pres = extract_presentation_sync(html_path)
        slide = pres.slides[0]
        unsupported = [
            e for e in slide.elements if e.element_type == ElementType.UNSUPPORTED
        ]
        assert len(unsupported) >= 1, "blur(5px) should trigger fallback"

    def test_mixed_negligible_and_significant_triggers_fallback(
        self, tmp_path: Path, tmp_output_dir: Path
    ) -> None:
        """brightness(1.02) + blur(3px) – one significant filter forces fallback."""
        md_path = tmp_path / "mixed-filter.md"
        md_path.write_text(
            """---
marp: true
style: |
  .mixed {
    filter: brightness(1.02) blur(3px);
    padding: 24px;
  }
---

# Slide

<div class="mixed">Mixed filters</div>
""",
            encoding="utf-8",
        )
        html_path = render_to_html(md_path, output_dir=tmp_output_dir)
        pres = extract_presentation_sync(html_path)
        slide = pres.slides[0]
        unsupported = [
            e for e in slide.elements if e.element_type == ElementType.UNSUPPORTED
        ]
        assert len(unsupported) >= 1, (
            "Mixed negligible + significant filter should trigger fallback"
        )


class TestVisualLineBreaks:
    """Tests for visual line break detection in headings and paragraphs."""

    @pytest.mark.integration
    def test_heading_visual_line_break_detected(
        self, tmp_path: Path, tmp_output_dir: Path
    ) -> None:
        """A long heading with large font should wrap and produce a visual line break."""
        md_path = tmp_path / "visual-line-break.md"
        md_path.write_text(
            """---
marp: true
style: |
  h1 { font-size: 100px; }
---

# AAAA BBBB CCCC DDDD
""",
            encoding="utf-8",
        )
        html_path = render_to_html(md_path, output_dir=tmp_output_dir)
        pres = extract_presentation_sync(html_path)
        slide = pres.slides[0]
        headings = [e for e in slide.elements if e.element_type == ElementType.HEADING]
        assert len(headings) >= 1, "Should have at least one heading element"
        heading = headings[0]
        full_text = "".join(
            run.text for para in heading.paragraphs for run in para.runs
        )
        assert "\n" in full_text, (
            f"Expected visual line break in wrapped heading, got: {full_text!r}"
        )

    @pytest.mark.integration
    def test_short_heading_no_false_line_break(
        self, tmp_path: Path, tmp_output_dir: Path
    ) -> None:
        """A short heading that fits on one line should NOT have a line break."""
        md_path = tmp_path / "no-line-break.md"
        md_path.write_text(
            """---
marp: true
---

# Hello
""",
            encoding="utf-8",
        )
        html_path = render_to_html(md_path, output_dir=tmp_output_dir)
        pres = extract_presentation_sync(html_path)
        slide = pres.slides[0]
        headings = [e for e in slide.elements if e.element_type == ElementType.HEADING]
        assert len(headings) >= 1, "Should have at least one heading element"
        heading = headings[0]
        full_text = "".join(
            run.text for para in heading.paragraphs for run in para.runs
        )
        assert "\n" not in full_text, (
            f"Short heading should not contain line breaks, got: {full_text!r}"
        )

    @pytest.mark.integration
    def test_br_tag_not_duplicated(self, tmp_path: Path, tmp_output_dir: Path) -> None:
        """An explicit <br> tag should produce exactly one line break, not two."""
        md_path = tmp_path / "br-tag.md"
        md_path.write_text(
            """---
marp: true
---

<p>Line one<br/>Line two</p>
""",
            encoding="utf-8",
        )
        html_path = render_to_html(md_path, output_dir=tmp_output_dir)
        pres = extract_presentation_sync(html_path)
        slide = pres.slides[0]
        paragraphs = [
            e for e in slide.elements if e.element_type == ElementType.PARAGRAPH
        ]
        assert len(paragraphs) >= 1, "Should have at least one paragraph element"
        para_elem = paragraphs[0]
        full_text = "".join(
            run.text for para in para_elem.paragraphs for run in para.runs
        )
        newline_count = full_text.count("\n")
        assert newline_count == 1, (
            f"Expected exactly 1 line break between 'Line one' and 'Line two', "
            f"got {newline_count} in: {full_text!r}"
        )
