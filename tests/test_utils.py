"""Tests for marpx.utils module."""
from __future__ import annotations

import pytest

from marpx.models import Box, RGBAColor
from marpx.fonts import safe_font_family
from marpx.utils import (
    blend_alpha,
    boxes_have_horizontal_overlap,
    boxes_have_mergeable_vertical_gap,
    boxes_share_column,
    parse_css_color,
    px_to_emu,
    px_to_pt,
    union_boxes,
)


# ---------------------------------------------------------------------------
# parse_css_color
# ---------------------------------------------------------------------------
class TestParseCssColor:
    """Tests for CSS color string parsing."""

    def test_rgb(self) -> None:
        c = parse_css_color("rgb(255, 128, 0)")
        assert c.r == 255
        assert c.g == 128
        assert c.b == 0
        assert c.a == 1.0

    def test_rgba(self) -> None:
        c = parse_css_color("rgba(10, 20, 30, 0.5)")
        assert c.r == 10
        assert c.g == 20
        assert c.b == 30
        assert c.a == pytest.approx(0.5)

    def test_hex_rrggbb(self) -> None:
        c = parse_css_color("#ff8000")
        assert c.r == 255
        assert c.g == 128
        assert c.b == 0
        assert c.a == 1.0

    def test_hex_rgb_shorthand(self) -> None:
        c = parse_css_color("#f00")
        assert c.r == 255
        assert c.g == 0
        assert c.b == 0

    def test_hex_rrggbbaa(self) -> None:
        c = parse_css_color("#ff000080")
        assert c.r == 255
        assert c.g == 0
        assert c.b == 0
        assert c.a == pytest.approx(128 / 255, abs=0.01)

    def test_named_black(self) -> None:
        c = parse_css_color("black")
        assert c == RGBAColor(r=0, g=0, b=0, a=1.0)

    def test_named_white(self) -> None:
        c = parse_css_color("white")
        assert c == RGBAColor(r=255, g=255, b=255, a=1.0)

    def test_named_red(self) -> None:
        c = parse_css_color("red")
        assert c == RGBAColor(r=255, g=0, b=0, a=1.0)

    def test_named_transparent(self) -> None:
        c = parse_css_color("transparent")
        assert c.a == 0.0

    def test_unknown_returns_black(self) -> None:
        c = parse_css_color("nonexistent-color")
        assert c == RGBAColor(r=0, g=0, b=0, a=1.0)

    def test_whitespace_trimming(self) -> None:
        c = parse_css_color("  rgb(1, 2, 3)  ")
        assert c.r == 1
        assert c.g == 2
        assert c.b == 3


# ---------------------------------------------------------------------------
# px_to_emu
# ---------------------------------------------------------------------------
class TestPxToEmu:
    """Tests for pixel-to-EMU conversion."""

    def test_zero(self) -> None:
        assert px_to_emu(0) == 0

    def test_known_100px(self) -> None:
        # 100 * 9525 = 952500
        assert px_to_emu(100) == 952500

    def test_known_1280px(self) -> None:
        # 1280 * 9525 = 12192000
        assert px_to_emu(1280) == 12192000

    def test_fractional(self) -> None:
        # Should return an int (rounded)
        result = px_to_emu(1.5)
        assert isinstance(result, int)
        assert result == round(1.5 * 9525)


# ---------------------------------------------------------------------------
# px_to_pt
# ---------------------------------------------------------------------------
class TestPxToPt:
    """Tests for pixel-to-point conversion."""

    def test_16px(self) -> None:
        assert px_to_pt(16) == pytest.approx(12.0)

    def test_96px(self) -> None:
        assert px_to_pt(96) == pytest.approx(72.0)

    def test_zero(self) -> None:
        assert px_to_pt(0) == 0.0

    def test_float_result(self) -> None:
        result = px_to_pt(20)
        assert isinstance(result, float)


# ---------------------------------------------------------------------------
# layout helpers
# ---------------------------------------------------------------------------
class TestLayoutHelpers:
    """Tests for shared box geometry helpers."""

    def test_boxes_share_column_with_small_offsets(self) -> None:
        first = Box(x=100, y=20, width=400, height=60)
        second = Box(x=106, y=120, width=390, height=40)
        assert boxes_share_column(first, second) is True

    def test_boxes_share_column_rejects_large_offset(self) -> None:
        first = Box(x=100, y=20, width=400, height=60)
        second = Box(x=130, y=120, width=390, height=40)
        assert boxes_share_column(first, second) is False

    def test_boxes_have_horizontal_overlap(self) -> None:
        first = Box(x=80, y=20, width=500, height=60)
        second = Box(x=140, y=100, width=420, height=50)
        assert boxes_have_horizontal_overlap(first, second) is True

    def test_boxes_have_horizontal_overlap_rejects_small_overlap(self) -> None:
        first = Box(x=80, y=20, width=200, height=60)
        second = Box(x=260, y=100, width=200, height=50)
        assert boxes_have_horizontal_overlap(first, second) is False

    def test_boxes_have_mergeable_vertical_gap(self) -> None:
        first = Box(x=80, y=20, width=300, height=50)
        second = Box(x=80, y=96, width=300, height=40)
        assert boxes_have_mergeable_vertical_gap(first, second, max_gap_px=32) is True

    def test_boxes_have_mergeable_vertical_gap_rejects_distant_boxes(self) -> None:
        first = Box(x=80, y=20, width=300, height=50)
        second = Box(x=80, y=150, width=300, height=40)
        assert boxes_have_mergeable_vertical_gap(first, second, max_gap_px=32) is False

    def test_union_boxes(self) -> None:
        merged = union_boxes(
            [
                Box(x=50, y=40, width=100, height=60),
                Box(x=120, y=70, width=80, height=50),
            ]
        )
        assert merged == Box(x=50, y=40, width=150, height=80)

    def test_union_boxes_requires_input(self) -> None:
        with pytest.raises(ValueError, match="at least one box"):
            union_boxes([])


# ---------------------------------------------------------------------------
# blend_alpha
# ---------------------------------------------------------------------------
class TestBlendAlpha:
    """Tests for alpha blending."""

    def test_opaque_stays_same(self) -> None:
        color = RGBAColor(r=100, g=150, b=200, a=1.0)
        result = blend_alpha(color)
        assert result.r == 100
        assert result.g == 150
        assert result.b == 200
        assert result.a == 1.0

    def test_transparent_becomes_bg(self) -> None:
        color = RGBAColor(r=0, g=0, b=0, a=0.0)
        result = blend_alpha(color)  # default bg is white
        assert result.r == 255
        assert result.g == 255
        assert result.b == 255

    def test_semi_transparent_on_white(self) -> None:
        color = RGBAColor(r=0, g=0, b=0, a=0.5)
        result = blend_alpha(color)
        # 0*0.5 + 255*0.5 = 127.5 -> 128
        assert result.r == 128
        assert result.g == 128
        assert result.b == 128

    def test_custom_background(self) -> None:
        color = RGBAColor(r=255, g=0, b=0, a=0.5)
        bg = RGBAColor(r=0, g=0, b=255)
        result = blend_alpha(color, bg)
        assert result.r == 128  # 255*0.5 + 0*0.5
        assert result.g == 0
        assert result.b == 128  # 0*0.5 + 255*0.5

    def test_result_is_opaque(self) -> None:
        color = RGBAColor(r=50, g=50, b=50, a=0.3)
        result = blend_alpha(color)
        assert result.a == 1.0


# ---------------------------------------------------------------------------
# safe_font_family
# ---------------------------------------------------------------------------
class TestSafeFontFamily:
    """Tests for CSS font family mapping."""

    # --- Generic CSS families ---
    def test_sans_serif(self) -> None:
        assert safe_font_family("sans-serif") == "Arial"

    def test_serif(self) -> None:
        assert safe_font_family("serif") == "Times New Roman"

    def test_monospace(self) -> None:
        assert safe_font_family("monospace") == "Courier New"

    def test_cursive(self) -> None:
        assert safe_font_family("cursive") == "Comic Sans MS"

    def test_fantasy(self) -> None:
        assert safe_font_family("fantasy") == "Impact"

    # --- System UI font mapping ---
    def test_system_ui(self) -> None:
        assert safe_font_family("system-ui") == "Calibri"

    def test_apple_system(self) -> None:
        assert safe_font_family("-apple-system") == "Calibri"

    def test_ui_monospace(self) -> None:
        assert safe_font_family("ui-monospace") == "Courier New"

    # --- Passthrough fonts (known safe for PowerPoint) ---
    def test_passthrough_calibri(self) -> None:
        assert safe_font_family("Calibri") == "Calibri"

    def test_passthrough_consolas(self) -> None:
        assert safe_font_family("Consolas") == "Consolas"

    def test_passthrough_georgia(self) -> None:
        assert safe_font_family("Georgia") == "Georgia"

    def test_passthrough_arial(self) -> None:
        assert safe_font_family("Arial") == "Arial"

    def test_passthrough_courier_new(self) -> None:
        assert safe_font_family("Courier New") == "Courier New"

    def test_passthrough_times_new_roman(self) -> None:
        assert safe_font_family("Times New Roman") == "Times New Roman"

    def test_passthrough_preserves_casing(self) -> None:
        # Original casing should be preserved for passthrough fonts
        assert safe_font_family("CALIBRI") == "CALIBRI"
        assert safe_font_family("calibri") == "calibri"

    # --- CJK font passthrough ---
    def test_passthrough_meiryo(self) -> None:
        assert safe_font_family("Meiryo") == "Meiryo"

    def test_passthrough_yu_gothic(self) -> None:
        assert safe_font_family("Yu Gothic") == "Yu Gothic"

    def test_passthrough_hiragino_sans(self) -> None:
        assert safe_font_family("Hiragino Sans") == "Hiragino Sans"

    def test_passthrough_microsoft_yahei(self) -> None:
        assert safe_font_family("Microsoft YaHei") == "Microsoft YaHei"

    def test_passthrough_malgun_gothic(self) -> None:
        assert safe_font_family("Malgun Gothic") == "Malgun Gothic"

    # --- Web font mapping ---
    def test_mapped_inter(self) -> None:
        assert safe_font_family("Inter") == "Calibri"

    def test_mapped_jetbrains_mono(self) -> None:
        assert safe_font_family("JetBrains Mono") == "Consolas"

    def test_mapped_ubuntu_mono(self) -> None:
        assert safe_font_family("Ubuntu Mono") == "Consolas"

    def test_mapped_ibm_plex_sans(self) -> None:
        assert safe_font_family("IBM Plex Sans") == "Arial"

    def test_mapped_courier(self) -> None:
        assert safe_font_family("Courier") == "Courier New"

    def test_mapped_times(self) -> None:
        assert safe_font_family("Times") == "Times New Roman"

    def test_mapped_helvetica(self) -> None:
        # Helvetica is in _PASSTHROUGH_FONTS (macOS) but also in _FONT_MAP.
        # Passthrough takes priority, so original casing is preserved.
        assert safe_font_family("Helvetica") == "Helvetica"

    # --- CSS font-family list handling ---
    def test_css_font_list_picks_first(self) -> None:
        assert safe_font_family("monospace, Arial, sans-serif") == "Courier New"

    def test_css_font_list_quoted(self) -> None:
        assert safe_font_family("'Courier New', monospace") == "Courier New"

    def test_css_font_list_helvetica_neue(self) -> None:
        # Helvetica Neue is in the passthrough list
        result = safe_font_family("'Helvetica Neue', Arial, sans-serif")
        assert result == "Helvetica Neue"

    # --- Unknown font passthrough ---
    def test_unknown_font_passthrough(self) -> None:
        assert safe_font_family("MyCustomFont") == "MyCustomFont"

    def test_unknown_font_exotic(self) -> None:
        assert safe_font_family("SomeExoticFont") == "SomeExoticFont"

    # --- Edge cases ---
    def test_empty_string_fallback(self) -> None:
        assert safe_font_family("") == "Arial"

    def test_whitespace_only_fallback(self) -> None:
        assert safe_font_family("   ") == "Arial"

    def test_double_quoted_font(self) -> None:
        assert safe_font_family('"Segoe UI", sans-serif') == "Segoe UI"

    def test_css_font_list_ui_monospace(self) -> None:
        assert safe_font_family("ui-monospace, SFMono-Regular, monospace") == "Courier New"
