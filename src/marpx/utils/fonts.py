"""Font mapping for CSS font families to PowerPoint-compatible equivalents."""

from __future__ import annotations

# Known fonts that are safe to pass through to PowerPoint directly.
# These are commonly installed on Windows/macOS and supported by PowerPoint.
_PASSTHROUGH_FONTS: set[str] = {
    # Windows/Office standard fonts
    "arial",
    "calibri",
    "cambria",
    "candara",
    "century gothic",
    "comic sans ms",
    "consolas",
    "constantia",
    "corbel",
    "courier new",
    "franklin gothic medium",
    "garamond",
    "georgia",
    "impact",
    "lucida console",
    "lucida sans unicode",
    "palatino linotype",
    "segoe ui",
    "tahoma",
    "times new roman",
    "trebuchet ms",
    "verdana",
    # macOS standard fonts
    "avenir",
    "avenir next",
    "futura",
    "gill sans",
    "helvetica",
    "helvetica neue",
    "menlo",
    "monaco",
    "optima",
    "palatino",
    "san francisco",
    "sf pro",
    "sf mono",
    # Common cross-platform
    "roboto",
    "open sans",
    "lato",
    "montserrat",
    "source sans pro",
    "source code pro",
    "noto sans",
    "noto serif",
    "fira code",
    "fira sans",
    # CJK fonts
    "yu gothic",
    "yu mincho",
    "meiryo",
    "ms gothic",
    "ms mincho",
    "hiragino sans",
    "hiragino kaku gothic pro",
    "hiragino mincho pro",
    "noto sans cjk jp",
    "noto serif cjk jp",
    "malgun gothic",
    "gulim",
    "batang",
    "microsoft yahei",
    "simsun",
    "simhei",
}

# Mapping from CSS/web font names to PowerPoint-safe equivalents.
_FONT_MAP: dict[str, str] = {
    # Generic families
    "sans-serif": "Arial",
    "serif": "Times New Roman",
    "monospace": "Courier New",
    "cursive": "Comic Sans MS",
    "fantasy": "Impact",
    # System UI fonts
    "system-ui": "Calibri",
    "-apple-system": "Calibri",
    "blinkmacsystemfont": "Calibri",
    "ui-monospace": "Courier New",
    "ui-sans-serif": "Arial",
    "ui-serif": "Times New Roman",
    "segoe ui": "Segoe UI",
    # Common web fonts -> closest PowerPoint equivalent
    "inter": "Calibri",
    "source sans 3": "Source Sans Pro",
    "ibm plex sans": "Arial",
    "ibm plex mono": "Consolas",
    "jetbrains mono": "Consolas",
    "ubuntu": "Calibri",
    "ubuntu mono": "Consolas",
    "droid sans": "Arial",
    "droid sans mono": "Courier New",
    # Legacy
    "arial black": "Arial Black",
    "book antiqua": "Palatino Linotype",
    "courier": "Courier New",
    "helvetica": "Arial",  # PowerPoint on Windows doesn't have Helvetica
    "times": "Times New Roman",
    "symbol": "Symbol",
    "wingdings": "Wingdings",
}


def safe_font_family(font_family: str) -> str:
    """Map CSS font family to a PowerPoint-compatible font.

    Strategy:
    1. Extract the first font from the CSS font-family list
    2. If it's a known safe font, pass it through directly
    3. If it has a known mapping, use the mapped font
    4. Otherwise return it as-is (PowerPoint will substitute)
    """
    # Extract first font from CSS font-family list
    first_font = font_family.split(",")[0].strip().strip("'\"")

    if not first_font:
        return "Arial"

    lower = first_font.lower()

    # Check passthrough list (known to work in PowerPoint)
    if lower in _PASSTHROUGH_FONTS:
        return first_font  # Preserve original casing

    # Check explicit mapping
    if lower in _FONT_MAP:
        return _FONT_MAP[lower]

    # For unknown fonts, return as-is -- PowerPoint will substitute
    return first_font
