# Background Images Feasibility Report

## 1. Marp Background Image Syntax

Marp supports the following background directives:

| Syntax | Effect |
|--------|--------|
| `![bg](url)` | Full-slide background image, cover mode (default) |
| `![bg cover](url)` | Explicit cover mode (same as default) |
| `![bg contain](url)` | Image fits within slide, preserving aspect ratio |
| `![bg fit](url)` | Alias for contain |
| `![bg left](url)` | Image on left 50%, content on right 50% |
| `![bg right](url)` | Image on right 50%, content on left 50% |
| `<!-- backgroundColor: #hex -->` | Solid color background via directive |
| `<!-- _backgroundColor: value -->` | Scoped (single-slide) background color |

## 2. How Marp Represents Backgrounds in HTML/DOM

Marp-cli (v4.2.3 with marp-core v4.3.0) uses a **three-section architecture** for slides with background images:

### Standard slide (solid color only)
```html
<section id="1" data-background-color="#336699"
    style="--background-color:#336699;background-color:#336699;background-image:none;">
  <h1>Solid Background</h1>
</section>
```
- `data-background-color` attribute holds the color value
- Inline styles set both `background-color` and a CSS variable `--background-color`
- `background-image:none` is explicitly set

### Background image slide (three sibling sections)
For each slide with `![bg]`, Marp emits **three sibling `<section>` elements**:

1. **Background section** (`data-marpit-advanced-background="background"`):
   - Contains a `<div data-marpit-advanced-background-container="true">` with `<figure>` children
   - Each `<figure>` has `style="background-image:url(...)"` and optional `background-size:contain`

2. **Content section** (`data-marpit-advanced-background="content"`):
   - Contains the actual slide text/markup (headings, paragraphs, etc.)
   - Has the same `id` attribute as the logical slide number

3. **Pseudo section** (`data-marpit-advanced-background="pseudo"`):
   - Empty section for CSS pseudo-element styling

### Split background slide
```html
<section ... data-marpit-advanced-background="background"
    data-marpit-advanced-background-split="left"
    style="...--marpit-advanced-background-split:50%;">
  <div data-marpit-advanced-background-container="true"
       data-marpit-advanced-background-direction="horizontal">
    <figure style="background-image:url(...)"></figure>
  </div>
</section>
```
- `data-marpit-advanced-background-split="left"` indicates split direction
- CSS variable `--marpit-advanced-background-split:50%` controls split ratio

### Contain mode
```html
<figure style="background-image:url(...);background-size:contain;"></figure>
```
- Simply adds `background-size:contain` to the figure's inline style

### Gradient / CSS backgrounds
```html
<section data-background-color="linear-gradient(to right, #ff0000, #0000ff)"
    style="--background-color:linear-gradient(to right, #ff0000, #0000ff);
           background-color:linear-gradient(to right, #ff0000, #0000ff);
           background-image:none;">
```
- Gradient is set as the `background-color` value (which is invalid CSS for `background-color` but Marp handles it)
- No three-section architecture; treated as a simple color directive

## 3. python-pptx Background Capabilities

### Tested Approaches

| Approach | Method | Result |
|----------|--------|--------|
| **Solid color** | `slide.background.fill.solid()` + `fore_color.rgb` | **Native API, works perfectly** |
| **Image bg (XML)** | `slide.part.get_or_add_image_part()` + XML `p:bgPr/a:blipFill` | **Works, requires XML manipulation** |
| **Image bg (picture shape)** | `slide.shapes.add_picture()` + z-order via `spTree.insert(2, ...)` | **Works, simpler API** |
| **Split bg** | Half-width `add_picture()` + z-order management | **Works** |
| **Contain bg** | Aspect-ratio calculation + centered `add_picture()` | **Works (needs Pillow or manual calc)** |

### Key Technical Details

**Approach 1 - XML Background Fill:**
- `slide.part.get_or_add_image_part(path)` returns `(ImagePart, rId)` -- the rId is immediately usable
- Do NOT call `slide.part.relate_to()` separately; it creates a broken relationship causing `AssertionError`
- Must clear existing `bg` children before appending `p:bgPr`
- Must include `a:effectLst` element for schema compliance
- Produces a true OOXML slide background (no shape in spTree)

**Approach 2 - Picture Shape:**
- `slide.shapes.add_picture()` adds the image as a normal shape
- Z-ordering: remove from spTree and re-insert at index 2 (after `nvGrpSpPr` and `grpSpPr`)
- More flexible for split backgrounds and contain mode
- Image is a shape, not a true background (selectable in PowerPoint)

## 4. Feasibility Assessment

| Background Type | Feasibility | Recommended Approach |
|----------------|-------------|---------------------|
| **Solid color** (`backgroundColor`) | **Native** | `slide.background.fill.solid()` |
| **Background image** (`![bg]`) | **Native** | Approach 2 (picture shape) -- simpler, more flexible |
| **Background cover** (`![bg cover]`) | **Native** | Full-slide picture shape stretched to slide dimensions |
| **Background contain** (`![bg contain]`) | **Native** | Aspect-ratio-preserving picture shape, centered |
| **Split left/right** (`![bg left]`) | **Native** | Half-width picture shape + offset content |
| **CSS gradient** | **Fallback** | Parse first/last color from gradient string, use solid fill |
| **Multiple bg images** | **Partial** | Stack multiple picture shapes with z-ordering |

## 5. Recommended Implementation Strategy

1. **Use Approach 2 (picture shapes) as the primary method** for background images:
   - Simpler API (no XML manipulation needed)
   - Naturally supports cover, contain, and split via positioning/sizing
   - Z-order management is straightforward via `spTree.insert(2, ...)`

2. **Use native `slide.background.fill` for solid colors** -- no reason to use shapes for this.

3. **Parsing strategy from Marp HTML:**
   - For each logical slide, check for `data-marpit-advanced-background="background"` sibling sections
   - Extract image URLs from `<figure style="background-image:url(...)">` elements
   - Detect `background-size:contain` in the figure's inline style
   - Detect split direction from `data-marpit-advanced-background-split` attribute
   - For simple slides, read `data-background-color` attribute on the section

4. **Gradient fallback:** Parse `linear-gradient(...)` to extract color stops, use the first color as a solid fill. Log a warning that gradients are not fully supported.

## 6. Files Created

- `tests/fixtures/bg-image.md` -- Test fixture with all background types
- `docs/spikes/bg_image_spike.py` -- Executable spike testing all approaches
- Generated HTML at `/tmp/marp_bg_test.html` (temporary)
- Generated PPTX files at `/tmp/bg_spike_output/` (temporary)
