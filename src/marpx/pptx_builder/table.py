"""Table rendering functions for pptx_builder."""
from __future__ import annotations

from pptx.util import Emu

from marpx.models import SlideElement, TableCell
from marpx.utils import px_to_emu

from ._helpers import _to_rgb
from .text import _add_paragraph_runs


def _set_cell_content(pptx_cell, cell: TableCell) -> None:
    """Set content and styling on a PPTX table cell."""
    tf = pptx_cell.text_frame
    for p_idx, para in enumerate(cell.paragraphs):
        if p_idx == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        _add_paragraph_runs(p, para.runs)

    if cell.background:
        fill = pptx_cell.fill
        fill.solid()
        fill.fore_color.rgb = _to_rgb(cell.background)


def _add_table(slide, element: SlideElement) -> None:
    """Add a table to the slide, handling colspan and rowspan merges."""
    if not element.table_rows:
        return

    num_rows = len(element.table_rows)

    # Step 1: Calculate true grid column count by summing colspans per row
    num_cols = 0
    for row in element.table_rows:
        row_cols = sum(cell.colspan for cell in row.cells)
        num_cols = max(num_cols, row_cols)

    if num_cols == 0:
        return

    # Step 2: Create the table shape
    left = Emu(px_to_emu(element.box.x))
    top = Emu(px_to_emu(element.box.y))
    width = Emu(px_to_emu(element.box.width))
    height = Emu(px_to_emu(element.box.height))

    table_shape = slide.shapes.add_table(num_rows, num_cols, left, top, width, height)
    table = table_shape.table

    column_widths_px = [0.0] * num_cols

    # Step 3: Build occupancy map and place cells
    occupied: list[list[bool]] = [
        [False] * num_cols for _ in range(num_rows)
    ]

    # Track merge operations to apply after placement
    merges: list[tuple[int, int, int, int, TableCell]] = []

    for r_idx, row in enumerate(element.table_rows):
        col_cursor = 0
        for cell in row.cells:
            # Find next unoccupied column
            while col_cursor < num_cols and occupied[r_idx][col_cursor]:
                col_cursor += 1

            if col_cursor >= num_cols:
                break

            c_idx = col_cursor

            # Mark occupied cells for this cell's span
            for dr in range(cell.rowspan):
                for dc in range(cell.colspan):
                    if r_idx + dr < num_rows and c_idx + dc < num_cols:
                        occupied[r_idx + dr][c_idx + dc] = True

            # Record merge if needed, otherwise set content directly
            if cell.width_px:
                per_col_width = cell.width_px / max(cell.colspan, 1)
                for dc in range(cell.colspan):
                    if c_idx + dc < num_cols:
                        column_widths_px[c_idx + dc] = max(
                            column_widths_px[c_idx + dc],
                            per_col_width,
                        )

            if cell.rowspan > 1 or cell.colspan > 1:
                merges.append((r_idx, c_idx, cell.rowspan, cell.colspan, cell))
            else:
                _set_cell_content(table.cell(r_idx, c_idx), cell)

            col_cursor = c_idx + cell.colspan

    # Step 4: Apply merges and set content AFTER merging
    for r, c, rowspan, colspan, cell_data in merges:
        end_r = min(r + rowspan - 1, num_rows - 1)
        end_c = min(c + colspan - 1, num_cols - 1)
        if end_r > r or end_c > c:
            table.cell(r, c).merge(table.cell(end_r, end_c))
        _set_cell_content(table.cell(r, c), cell_data)

    if any(width_px > 0 for width_px in column_widths_px):
        total_width_px = sum(width_px for width_px in column_widths_px if width_px > 0)
        if total_width_px > 0:
            for idx, width_px in enumerate(column_widths_px):
                if width_px > 0:
                    table.columns[idx].width = Emu(px_to_emu(width_px))
