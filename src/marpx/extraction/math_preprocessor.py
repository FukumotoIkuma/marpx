"""Pre-process Marp Markdown to preserve LaTeX source for math expressions."""

from __future__ import annotations

import html
import re


def preprocess_math_latex(markdown: str) -> str:
    """Wrap $...$ and $$...$$ with data-latex attributes.

    Preserves the original math delimiters so MathJax still renders,
    while adding data-latex attributes that survive in the HTML output.
    """
    lines = markdown.split("\n")
    result: list[str] = []

    # State tracking
    in_frontmatter = False
    in_code_block = False

    i = 0
    while i < len(lines):
        line = lines[i]

        # Track frontmatter (only at start of file)
        if i == 0 and line.strip() == "---":
            in_frontmatter = True
            result.append(line)
            i += 1
            continue

        if in_frontmatter:
            if line.strip() == "---":
                in_frontmatter = False
            result.append(line)
            i += 1
            continue

        # Track fenced code blocks
        if re.match(r"^(`{3,}|~{3,})", line.strip()):
            in_code_block = not in_code_block
            result.append(line)
            i += 1
            continue

        if in_code_block:
            result.append(line)
            i += 1
            continue

        # Check for display math ($$...$$)
        # Could be single-line or multi-line
        display_match = re.match(r"^(\s*)\$\$(.*)$", line)
        if display_match:
            indent = display_match.group(1)
            rest = display_match.group(2)

            # Check if closing $$ is on the same line
            if "$$" in rest:
                # Single-line display math: $$content$$
                inner_match = re.match(r"^(.*?)\$\$(.*)$", rest)
                if inner_match:
                    latex_content = inner_match.group(1)
                    after = inner_match.group(2)
                    escaped = html.escape(latex_content, quote=True)
                    result.append(
                        f'{indent}<div data-latex="{escaped}">'
                        f"$${latex_content}$${after}</div>"
                    )
                    i += 1
                    continue

            # Multi-line display math
            math_lines = [line]
            j = i + 1
            while j < len(lines):
                math_lines.append(lines[j])
                if "$$" in lines[j] and j != i:
                    break
                j += 1

            # Extract LaTeX content
            full_math = "\n".join(math_lines)
            # Match $$...$$
            dm_match = re.search(r"\$\$(.*?)\$\$", full_math, re.DOTALL)
            if dm_match:
                latex_content = dm_match.group(1).strip()
                escaped = html.escape(latex_content, quote=True)
                result.append(f'{indent}<div data-latex="{escaped}">')
                for ml in math_lines:
                    result.append(ml)
                result.append("</div>")
                i = j + 1
                continue
            else:
                # Couldn't match, pass through
                result.append(line)
                i += 1
                continue

        # Process inline math on this line
        line = _process_inline_math(line)
        result.append(line)
        i += 1

    return "\n".join(result)


def _process_inline_math(line: str) -> str:
    """Replace $...$ with <span data-latex="...">$...$</span> in a single line."""
    # Protect inline code spans first
    code_spans: list[str] = []

    def _save_code(m: re.Match) -> str:
        code_spans.append(m.group(0))
        return f"\x00CODE{len(code_spans) - 1}\x00"

    protected = re.sub(r"`[^`]+`", _save_code, line)

    # Find inline math: $...$ (not $$)
    # Rules: opening $ must not be followed by space, closing $ must not be
    # preceded by space, closing $ must not be followed by digit,
    # handle escaped \$
    def _replace_inline(m: re.Match) -> str:
        latex = m.group(1)
        escaped = html.escape(latex, quote=True)
        return f'<span data-latex="{escaped}">${latex}$</span>'

    # Match $...$ but not $$, not \$, not $ followed by space,
    # not preceded-by-space $
    processed = re.sub(
        r"(?<!\\)(?<!\$)\$(?!\$)(?!\s)(.+?)(?<!\s)\$(?!\d)(?!\$)",
        _replace_inline,
        protected,
    )

    # Restore code spans
    for idx, code in enumerate(code_spans):
        processed = processed.replace(f"\x00CODE{idx}\x00", code)

    return processed
