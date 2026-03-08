"""Tests for marpx.gradient_utils module."""

from __future__ import annotations

import pytest

from marpx.gradient_utils import (
    ParsedLinearGradient,
    ParsedRadialGradient,
    css_angle_to_ooxml_angle,
    parse_linear_gradient,
    parse_radial_gradient,
    render_gradient_png,
    render_linear_gradient_png,
    render_radial_gradient_png,
    representative_gradient_color,
)
from marpx.models import RGBAColor

# PNG magic bytes signature
_PNG_HEADER = b"\x89PNG\r\n\x1a\n"


# ---------------------------------------------------------------------------
# TestCssAngleToOoxmlAngle
# ---------------------------------------------------------------------------
class TestCssAngleToOoxmlAngle:
    """Tests for css_angle_to_ooxml_angle conversion."""

    def test_zero_degrees(self) -> None:
        # CSS 0deg → OOXML 90deg → 90 * 60000 = 5400000
        result = css_angle_to_ooxml_angle(0.0)
        assert result == 5400000

    def test_90_degrees(self) -> None:
        # CSS 90deg → OOXML 0deg → 0
        result = css_angle_to_ooxml_angle(90.0)
        assert result == 0

    def test_180_degrees(self) -> None:
        # CSS 180deg → OOXML 270deg → 270 * 60000 = 16200000
        result = css_angle_to_ooxml_angle(180.0)
        assert result == 16200000

    def test_270_degrees(self) -> None:
        # CSS 270deg → OOXML 180deg → 180 * 60000 = 10800000
        result = css_angle_to_ooxml_angle(270.0)
        assert result == 10800000

    def test_arbitrary_angle_45(self) -> None:
        # CSS 45deg → OOXML (90-45)=45deg → 45 * 60000 = 2700000
        result = css_angle_to_ooxml_angle(45.0)
        assert result == 2700000

    def test_arbitrary_angle_135(self) -> None:
        # CSS 135deg → OOXML (90-135) % 360 = 315deg → 315 * 60000 = 18900000
        result = css_angle_to_ooxml_angle(135.0)
        assert result == 18900000


# ---------------------------------------------------------------------------
# TestRepresentativeGradientColor
# ---------------------------------------------------------------------------
class TestRepresentativeGradientColor:
    """Tests for representative_gradient_color."""

    def test_single_color_stop(self) -> None:
        color = representative_gradient_color("linear-gradient(red, red)")
        assert color is not None
        assert color.r == 255
        assert color.g == 0
        assert color.b == 0

    def test_multiple_colors_returns_first_stop(self) -> None:
        # Should return the first color stop (red), not blue
        color = representative_gradient_color("linear-gradient(red, blue)")
        assert color is not None
        assert color.r == 255
        assert color.g == 0
        assert color.b == 0

    def test_invalid_gradient_returns_none(self) -> None:
        color = representative_gradient_color("not-a-gradient")
        assert color is None

    def test_empty_string_returns_none(self) -> None:
        color = representative_gradient_color("")
        assert color is None

    def test_radial_gradient_returns_none(self) -> None:
        # representative_gradient_color only handles linear-gradient internally
        color = representative_gradient_color("radial-gradient(red, blue)")
        assert color is None


# ---------------------------------------------------------------------------
# TestParseLinearGradient
# ---------------------------------------------------------------------------
class TestParseLinearGradient:
    """Tests for parse_linear_gradient."""

    def test_basic_two_colors_default_angle(self) -> None:
        result = parse_linear_gradient("linear-gradient(red, blue)")
        assert result is not None
        assert isinstance(result, ParsedLinearGradient)
        assert result.angle_deg == pytest.approx(180.0)
        assert len(result.stops) == 2

    def test_angle_direction_0deg(self) -> None:
        result = parse_linear_gradient("linear-gradient(0deg, red, blue)")
        assert result is not None
        assert result.angle_deg == pytest.approx(0.0)

    def test_angle_direction_90deg(self) -> None:
        result = parse_linear_gradient("linear-gradient(90deg, red, blue)")
        assert result is not None
        assert result.angle_deg == pytest.approx(90.0)

    def test_keyword_to_right(self) -> None:
        result = parse_linear_gradient("linear-gradient(to right, red, blue)")
        assert result is not None
        assert result.angle_deg == pytest.approx(90.0)

    def test_keyword_to_bottom(self) -> None:
        result = parse_linear_gradient("linear-gradient(to bottom, white, black)")
        assert result is not None
        assert result.angle_deg == pytest.approx(180.0)

    def test_keyword_to_top(self) -> None:
        result = parse_linear_gradient("linear-gradient(to top, white, black)")
        assert result is not None
        assert result.angle_deg == pytest.approx(0.0)

    def test_keyword_to_left(self) -> None:
        result = parse_linear_gradient("linear-gradient(to left, white, black)")
        assert result is not None
        assert result.angle_deg == pytest.approx(270.0)

    def test_keyword_to_bottom_left(self) -> None:
        result = parse_linear_gradient("linear-gradient(to bottom left, red, blue)")
        assert result is not None
        assert result.angle_deg == pytest.approx(225.0)

    def test_keyword_to_top_right(self) -> None:
        result = parse_linear_gradient("linear-gradient(to top right, red, blue)")
        assert result is not None
        assert result.angle_deg == pytest.approx(45.0)

    def test_explicit_stop_positions(self) -> None:
        result = parse_linear_gradient("linear-gradient(red 0%, blue 100%)")
        assert result is not None
        assert len(result.stops) == 2
        assert result.stops[0].position == pytest.approx(0.0)
        assert result.stops[-1].position == pytest.approx(1.0)

    def test_implicit_stop_positions_interpolated(self) -> None:
        # Three stops with no explicit positions: 0%, 50%, 100%
        result = parse_linear_gradient("linear-gradient(red, green, blue)")
        assert result is not None
        assert len(result.stops) == 3
        assert result.stops[0].position == pytest.approx(0.0)
        assert result.stops[1].position == pytest.approx(0.5)
        assert result.stops[2].position == pytest.approx(1.0)

    def test_rgba_color_stop_parenthesis_depth(self) -> None:
        # Commas inside rgba() must not be treated as stop separators
        result = parse_linear_gradient("linear-gradient(rgba(255,0,0,0.5), blue)")
        assert result is not None
        assert len(result.stops) == 2
        first = result.stops[0].color
        assert first.r == 255
        assert first.g == 0
        assert first.b == 0
        assert first.a == pytest.approx(0.5)

    def test_invalid_not_a_gradient(self) -> None:
        assert parse_linear_gradient("not-a-gradient") is None

    def test_invalid_radial_gradient(self) -> None:
        assert parse_linear_gradient("radial-gradient(red, blue)") is None

    def test_invalid_empty_string(self) -> None:
        assert parse_linear_gradient("") is None

    def test_missing_closing_paren_returns_none(self) -> None:
        assert parse_linear_gradient("linear-gradient(red, blue") is None

    def test_stop_colors_correct_values(self) -> None:
        result = parse_linear_gradient("linear-gradient(#ff0000, #0000ff)")
        assert result is not None
        assert result.stops[0].color == RGBAColor(r=255, g=0, b=0, a=1.0)
        assert result.stops[1].color == RGBAColor(r=0, g=0, b=255, a=1.0)


# ---------------------------------------------------------------------------
# TestParseRadialGradient
# ---------------------------------------------------------------------------
class TestParseRadialGradient:
    """Tests for parse_radial_gradient."""

    def test_basic_two_colors(self) -> None:
        result = parse_radial_gradient("radial-gradient(red, blue)")
        assert result is not None
        assert isinstance(result, ParsedRadialGradient)
        assert len(result.stops) == 2

    def test_default_center_is_midpoint(self) -> None:
        result = parse_radial_gradient("radial-gradient(red, blue)")
        assert result is not None
        assert result.center_x == pytest.approx(0.5)
        assert result.center_y == pytest.approx(0.5)

    def test_with_position_at_percent(self) -> None:
        result = parse_radial_gradient("radial-gradient(circle at 25% 75%, red, blue)")
        assert result is not None
        assert result.center_x == pytest.approx(0.25)
        assert result.center_y == pytest.approx(0.75)

    def test_color_stop_positions(self) -> None:
        result = parse_radial_gradient("radial-gradient(white 0%, black 100%)")
        assert result is not None
        assert result.stops[0].position == pytest.approx(0.0)
        assert result.stops[1].position == pytest.approx(1.0)

    def test_invalid_returns_none(self) -> None:
        assert parse_radial_gradient("linear-gradient(red, blue)") is None

    def test_empty_string_returns_none(self) -> None:
        assert parse_radial_gradient("") is None


# ---------------------------------------------------------------------------
# TestRenderLinearGradientPng
# ---------------------------------------------------------------------------
class TestRenderLinearGradientPng:
    """Tests for render_linear_gradient_png."""

    def test_returns_bytes(self) -> None:
        result = render_linear_gradient_png("linear-gradient(red, blue)", 100, 100)
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_valid_png_header(self) -> None:
        result = render_linear_gradient_png("linear-gradient(red, blue)", 100, 100)
        assert result is not None
        assert result[:8] == _PNG_HEADER

    def test_different_angles_produce_different_output(self) -> None:
        horizontal = render_linear_gradient_png(
            "linear-gradient(to right, red, blue)", 50, 50
        )
        vertical = render_linear_gradient_png(
            "linear-gradient(to bottom, red, blue)", 50, 50
        )
        assert horizontal != vertical

    def test_color_accuracy_solid_red(self) -> None:
        from PIL import Image
        import io

        result = render_linear_gradient_png("linear-gradient(red, red)", 10, 10)
        assert result is not None
        img = Image.open(io.BytesIO(result)).convert("RGBA")
        pixel = img.getpixel((5, 5))
        assert pixel[0] == 255  # R
        assert pixel[1] == 0  # G
        assert pixel[2] == 0  # B

    def test_invalid_gradient_returns_none(self) -> None:
        result = render_linear_gradient_png("not-a-gradient", 100, 100)
        assert result is None

    def test_border_radius_applied(self) -> None:
        # With border_radius_px > 0, corners should have transparency
        from PIL import Image
        import io

        result = render_linear_gradient_png(
            "linear-gradient(red, red)", 100, 100, border_radius_px=20.0
        )
        assert result is not None
        img = Image.open(io.BytesIO(result)).convert("RGBA")
        # Top-left corner pixel should be transparent (alpha = 0)
        corner_pixel = img.getpixel((0, 0))
        assert corner_pixel[3] == 0

    def test_minimum_size_one_pixel(self) -> None:
        result = render_linear_gradient_png("linear-gradient(red, blue)", 1, 1)
        assert result is not None
        assert result[:8] == _PNG_HEADER


# ---------------------------------------------------------------------------
# TestRenderRadialGradientPng
# ---------------------------------------------------------------------------
class TestRenderRadialGradientPng:
    """Tests for render_radial_gradient_png."""

    def test_returns_bytes(self) -> None:
        result = render_radial_gradient_png("radial-gradient(red, blue)", 100, 100)
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_valid_png_header(self) -> None:
        result = render_radial_gradient_png("radial-gradient(red, blue)", 100, 100)
        assert result is not None
        assert result[:8] == _PNG_HEADER

    def test_different_center_produces_different_output(self) -> None:
        centered = render_radial_gradient_png(
            "radial-gradient(circle at 50% 50%, red, blue)", 50, 50
        )
        offset = render_radial_gradient_png(
            "radial-gradient(circle at 10% 10%, red, blue)", 50, 50
        )
        assert centered != offset

    def test_invalid_gradient_returns_none(self) -> None:
        result = render_radial_gradient_png("not-a-gradient", 100, 100)
        assert result is None

    def test_color_accuracy_solid_blue(self) -> None:
        from PIL import Image
        import io

        result = render_radial_gradient_png("radial-gradient(blue, blue)", 10, 10)
        assert result is not None
        img = Image.open(io.BytesIO(result)).convert("RGBA")
        pixel = img.getpixel((5, 5))
        assert pixel[0] == 0  # R
        assert pixel[1] == 0  # G
        assert pixel[2] == 255  # B


# ---------------------------------------------------------------------------
# TestRenderGradientPng
# ---------------------------------------------------------------------------
class TestRenderGradientPng:
    """Tests for render_gradient_png dispatcher."""

    def test_dispatches_to_linear(self) -> None:
        result = render_gradient_png("linear-gradient(red, blue)", 50, 50)
        assert result is not None
        assert result[:8] == _PNG_HEADER

    def test_dispatches_to_radial(self) -> None:
        result = render_gradient_png("radial-gradient(red, blue)", 50, 50)
        assert result is not None
        assert result[:8] == _PNG_HEADER

    def test_unknown_gradient_type_returns_none(self) -> None:
        result = render_gradient_png("conic-gradient(red, blue)", 50, 50)
        assert result is None

    def test_empty_string_returns_none(self) -> None:
        result = render_gradient_png("", 50, 50)
        assert result is None

    def test_linear_and_radial_outputs_differ(self) -> None:
        linear = render_gradient_png("linear-gradient(red, blue)", 50, 50)
        radial = render_gradient_png("radial-gradient(red, blue)", 50, 50)
        assert linear != radial
