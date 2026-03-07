---
marp: true
theme: default
size: 16:9
paginate: true
header: marpx デモ
footer: github.com/FukumotoIkuma/marpx
style: |
  section {
    font-family: 'Hiragino Sans', 'Yu Gothic', sans-serif;
    font-size: 22px;
    color: #1f2937;
    background: #fbfbfd;
    padding: 56px 72px;
  }
  h1, h2, h3 {
    color: #0f172a;
  }
  a {
    color: #0f62fe;
  }
  code {
    background: #e8edf5;
    border-radius: 6px;
    padding: 0.1em 0.3em;
  }
  pre code {
    background: transparent;
    padding: 0;
  }
  .lead {
    background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 100%);
    color: #eff6ff;
  }
  .lead h1, .lead h2, .lead h3, .lead p, .lead li {
    color: #eff6ff;
  }
  .lead .muted {
    color: #cbd5e1;
  }
  .grid-2 {
    display: flex;
    gap: 28px;
    align-items: flex-start;
  }
  .grid-2 > div {
    flex: 1;
    min-width: 0;
  }
  .grid-3 {
    display: flex;
    gap: 18px;
    align-items: stretch;
  }
  .grid-3 > div {
    flex: 1;
    min-width: 0;
  }
  .card {
    background: #eef4ff;
    border: 1px solid #bfd3ff;
    border-radius: 16px;
    padding: 18px 20px;
  }
  .quote-box {
    background: #f8f4ff;
    border-left: 6px solid #6d28d9;
    border-radius: 14px;
    color: #312e81;
    padding: 18px 22px;
    margin: 10px 0;
  }
  .panel {
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 14px;
    padding: 14px 18px;
  }
  .swatch {
    border-radius: 12px;
    color: white;
    font-weight: 700;
    padding: 18px 16px;
    min-height: 84px;
  }
  .mono {
    font-family: 'Courier New', monospace;
  }
  .serif {
    font-family: 'Times New Roman', serif;
  }
  .tiny {
    font-size: 0.72em;
    color: #475569;
  }
  .center {
    text-align: center;
  }
  .right {
    text-align: right;
  }
  .kpi {
    font-size: 1.8em;
    font-weight: 700;
    line-height: 1.1;
    color: #0f172a;
  }
  .checklist {
    list-style: none;
    padding-left: 0;
    margin: 0.4em 0;
  }
  .checklist li {
    margin: 0.18em 0;
  }
  .checklist li::before {
    content: "☐ ";
    color: #0f172a;
    font-weight: 700;
  }
  .compare-row {
    display: flex;
    gap: 20px;
    align-items: flex-start;
    margin-top: 14px;
  }
  .compare-row > figure {
    flex: 1;
    margin: 0;
  }
  .compare-row img {
    width: 100%;
    height: 220px;
    object-fit: contain;
    object-position: center;
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 12px;
  }
  .compare-row figcaption {
    font-size: 0.7em;
    color: #475569;
    text-align: center;
    margin-top: 8px;
  }
  .hero-image {
    display: flex;
    justify-content: center;
    margin-top: 18px;
  }
  .hero-image img {
    width: 1000px;
    max-width: 100%;
    height: auto;
  }
  .svg-pair {
    display: flex;
    gap: 20px;
    align-items: flex-start;
  }
  .svg-pair img {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 12px;
    padding: 10px;
  }
  .svg-pair .wide {
    width: 62%;
  }
  .svg-pair .narrow {
    width: 30%;
  }
  .callout-list p {
    margin: 0 0 0.35em 0;
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
  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.8em;
  }
  th {
    background: #0f172a;
    color: #ffffff;
    border: 1px solid #0f172a;
    padding: 8px 10px;
  }
  td {
    border: 1px solid #cbd5e1;
    padding: 8px 10px;
    background: #ffffff;
  }
  tr:nth-child(even) td {
    background: #f8fafc;
  }
  .merge-table td[colspan],
  .merge-table td[rowspan] {
    background: #e0f2fe;
    font-weight: 700;
  }
  .rtl {
    direction: rtl;
    text-align: right;
  }
  .math-box {
    background: #fff7ed;
    border: 1px solid #fdba74;
    border-radius: 12px;
    padding: 14px 18px;
  }
---

<!-- _class: lead -->
<!-- note: marpx Feature Showcase — comprehensive demo of all supported conversion features. Speaker notes are included to test the notes pane output in PPTX. -->

# marpx デモ — Feature Showcase
## Marp Markdown → 編集可能な PowerPoint

- Purpose: demonstrate every feature marpx converts natively
- Scope: native shapes, images, backgrounds, fallbacks, notes, and directives
- Rule: visual fidelity matters more than editability on this deck

<p class="muted">This file intentionally mixes ordinary layouts, edge cases, and unsupported content.</p>

---

## Typography And Inline Styles

This paragraph checks **bold**, *italic*, `inline code`, [links](https://example.com), and <u>underline via HTML</u>.

これは日本語の表示確認用サンプルです。English and 日本語 should coexist without broken spacing.

<p class="right">This line is right aligned by HTML.</p>
<p class="center serif">This centered line uses a serif family.</p>
<p class="mono tiny">Monospace tiny text: key=value, port=8080, mode=review.</p>

#### Heading Level Four
##### Heading Level Five
###### Heading Level Six

---

## Paragraph Flow And Wrapping

This slide intentionally uses multiple paragraphs with different lengths so a reviewer can check text box grouping, paragraph spacing, and line wrapping in a dense but ordinary layout.

The second paragraph is shorter. It should remain in the same visual region rather than drifting into a separate, oddly placed text box.

The third paragraph contains a forced<br>line break to verify that explicit HTML line breaks survive conversion.

---

## Lists And Nesting

- First bullet with ordinary text
- Second bullet with **emphasis** and a [link](https://example.com/docs)
  - Nested bullet level two
  - Another nested bullet level two
    - Nested bullet level three
- Third bullet closes the structure

1. First ordered item
2. Second ordered item
   1. Nested ordered item
   2. Another nested ordered item
3. Third ordered item

<ul class="checklist">
  <li>Checklist item rendered with pseudo content</li>
  <li>Another checklist item for visual comparison</li>
</ul>

---

## Quote And Decorated Containers

<div class="quote-box">

**Highlighted note for decoration testing**
- The first bullet should stay inside the decorated block
- The second bullet should preserve list level semantics
- **The final bullet should remain bold**

</div>

<div class="panel callout-list">
  <p>This neutral callout contains enough prose to test paragraph extraction.</p>
  <p>It should appear as two paragraphs inside a decorated shape.</p>
</div>

> This is a real Markdown blockquote.
> It should follow the native blockquote extraction path.
>
> The second paragraph checks paragraph breaks inside the same quote.

---

## Simple Table

| Column | Left aligned text | Numeric |
| --- | --- | ---: |
| Row A | Plain content | 12 |
| Row B | Content with **bold** text | 345 |
| Row C | Content with `code` | 6789 |
| Row D | Content with a [link](https://example.com) | 10 |

---

## Merged HTML Table

<table class="merge-table">
  <tr>
    <th>Group</th>
    <th>Variant</th>
    <th>Status</th>
    <th>Notes</th>
  </tr>
  <tr>
    <td rowspan="2">Merged Row</td>
    <td>Case A</td>
    <td>OK</td>
    <td>Checks rowspan handling.</td>
  </tr>
  <tr>
    <td>Case B</td>
    <td>OK</td>
    <td>Checks cell content after merge.</td>
  </tr>
  <tr>
    <td colspan="2">Merged Column</td>
    <td>Warn</td>
    <td>Checks colspan handling.</td>
  </tr>
</table>

---

## Code Blocks

```python
from dataclasses import dataclass

@dataclass
class Sample:
    name: str
    score: float

def normalize(value: float) -> float:
    return round(value / 100.0, 3)
```

Inline code should still look distinct: `uv run marpx input.md -o output.pptx`

---

## Two Column Layout

<div class="grid-2">
  <div class="card">
    <h3>Left Column</h3>
    <p>This side mixes heading, body text, and a short list.</p>
    <ul>
      <li>Layout should stay balanced</li>
      <li>Bullets should align to the text box</li>
    </ul>
  </div>
  <div class="card">
    <h3>Right Column</h3>
    <p>The right column uses a KPI and a short note.</p>
    <div class="kpi">97.4%</div>
    <p class="tiny">This value is arbitrary and only checks font sizing and spacing.</p>
  </div>
</div>

---

## PNG Images With Width Directives

![w:1000](./images/chart-states.png)

<p class="tiny center">Check that the image appears, keeps its aspect ratio, and stays centered.</p>

---

## Side By Side PNG Images

<div class="compare-row">
  <figure>
    <img src="./images/chart-wave-raw.png" alt="Sample image A" />
    <figcaption>Image A with <code>object-fit: contain</code></figcaption>
  </figure>
  <figure>
    <img src="./images/chart-wave-filtered.png" alt="Sample image B" />
    <figcaption>Image B with the same container size</figcaption>
  </figure>
</div>

---

## SVG Images

<div class="svg-pair">
  <img class="wide" src="./images/diagram-network.svg" alt="Wide SVG" />
  <img class="narrow" src="./images/diagram-pipeline.svg" alt="Tall SVG" />
</div>

<p class="tiny">Check that both SVG images render, preserve aspect ratio, and do not blur excessively.</p>

---

## Local Image Gallery

<div class="compare-row">
  <figure>
    <img src="./images/chart-distribution.png" alt="Distribution sample" />
    <figcaption>Distribution style image</figcaption>
  </figure>
  <figure>
    <img src="./images/chart-lines.png" alt="Line chart sample" />
    <figcaption>Line chart style image</figcaption>
  </figure>
  <figure>
    <img src="./images/chart-grid.png" alt="Grid sample" />
    <figcaption>Grid style image</figcaption>
  </figure>
</div>

---

## Background Color Only
<!-- _header: marpx デモ / Background Color -->
<!-- _footer: Solid background -->
<!-- _backgroundColor: #0f766e -->

<div class="grid-3">
  <div class="swatch" style="background:#1d4ed8;">Blue swatch</div>
  <div class="swatch" style="background:#0f766e;">Green swatch</div>
  <div class="swatch" style="background:#b91c1c;">Red swatch</div>
</div>

<p>This slide is useful for checking colored fills, rounded rectangles, and white text on dark backgrounds.</p>

---

## Background Image Default

![bg](./images/chart-comparison.png)

<div class="panel">
  <h3>Default Background</h3>
  <p>This slide checks the plain <code>![bg]</code> path, which should behave like cover.</p>
</div>

---

## Background Image Cover

![bg cover](./images/chart-lines.png)

<div class="panel">
  <h3>Foreground Over Cover Background</h3>
  <p>Check text readability, z-order, and the crop behavior of the background image.</p>
</div>

---

## Background Image Contain

![bg contain](./images/diagram-pipeline.svg)

<div class="panel">
  <h3>Contain Background</h3>
  <p>The background should remain fully visible and centered rather than cropped.</p>
</div>

---

## Background Position Top Left

![bg cover](./images/chart-lines.png)

<div class="panel" style="background:rgba(255,255,255,0.88);">
  <h3>Anchored Cover Background</h3>
  <p>This slide should be reviewed with background position anchored toward the top-left corner.</p>
</div>

<!-- note: If needed, compare this with a version using top-left background position after HTML render. -->

---

## Background Image Split Right

![bg right](./images/diagram-network.svg)

### Split Background Right

- Content should stay on the left half.
- The background image should stay on the right half.
- Slide size should remain 16:9.

---

## Background Image Split Left

![bg left](./images/diagram-pipeline.svg)

### Split Background Left

- Content should move to the right half.
- The background image should stay on the left half.
- This is a direct check of the advanced background split path.

---

## Multiple Background Images

![bg contain](./images/diagram-pipeline.svg)
![bg right](./images/diagram-network.svg)

### Layered Backgrounds

- The slide should keep both background images.
- Their order and split behavior should stay stable.
- Foreground text should remain readable.

---

## Image Scale Down And Position

<div class="compare-row">
  <figure>
    <img src="./images/diagram-pipeline.svg" alt="Scale down sample" style="width:100%; height:260px; object-fit:scale-down; object-position:right center; background:#fff;" />
    <figcaption><code>object-fit: scale-down</code> and <code>object-position: right center</code></figcaption>
  </figure>
  <figure>
    <img src="./images/diagram-network.svg" alt="Top left sample" style="width:100%; height:260px; object-fit:contain; object-position:top left; background:#fff;" />
    <figcaption><code>object-position: top left</code></figcaption>
  </figure>
</div>

---

## Split Style Layout Without Background Directive

<div class="grid-2">
  <div>
    <h3>Text Region</h3>
    <ul>
      <li>This slide simulates a split layout without changing slide size.</li>
      <li>Use it to compare ordinary text beside a large SVG.</li>
      <li>The image should stay on the right and keep its aspect ratio.</li>
    </ul>
  </div>
  <div class="panel center">
    <img src="./images/diagram-network.svg" alt="Split layout SVG" style="width:100%; height:420px; object-fit:contain;" />
  </div>
</div>

---

## Directives And Pagination
<!-- _header: Directive Override -->
<!-- _footer: Footer override -->
<!-- _paginate: false -->

This slide overrides the header, footer, and paginate directives.

The expected behavior is:

- header text changes on this slide only
- footer text changes on this slide only
- page number is hidden on this slide

<!-- note: Speaker note for directive slide. Verify that this note appears in the PPTX notes pane. -->

---

## Directives Hidden
<!-- _header: "" -->
<!-- _footer: "" -->
<!-- _paginate: false -->

This slide should hide the header, footer, and page number entirely.

Use it to confirm that empty directive overrides remove generated text rather than leaving placeholders.

---

## Multi Paragraph Decorated Block

<aside class="quote-box">
This decorated aside uses ordinary placeholder prose and should become a decorated text shape.
It includes more than one sentence so the first paragraph wraps naturally.

Default mode is Example. Optional mode is Alternate.
</aside>

---

## Raw Inline SVG Fallback

<p>This slide contains inline SVG markup that should be rendered via fallback if native conversion is unavailable.</p>

<svg width="300" height="140" xmlns="http://www.w3.org/2000/svg">
  <rect x="10" y="10" width="280" height="120" rx="16" fill="#dbeafe" stroke="#1d4ed8" stroke-width="4"/>
  <circle cx="80" cy="70" r="28" fill="#1d4ed8"/>
  <text x="155" y="78" text-anchor="middle" font-size="26" fill="#0f172a">Inline SVG</text>
</svg>

---

## Full Slide Fallback Review Target

This slide is intended for optional review with `--fallback-mode slide`.

<svg width="1100" height="460" xmlns="http://www.w3.org/2000/svg">
  <rect x="10" y="10" width="1080" height="440" rx="32" fill="#eff6ff" stroke="#1d4ed8" stroke-width="8"/>
  <text x="550" y="110" text-anchor="middle" font-size="42" fill="#0f172a">Full Slide Fallback Candidate</text>
  <g fill="#1d4ed8">
    <circle cx="180" cy="220" r="36"/>
    <circle cx="340" cy="320" r="36"/>
    <circle cx="500" cy="220" r="36"/>
    <circle cx="660" cy="320" r="36"/>
    <circle cx="820" cy="220" r="36"/>
    <circle cx="980" cy="320" r="36"/>
  </g>
  <g stroke="#64748b" stroke-width="8">
    <line x1="180" y1="220" x2="340" y2="320"/>
    <line x1="340" y1="320" x2="500" y2="220"/>
    <line x1="500" y1="220" x2="660" y2="320"/>
    <line x1="660" y1="320" x2="820" y2="220"/>
    <line x1="820" y1="220" x2="980" y2="320"/>
  </g>
  <text x="550" y="450" text-anchor="middle" font-size="26" fill="#334155">This slide is useful when reviewing full-slide fallback behavior.</text>
</svg>

<!-- note: This slide should be reviewed in both default mode and --fallback-mode slide. -->

---

## Math And Mixed Text

<div class="math-box">
  <p>Math below may use a fallback path depending on the renderer:</p>
  <p>$$ f(x) = \int_{-\infty}^{\infty} e^{-t^2} \cos(xt)\,dt $$</p>
</div>

<p>Use this slide to check how unsupported structured content is captured.</p>

---

## RTL And Language Mix

<p class="rtl">هذا سطر عربي بسيط لاختبار الاتجاه من اليمين إلى اليسار.</p>

한국어 문장도 하나 넣어서 CJK 혼합 표시를 확인합니다.

Regular English text remains below for comparison.

---

## Dense Mixed Layout

<div class="grid-2">
  <div>
    <div class="card">
      <h3>Left Stack</h3>
      <p>A short paragraph sits above a small table.</p>
      <table>
        <tr><th>Key</th><th>Value</th></tr>
        <tr><td>alpha</td><td>12</td></tr>
        <tr><td>beta</td><td>34</td></tr>
      </table>
    </div>
  </div>
  <div>
    <div class="card">
      <h3>Right Stack</h3>
      <ul>
        <li>Bullet one</li>
        <li>Bullet two</li>
      </ul>
      <img src="./images/chart-bars.png" alt="Small chart" style="width:100%; height:180px; object-fit:contain;" />
    </div>
  </div>
</div>

---

## Final Checklist

- Text stays editable where expected
- Tables remain native tables where possible
- Images and SVGs render with correct sizing
- Background images stay behind foreground content
- Notes, header, footer, and pagination behave as expected
- Fallback content appears instead of disappearing

<p class="tiny">If anything looks wrong, capture the slide number, what differs, and whether the issue is content loss or visual drift.</p>

<!-- note: Final reminder note. Testers can write feedback directly against slide numbers from this deck. -->
