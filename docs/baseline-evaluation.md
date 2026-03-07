# Marp CLI PPTX Baseline Evaluation

**Date:** 2026-03-06
**Marp CLI version:** Latest via npx @marp-team/marp-cli
**Test input:** 2-slide Markdown with heading, bullet list, and table

## Summary

Marp CLI supports two PPTX output modes:

1. **Standard (`--pptx`)** -- Renders each slide as a PNG image embedded in the PPTX. No editable text, no editable shapes. Each slide is a single raster image.
2. **Editable (`--pptx --pptx-editable`)** -- Experimental feature that uses LibreOffice under the hood. Produces editable text boxes and freeform vector shapes.

## Standard Mode (`--pptx`)

- Each slide contains **zero shapes** visible to python-pptx (content is a background image)
- Slide images stored as `ppt/media/Slide-N-image-1.png`
- **Text is NOT editable** -- it is baked into raster images
- Tables, lists, headings are all rasterized

**Verdict:** Unusable for editable PPTX output.

## Editable Mode (`--pptx --pptx-editable`)

- Text IS editable via `TEXT_BOX` shapes with correct text content
- Formatting is preserved: font sizes, bold, colors (e.g., heading: 441960 EMU / ~34pt, bold, color #224466)
- Layout positions are reasonable (e.g., heading at ~0.82in from left, ~2.76in from top)

### Limitations

| Issue | Detail |
|-------|--------|
| **Tables are not native** | Tables are rendered as separate text boxes + freeform rectangle shapes, NOT native PPTX `<a:tbl>` elements. Each cell is an independent text box. |
| **Excessive freeform shapes** | Slide 2 (with a 2x2 table) produced 19 freeform shapes + 5 text boxes = 24 total shapes. Background and decorative elements are vector paths. |
| **LibreOffice dependency** | Requires LibreOffice (`soffice`) installed. The conversion pipeline is Marp -> HTML -> PDF -> PPTX via LibreOffice. |
| **Experimental warning** | Marp itself warns: "The output depends on LibreOffice and slide reproducibility is not fully guaranteed." |
| **No semantic structure** | Bullet lists lose their list semantics -- items become independent text boxes without bullet markers managed by PowerPoint. |
| **No native table support** | Cannot resize columns/rows, add/remove cells, or use PowerPoint's table styling features. |

### Shape Breakdown (Editable Mode)

**Slide 1** (heading + 2 bullets): 5 freeform shapes + 3 text boxes
**Slide 2** (heading + 2x2 table): 19 freeform shapes + 5 text boxes

## Conclusion

| Question | Answer |
|----------|--------|
| Does marp-cli produce editable text in PPTX? | **Yes**, with `--pptx-editable` (experimental). Text boxes are editable. |
| Does it preserve layout/formatting adequately? | **Partially.** Positions and font styles are preserved, but tables and lists lose their native PowerPoint structure. |
| Is custom implementation justified? | **Yes.** The editable mode has significant limitations: no native tables, no native lists, excessive shape count, LibreOffice dependency, and experimental status. A custom implementation can produce semantically correct PowerPoint elements (native tables, bulleted lists, proper slide layouts) that are fully editable and maintainable. |
