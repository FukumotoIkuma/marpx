# Research Report: Advanced Tables (rowspan/colspan merge) Feasibility

**Date:** 2026-03-06
**Phase:** 0 Discovery
**Status:** Research Complete

---

## 1. How Marp Renders HTML Tables with Merge Attributes

Marp preserves `colspan` and `rowspan` attributes **as-is** in the rendered HTML output. The HTML table from the fixture:

```html
<th colspan="2">Header spanning 2 cols</th>
<td rowspan="2">Spans 2 rows</td>
```

appears identically in the Marp HTML output (confirmed by parsing `/tmp/marp_table_test.html`). Marp does not transform or flatten these attributes. Standard Markdown tables (pipe syntax) render as normal `<table>` without any merge attributes.

**Key finding:** The extractor's JavaScript `extractTable()` function already reads `td.colSpan` and `td.rowSpan` from the DOM and includes them in extraction output. No changes needed in the JS extraction code.

## 2. python-pptx Merge API Capabilities and Limitations

### API

```python
table.cell(start_row, start_col).merge(table.cell(end_row, end_col))
```

### Test Results (ALL PASSED)

| Test Case | Description | Result |
|-----------|-------------|--------|
| basic_colspan | Horizontal merge (0,0)-(0,1) | PASS |
| basic_rowspan | Vertical merge (1,0)-(2,0) | PASS |
| combined_merge | Both colspan and rowspan in same table | PASS |
| block_merge | 2x2 rectangular block merge | PASS |
| full_row_merge | Merge entire row across all columns | PASS |
| adjacent_merges | Two side-by-side colspan merges in same row | PASS |
| text_formatting_in_merged | Bold, color, font size, cell fill in merged cell | PASS |

### XML Representation (verified)

python-pptx uses OOXML merge attributes:
- **`gridSpan=N`** on the origin cell for horizontal merges (colspan)
- **`rowSpan=N`** on the origin cell for vertical merges (rowspan)
- **`hMerge=1`** on continuation cells (horizontal)
- **`vMerge=1`** on continuation cells (vertical)

### Limitations Discovered

1. **Table must be created with full grid dimensions first** -- you must pre-calculate the actual column count (accounting for colspans) and actual row count before creating the table shape.
2. **Text on continuation cells is ignored** -- only the origin cell's text is visible after merge.
3. **No "unmerge" API** -- merges are one-way.
4. **Overlapping merges** -- python-pptx does not raise errors for overlapping merges but the behavior is undefined in PowerPoint. Must be avoided.

## 3. Current Codebase Analysis

### Extractor (`src/marp_to_pptx/extractor.py`)

- **Already captures `colspan` and `rowspan`** in the JS `extractTable()` function (lines 171-178).
- **Already builds `TableCell` model** with `colspan` and `rowspan` fields (lines 431-434).
- **No changes needed** in the extractor.

### Models (`src/marp_to_pptx/models.py`)

- `TableCell` already has `colspan: int = 1` and `rowspan: int = 1` fields.
- **No changes needed** in the models.

### Builder (`src/marp_to_pptx/pptx_builder.py`)

The `_add_table()` function (line 174) has **two critical gaps**:

#### Gap 1: Column count calculation is wrong for merged tables

```python
# Current (WRONG for merged tables):
cols = max(len(row.cells) for row in element.table_rows)
```

When a row has `<th colspan="2">` + `<th>`, it has 2 cells in the DOM but represents 3 columns. The column count must account for colspans:

```python
# Correct:
cols = max(sum(cell.colspan for cell in row.cells) for row in element.table_rows)
```

#### Gap 2: No merge calls

The current code iterates `(r_idx, c_idx)` assuming 1:1 mapping between cell index and grid position. With merged tables, the column index must be offset by preceding colspans. After placing text, `table.cell().merge()` must be called.

#### Gap 3: Row count may be wrong for rowspan tables

Rows with rowspan reduce the number of `<td>` elements in subsequent rows. The row count from `len(element.table_rows)` is correct (each `<tr>` is a row), but the cell-to-grid mapping must track which grid positions are occupied by rowspans from previous rows.

### Required Changes (builder only)

1. **Calculate true grid dimensions**: Walk all rows, summing colspans per row for true column count. Row count = number of `<tr>` elements (already correct).

2. **Build a grid occupancy map**: Track which `(row, col)` positions are occupied by rowspans from prior rows.

3. **Map DOM cells to grid positions**: For each row, place cells into the next available grid column (skipping cells occupied by rowspans).

4. **Apply merges after text placement**: Call `table.cell(r, c).merge(table.cell(r + rowspan - 1, c + colspan - 1))` for any cell with colspan > 1 or rowspan > 1.

## 4. Feasibility Assessment

**Feasibility: NATIVE**

- The extractor and models already support colspan/rowspan -- no changes needed.
- python-pptx's merge API handles all tested scenarios correctly.
- Only the `_add_table()` function in `pptx_builder.py` needs modification.
- The implementation is a grid-mapping algorithm (well-understood, no external dependencies).

### Estimated complexity

- **Lines of code changed:** ~40-60 lines in `_add_table()` function
- **Risk:** Low -- the merge API is stable and well-tested
- **Dependencies:** None new

## 5. Edge Cases to Handle

| Edge Case | Risk | Mitigation |
|-----------|------|------------|
| Overlapping merges (colspan and rowspan compete for same cell) | Medium | Grid occupancy map prevents double-assignment |
| colspan/rowspan exceeding table bounds | Low | Clamp to actual grid dimensions |
| Empty merged cells (continuation cells have no text) | None | python-pptx handles this natively |
| Nested tables (table inside a merged cell) | Low | Not supported by Marp markdown; HTML tables could theoretically nest but extremely rare |
| Mixed HTML + Markdown tables on same slide | None | Each table is extracted independently |
| colspan=1 / rowspan=1 (no-op values) | None | Skip merge call when both are 1 |

## 6. Files Created

- **Test fixture:** `tests/fixtures/merged-table.md`
- **Spike script:** `docs/spikes/table_merge_spike.py` (all 7 tests PASS)
- **Generated PPTX files:** `/tmp/table_merge_*.pptx` (7 files for manual verification)
- **Generated HTML:** `/tmp/marp_table_test.html`
