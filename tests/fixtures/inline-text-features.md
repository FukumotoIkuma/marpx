---
marp: true
---

<!-- Slide 1: test_heading_with_inline_spans_preserves_inter_run_space -->
# Slide

## <span style="color:#60a5fa;">marpx</span> <span style="color:#e2e8f0;">Kitchen Sink</span>

---

<!-- Slide 2: test_paragraph_trims_html_indentation_whitespace -->
# Slide

<p style="text-align:right; color:#94a3b8; font-size:0.62em;">
  Header · Footer · Paginate · Speaker Notes · Background — all directives supported
</p>

---

<!-- Slide 3: test_paragraph_preserves_br_line_breaks -->
# Slide

<p>
  <strong>Heading · List · Table · Code · Image · Badge · Quote</strong><br/>
  1 枚に全部載せ。これがネイティブ PowerPoint になります。
</p>

---

<!-- Slide 4: test_code_block_preserves_newlines_and_indentation -->
# Slide

```python
from dataclasses import dataclass

@dataclass
class Sample:
    value: int
```

---

<!-- Slide 5: test_inline_code_stays_in_paragraph_runs + test_inline_code_is_not_extracted_as_overlay_decorated_element -->
# Slide

This uses `inline code` in a sentence.

---

<!-- Slide 6: test_mark_stays_in_paragraph_runs -->
# Slide

<mark>This text is highlighted</mark> and continues normally.

---

<!-- Slide 7: test_twemoji_inline_images_fallback_to_alt_text -->
# Slide

Target: 🎯 Rocket: 🚀

---

<!-- Slide 8: test_markdown_blockquote_extracts_decoration -->
# Slide

> Sample blockquote text

---

<!-- Slide 9: test_nested_blockquote_preserves_nested_quote_and_paragraph_break -->
# Slide

> > line one
> >
> > -- **Jeff Atwood**, *Coding Horror*

---

<!-- Slide 10: test_blockquote_strikethrough_is_extracted -->
# Slide

> Remember that ~~premature optimization~~ is the root of all evil.

---

<!-- Slide 11: test_nested_bold_inside_strikethrough_preserves_strike -->
# Slide

Strikethrough with bold: <s>this is struck through with <strong>bold emphasis</strong> inside</s>

---

<!-- Slide 12: test_inline_emphasis_in_list_item_preserves_surrounding_spaces -->

- First bullet
- Second bullet with **emphasis** and trailing text
