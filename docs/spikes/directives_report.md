# Marp Directives Feasibility Report

**Date:** 2026-03-06
**Scope:** paginate, header, footer, size directives

---

## 1. How Marp Renders Directives in the DOM

### Section Element Attributes

Each slide is rendered as a `<section>` inside an `<svg data-marpit-svg="" viewBox="0 0 1280 720">` / `<foreignObject>` wrapper. Directives appear as **data attributes** and **CSS custom properties** on the `<section>` element:

```html
<section id="1"
  data-paginate="true"
  data-header="My Presentation"
  data-footer="(c) 2026 Example Corp"
  data-marpit-pagination="1"
  data-marpit-pagination-total="4"
  data-size="16:9"
  style="--paginate:true;--header:My Presentation;--footer:(c) 2026 Example Corp;"
  lang="C">
```

### Header Element
Rendered as a child `<header>` HTML element inside the section:
```html
<header>My Presentation</header>
```

### Footer Element
Rendered as a child `<footer>` HTML element inside the section:
```html
<footer>(c) 2026 Example Corp</footer>
```

### Pagination (Page Number)
Rendered via CSS `::after` pseudo-element on the section. The content is driven by `data-marpit-pagination` attribute. The CSS rule is:
```css
section:after {
  bottom: 21px;
  color: var(--paginate-color);
  font-size: 24px;
  position: absolute;
  right: 30px;
}
```
The actual page number text comes from `data-marpit-pagination` (value: "1", "2", etc.) and `data-marpit-pagination-total` (value: "4").

### Size Directive
The SVG `viewBox` is set to `0 0 1280 720` for 16:9. The section CSS also explicitly sets `width: 1280px; height: 720px`. The `data-size="16:9"` attribute is also present.

### Per-Slide Directive Overrides

When `_paginate: false`, `_header: ""`, `_footer: ""` are used:
- The `data-paginate`, `data-header`, `data-footer` attributes are **removed entirely** from that section
- The `<header>` and `<footer>` child elements are **not rendered**
- The `data-marpit-pagination` attribute is **not present** (so no page number)

When `_header: "Custom Header"` is used:
- `data-header="Custom Header"` replaces the global value
- `<header>Custom Header</header>` element contains the override text

---

## 2. Extraction Strategy

### Recommended: DOM Observation (HTML parsing with BeautifulSoup)

For each `<section>` element, extract:

| Directive | Extraction Method |
|-----------|------------------|
| `paginate` | Check `data-paginate` attribute exists and equals `"true"` |
| Page number | Read `data-marpit-pagination` attribute value |
| Total pages | Read `data-marpit-pagination-total` attribute value |
| Header text | Read `<header>` child element text content |
| Footer text | Read `<footer>` child element text content |
| Size | Read `data-size` attribute, or parse SVG `viewBox` (1280x720 = 16:9, 960x720 = 4:3) |

**Why DOM over Markdown parsing:**
- DOM reflects the *resolved* state after all directive inheritance and overrides
- No need to implement Marp's directive scoping/cascading logic
- Handles per-slide overrides (`_directive`) automatically
- Handles edge cases like empty strings overriding global values

---

## 3. python-pptx Capabilities for Directives

### Slide Dimensions (size directive)

**Feasibility: NATIVE**

```python
from pptx.util import Emu
prs.slide_width = Emu(12192000)   # 16:9 (13.33 x 7.50 inches)
prs.slide_height = Emu(6858000)
```

Size mapping:
| Marp size | SVG viewBox | PPTX EMU (width x height) |
|-----------|------------|---------------------------|
| 16:9 | 1280 x 720 | 12192000 x 6858000 |
| 4:3 | 960 x 720 | 9144000 x 6858000 |

### Footer (footer directive)

**Feasibility: NATIVE**

All default slide layouts (0-10) include a Footer placeholder (idx=11, type=FOOTER). This is a native PPTX feature. The footer text can be set via the placeholder's text_frame.

**Alternative:** Text box at bottom-left, positioned at (0, slide_height - 457200) with full width.

### Slide Number (paginate directive)

**Feasibility: NATIVE**

All default slide layouts (0-10) include a Slide Number placeholder (idx=12, type=SLIDE_NUMBER). This auto-increments natively in PowerPoint.

Additionally, a slide number field can be inserted via XML:
```xml
<a:fld id="{...}" type="slidenum">
  <a:rPr lang="en-US" sz="1000"/>
  <a:t>&lt;#&gt;</a:t>
</a:fld>
```

**Per-slide suppression:** When `_paginate: false`, simply do not add the slide number placeholder/textbox for that slide.

### Header (header directive)

**Feasibility: PARTIAL (textbox fallback)**

There is **no native "header" placeholder** in the default PPTX template. The placeholder indices found are:
- idx=10: DATE
- idx=11: FOOTER
- idx=12: SLIDE_NUMBER

Headers must be implemented as positioned text boxes at the top of the slide. Marp's CSS positions the header at `top: 21px; left: 30px`.

### Date Placeholder

**Feasibility: NATIVE (bonus)**

All layouts include a Date placeholder (idx=10, type=DATE). Not directly used by Marp but available.

---

## 4. Feasibility Summary

| Directive | Feasibility | Implementation Strategy |
|-----------|-------------|------------------------|
| `size` | **NATIVE** | Set `prs.slide_width` / `prs.slide_height` based on `data-size` or SVG viewBox |
| `footer` | **NATIVE** | Use layout Footer placeholder (idx=11) OR positioned text box |
| `paginate` | **NATIVE** | Use layout Slide Number placeholder (idx=12) with `<a:fld type="slidenum">` |
| `header` | **PARTIAL** | No native header placeholder; use positioned text box at top of slide |
| `_paginate: false` | **NATIVE** | Omit slide number shape for that slide |
| `_header: ""` | **NATIVE** | Omit header text box for that slide |
| `_footer: ""` | **NATIVE** | Omit footer shape for that slide |
| `_header: "Custom"` | **NATIVE** | Set different text in header text box for that slide |

### Key Findings

1. **Footer and slide number have first-class PPTX support** through layout placeholders present in every default layout. Using these gives native PowerPoint behavior (e.g., slide numbers auto-update when slides are reordered).

2. **Header requires a text box workaround** since PPTX has no native header placeholder concept. This is straightforward but means the header is a static shape rather than a managed placeholder.

3. **Per-slide overrides are simple to implement** because the DOM already resolves which slides have which directives. The converter just checks for attribute presence/absence per section.

4. **Size is trivially mapped** from Marp's 1280x720 (16:9) or 960x720 (4:3) viewBox to PPTX EMU dimensions.

---

## 5. Recommended Architecture

```
HTML section element
    |
    +-- data-size         --> prs.slide_width / prs.slide_height (once, globally)
    +-- data-paginate     --> if present: add slide number placeholder (idx=12) or fld element
    +-- data-header       --> if present: add positioned text box at top
    +-- <header> text     --> text content for header text box
    +-- data-footer       --> if present: add footer placeholder (idx=11) or text box at bottom
    +-- <footer> text     --> text content for footer text box / placeholder
    +-- data-marpit-pagination --> page number value (for static fallback if needed)
    +-- data-marpit-pagination-total --> total pages (for "X / Y" format if needed)
```

### Open Questions for Implementation

1. **Placeholder vs text box for footer/slide-number:** Using native placeholders gives better PowerPoint integration (auto-update, theme-aware) but requires careful layout selection. Text boxes are simpler and give pixel-perfect control. Recommend: **text boxes for header, native placeholders for footer and slide number if using a layout that has them, text box fallback otherwise.**

2. **Styling consistency:** Marp renders header/footer with `font-size: 18px; color: hsla(0,0%,40%,.75); left: 30px`. These need to be mapped to equivalent PPTX styling (Pt sizes, RGBColor values, EMU positioning).

3. **Pagination format:** Marp shows just the page number. PPTX native slide number also shows just the number. If "X / Y" format is desired, a custom text box with both fields would be needed.
