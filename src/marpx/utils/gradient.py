"""Helpers for parsing and rendering simple CSS gradients."""

from __future__ import annotations

import io
import math
import re
from dataclasses import dataclass

import numpy as np
from PIL import Image, ImageDraw

from marpx.models import RGBAColor
from marpx.utils.common import parse_css_color


@dataclass(frozen=True)
class GradientStop:
    color: RGBAColor
    position: float
    unit: str = "%"  # "%" for relative positions, "px" for pixel positions


@dataclass(frozen=True)
class ParsedLinearGradient:
    angle_deg: float
    stops: tuple[GradientStop, ...]


@dataclass(frozen=True)
class ParsedRadialGradient:
    center_x: float
    center_y: float
    stops: tuple[GradientStop, ...]


def css_angle_to_ooxml_angle(angle_deg: float) -> int:
    """Convert CSS linear-gradient angle to OOXML a:lin angle units."""
    normalized = (90.0 - angle_deg) % 360.0
    return int(round(normalized * 60000))


def representative_gradient_color(css_gradient: str) -> RGBAColor | None:
    """Return a representative color for text gradients."""
    parsed = parse_linear_gradient(css_gradient)
    if parsed is None:
        parsed = parse_repeating_linear_gradient(css_gradient)
    if not parsed or not parsed.stops:
        return None
    return parsed.stops[0].color


def parse_linear_gradient(css_gradient: str) -> ParsedLinearGradient | None:
    """Parse a simple CSS linear-gradient() string."""
    gradient = css_gradient.strip()
    if not gradient.lower().startswith("linear-gradient(") or not gradient.endswith(
        ")"
    ):
        return None

    inner = gradient[len("linear-gradient(") : -1]
    return _parse_linear_gradient_inner(inner)


def parse_repeating_linear_gradient(
    css_gradient: str,
) -> ParsedLinearGradient | None:
    """Parse a CSS repeating-linear-gradient() string.

    Returns a ``ParsedLinearGradient`` with stops *as declared* (not expanded).
    The repeating behaviour is handled at render time.
    """
    gradient = css_gradient.strip()
    if not gradient.lower().startswith(
        "repeating-linear-gradient("
    ) or not gradient.endswith(")"):
        return None

    inner = gradient[len("repeating-linear-gradient(") : -1]
    return _parse_linear_gradient_inner(inner)


def _parse_linear_gradient_inner(inner: str) -> ParsedLinearGradient | None:
    """Shared parsing logic for linear-gradient and repeating-linear-gradient."""
    parts = _split_top_level_commas(inner)
    if len(parts) < 2:
        return None

    angle_deg = 180.0
    stop_parts = parts
    first = parts[0].strip().lower()
    if _looks_like_direction(first):
        parsed_angle = _parse_gradient_direction(first)
        if parsed_angle is not None:
            angle_deg = parsed_angle
            stop_parts = parts[1:]

    raw_stops: list[tuple[RGBAColor, float | None, str]] = []
    for part in stop_parts:
        parsed = _parse_gradient_stop(part)
        if parsed is None:
            return None
        raw_stops.append(parsed)

    stops = _resolve_stop_positions(raw_stops)
    return ParsedLinearGradient(angle_deg=angle_deg, stops=tuple(stops))


def render_repeating_linear_gradient_png(
    css_gradient: str,
    width_px: int,
    height_px: int,
    border_radius_px: float = 0.0,
) -> bytes | None:
    """Render a repeating-linear-gradient rectangle to PNG."""
    image = _render_repeating_linear_gradient_image(
        css_gradient,
        width_px,
        height_px,
        border_radius_px=border_radius_px,
    )
    return _encode_png(image) if image is not None else None


def render_linear_gradient_png(
    css_gradient: str,
    width_px: int,
    height_px: int,
    border_radius_px: float = 0.0,
) -> bytes | None:
    """Render a simple linear gradient rectangle to PNG."""
    image = _render_linear_gradient_image(
        css_gradient,
        width_px,
        height_px,
        border_radius_px=border_radius_px,
    )
    return _encode_png(image) if image is not None else None


def _render_linear_gradient_image(
    css_gradient: str,
    width_px: int,
    height_px: int,
    border_radius_px: float = 0.0,
) -> Image.Image | None:
    """Render a simple linear gradient rectangle to a PIL image."""
    parsed = parse_linear_gradient(css_gradient)
    if parsed is None:
        return None

    return _render_linear_gradient_from_parsed(
        parsed, width_px, height_px, border_radius_px
    )


def _render_repeating_linear_gradient_image(
    css_gradient: str,
    width_px: int,
    height_px: int,
    border_radius_px: float = 0.0,
) -> Image.Image | None:
    """Render a repeating linear gradient rectangle to a PIL image.

    The approach expands the declared color stops to cover the full gradient
    line by repeating them cyclically, then renders exactly like a normal
    linear gradient.
    """
    parsed = parse_repeating_linear_gradient(css_gradient)
    if parsed is None:
        return None

    if not parsed.stops:
        return None

    width = max(int(round(width_px)), 1)
    height = max(int(round(height_px)), 1)

    # Resolve px stops to relative positions based on the gradient line length.
    stops = _resolve_px_stops(parsed.stops, parsed.angle_deg, width, height)

    first_position = stops[0].position
    last_position = stops[-1].position

    # Cycle length is the distance between first and last stops.
    cycle = last_position - first_position

    # CSS spec: if cycle is zero or negative (degenerate), the gradient should
    # show the last declared color as a solid fill. Also, when all stops are
    # implicit (distributed across [0, 1]), cycle=1.0 means no repetition;
    # per CSS spec this degenerates to a solid color (the last stop color).
    if cycle <= 1e-9 or cycle >= 1.0 - 1e-9:
        solid_color = stops[-1].color
        expanded_stops = (
            GradientStop(color=solid_color, position=0.0),
            GradientStop(color=solid_color, position=1.0),
        )
        expanded_parsed = ParsedLinearGradient(
            angle_deg=parsed.angle_deg, stops=expanded_stops
        )
        return _render_linear_gradient_from_parsed(
            expanded_parsed, width_px, height_px, border_radius_px
        )

    # Expand stops to fill [0, 1] by repeating the cycle.
    # Use i * cycle + (stop.position - first_position) to avoid floating-point
    # seam accumulation from incremental offsets.
    expanded: list[GradientStop] = []
    num_cycles = max(int(math.ceil(1.0 / cycle)), 1)
    for i in range(num_cycles):
        for stop in stops:
            pos = i * cycle + (stop.position - first_position)
            if pos > 1.0 + 1e-9:
                break
            expanded.append(GradientStop(color=stop.color, position=min(pos, 1.0)))

    if not expanded:
        expanded = list(stops)

    # Ensure we cover 0.0 and 1.0
    if expanded[0].position > 1e-9:
        expanded.insert(0, GradientStop(color=expanded[0].color, position=0.0))
    if expanded[-1].position < 1.0 - 1e-9:
        expanded.append(GradientStop(color=expanded[-1].color, position=1.0))

    expanded_parsed = ParsedLinearGradient(
        angle_deg=parsed.angle_deg, stops=tuple(expanded)
    )

    return _render_linear_gradient_from_parsed(
        expanded_parsed, width_px, height_px, border_radius_px
    )


def _resolve_px_stops(
    stops: tuple[GradientStop, ...],
    angle_deg: float,
    width: int,
    height: int,
) -> tuple[GradientStop, ...]:
    """Convert any px-unit stops to relative [0, 1] positions.

    The gradient line length is computed from the angle and image dimensions,
    matching the CSS spec definition.
    """
    has_px = any(s.unit == "px" for s in stops)
    if not has_px:
        return stops

    # Compute gradient line length per CSS spec.
    radians = math.radians(angle_deg)
    dx = math.sin(radians)
    dy = -math.cos(radians)
    corners = (
        (0.0, 0.0),
        (float(width), 0.0),
        (0.0, float(height)),
        (float(width), float(height)),
    )
    projections = [x * dx + y * dy for x, y in corners]
    grad_line_length = max(max(projections) - min(projections), 1e-6)

    resolved: list[GradientStop] = []
    for stop in stops:
        if stop.unit == "px":
            pos = stop.position / grad_line_length
            resolved.append(GradientStop(color=stop.color, position=pos))
        else:
            resolved.append(GradientStop(color=stop.color, position=stop.position))
    return tuple(resolved)


def _render_linear_gradient_from_parsed(
    parsed: ParsedLinearGradient,
    width_px: int,
    height_px: int,
    border_radius_px: float = 0.0,
) -> Image.Image:
    """Shared rendering logic for linear and repeating-linear gradients."""
    width = max(int(round(width_px)), 1)
    height = max(int(round(height_px)), 1)

    radians = math.radians(parsed.angle_deg)
    dx = math.sin(radians)
    dy = -math.cos(radians)

    corners = ((0.0, 0.0), (1.0, 0.0), (0.0, 1.0), (1.0, 1.0))
    projections = [x * dx + y * dy for x, y in corners]
    min_proj = min(projections)
    max_proj = max(projections)
    span = max(max_proj - min_proj, 1e-6)

    # Build coordinate grids using NumPy
    if width == 1:
        xn = np.full((height, width), 0.5, dtype=np.float64)
    else:
        xn = np.linspace(0.0, 1.0, width, dtype=np.float64).reshape(1, width)
        xn = np.broadcast_to(xn, (height, width))

    if height == 1:
        yn = np.full((height, width), 0.5, dtype=np.float64)
    else:
        yn = np.linspace(0.0, 1.0, height, dtype=np.float64).reshape(height, 1)
        yn = np.broadcast_to(yn, (height, width))

    t_values = ((xn * dx + yn * dy) - min_proj) / span

    rgba = _interpolate_stops_vectorized(parsed.stops, t_values)
    image = Image.fromarray(rgba, "RGBA")

    if border_radius_px > 0:
        mask = Image.new("L", (width, height), 0)
        radius = min(border_radius_px, width / 2, height / 2)
        ImageDraw.Draw(mask).rounded_rectangle(
            (0, 0, width - 1, height - 1),
            radius=int(round(radius)),
            fill=255,
        )
        image.putalpha(mask)

    return image


def parse_radial_gradient(css_gradient: str) -> ParsedRadialGradient | None:
    """Parse a simple CSS radial-gradient() string."""
    gradient = css_gradient.strip()
    if not gradient.lower().startswith("radial-gradient(") or not gradient.endswith(
        ")"
    ):
        return None

    inner = gradient[len("radial-gradient(") : -1]
    parts = _split_top_level_commas(inner)
    if len(parts) < 2:
        return None

    descriptor = parts[0].strip().lower()
    stop_parts = parts
    center_x = 0.5
    center_y = 0.5
    if _looks_like_radial_descriptor(descriptor):
        parsed_center = _parse_radial_center(descriptor)
        if parsed_center is not None:
            center_x, center_y = parsed_center
        stop_parts = parts[1:]

    raw_stops: list[tuple[RGBAColor, float | None, str]] = []
    for part in stop_parts:
        parsed = _parse_gradient_stop(part)
        if parsed is None:
            return None
        raw_stops.append(parsed)

    stops = _resolve_stop_positions(raw_stops)
    return ParsedRadialGradient(
        center_x=center_x,
        center_y=center_y,
        stops=tuple(stops),
    )


def render_radial_gradient_png(
    css_gradient: str,
    width_px: int,
    height_px: int,
    border_radius_px: float = 0.0,
) -> bytes | None:
    """Render a simple radial gradient rectangle to PNG."""
    image = _render_radial_gradient_image(
        css_gradient,
        width_px,
        height_px,
        border_radius_px=border_radius_px,
    )
    return _encode_png(image) if image is not None else None


def _render_radial_gradient_image(
    css_gradient: str,
    width_px: int,
    height_px: int,
    border_radius_px: float = 0.0,
) -> Image.Image | None:
    """Render a simple radial gradient rectangle to a PIL image."""
    parsed = parse_radial_gradient(css_gradient)
    if parsed is None:
        return None

    width = max(int(round(width_px)), 1)
    height = max(int(round(height_px)), 1)

    cx = parsed.center_x
    cy = parsed.center_y
    rx = max(cx, 1.0 - cx, 1e-6)
    ry = max(cy, 1.0 - cy, 1e-6)

    # Build coordinate grids using NumPy
    if width == 1:
        xn = np.full((height, width), 0.5, dtype=np.float64)
    else:
        xn = np.linspace(0.0, 1.0, width, dtype=np.float64).reshape(1, width)
        xn = np.broadcast_to(xn, (height, width))

    if height == 1:
        yn = np.full((height, width), 0.5, dtype=np.float64)
    else:
        yn = np.linspace(0.0, 1.0, height, dtype=np.float64).reshape(height, 1)
        yn = np.broadcast_to(yn, (height, width))

    dx_arr = (xn - cx) / rx
    dy_arr = (yn - cy) / ry
    t_values = np.sqrt(dx_arr * dx_arr + dy_arr * dy_arr)

    rgba = _interpolate_stops_vectorized(parsed.stops, t_values)
    image = Image.fromarray(rgba, "RGBA")

    if border_radius_px > 0:
        mask = Image.new("L", (width, height), 0)
        radius = min(border_radius_px, width / 2, height / 2)
        ImageDraw.Draw(mask).rounded_rectangle(
            (0, 0, width - 1, height - 1),
            radius=int(round(radius)),
            fill=255,
        )
        image.putalpha(mask)

    return image


def render_gradient_png(
    css_gradient: str,
    width_px: int,
    height_px: int,
    border_radius_px: float = 0.0,
) -> bytes | None:
    """Render a supported CSS gradient rectangle to PNG."""
    layers = [
        layer.strip()
        for layer in _split_top_level_commas(css_gradient)
        if layer.strip() and layer.strip().lower() != "none"
    ]
    if not layers:
        return None

    width = max(int(round(width_px)), 1)
    height = max(int(round(height_px)), 1)
    composite = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    rendered_any = False

    for layer in reversed(layers):
        image = _render_gradient_layer_image(
            layer,
            width,
            height,
            border_radius_px=border_radius_px,
        )
        if image is None:
            continue
        composite.alpha_composite(image)
        rendered_any = True

    return _encode_png(composite) if rendered_any else None


def _split_top_level_commas(value: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    depth = 0
    for char in value:
        if char == "(":
            depth += 1
        elif char == ")":
            depth = max(depth - 1, 0)
        if char == "," and depth == 0:
            parts.append("".join(current).strip())
            current = []
            continue
        current.append(char)
    if current:
        parts.append("".join(current).strip())
    return parts


def _looks_like_direction(value: str) -> bool:
    return value.startswith("to ") or value.endswith("deg")


def _looks_like_radial_descriptor(value: str) -> bool:
    normalized = value.strip().lower()
    if not normalized:
        return False
    if "at " in normalized:
        return True
    if normalized.startswith(("circle", "ellipse", "closest-", "farthest-")):
        return True
    return _parse_gradient_stop(normalized) is None


def _parse_gradient_direction(value: str) -> float | None:
    if value.endswith("deg"):
        try:
            return float(value[:-3].strip())
        except ValueError:
            return None

    if not value.startswith("to "):
        return None

    tokens = value[3:].split()
    mapping = {
        ("top",): 0.0,
        ("right",): 90.0,
        ("bottom",): 180.0,
        ("left",): 270.0,
        ("top", "right"): 45.0,
        ("right", "top"): 45.0,
        ("bottom", "right"): 135.0,
        ("right", "bottom"): 135.0,
        ("bottom", "left"): 225.0,
        ("left", "bottom"): 225.0,
        ("top", "left"): 315.0,
        ("left", "top"): 315.0,
    }
    return mapping.get(tuple(tokens))


def _parse_radial_center(value: str) -> tuple[float, float] | None:
    match = re.search(r"\bat\s+([0-9.]+)%\s+([0-9.]+)%", value)
    if match:
        return (
            max(0.0, min(float(match.group(1)) / 100.0, 1.0)),
            max(0.0, min(float(match.group(2)) / 100.0, 1.0)),
        )
    return None


def _parse_gradient_stop(
    value: str,
) -> tuple[RGBAColor, float | None, str] | None:
    """Parse a single gradient stop, returning (color, position, unit).

    *unit* is ``"%"`` for percentage values, ``"px"`` for pixel values,
    or ``"%"`` when position is ``None`` (implicit).
    """
    stop = value.strip()
    if not stop:
        return None

    position: float | None = None
    unit = "%"

    # Try percentage first
    match = re.search(r"\s+([0-9.]+)%\s*$", stop)
    if match:
        position = max(0.0, min(float(match.group(1)) / 100.0, 1.0))
        unit = "%"
        stop = stop[: match.start()].strip()
    else:
        # Try pixel value
        match_px = re.search(r"\s+([0-9.]+)px\s*$", stop)
        if match_px:
            position = float(match_px.group(1))
            unit = "px"
            stop = stop[: match_px.start()].strip()

    color = _try_parse_css_color(stop)
    if color is None:
        return None
    return color, position, unit


def _render_gradient_layer_image(
    css_gradient: str,
    width_px: int,
    height_px: int,
    border_radius_px: float = 0.0,
) -> Image.Image | None:
    gradient = css_gradient.strip().lower()
    if gradient.startswith("linear-gradient("):
        return _render_linear_gradient_image(
            css_gradient,
            width_px,
            height_px,
            border_radius_px=border_radius_px,
        )
    if gradient.startswith("repeating-linear-gradient("):
        return _render_repeating_linear_gradient_image(
            css_gradient,
            width_px,
            height_px,
            border_radius_px=border_radius_px,
        )
    if gradient.startswith("radial-gradient("):
        return _render_radial_gradient_image(
            css_gradient,
            width_px,
            height_px,
            border_radius_px=border_radius_px,
        )
    return None


def _encode_png(image: Image.Image) -> bytes:
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return buf.getvalue()


def _try_parse_css_color(value: str) -> RGBAColor | None:
    normalized = value.strip()
    if not normalized:
        return None
    lower = normalized.lower()
    if re.fullmatch(r"rgba?\([^()]+\)", lower):
        return parse_css_color(normalized)
    if re.fullmatch(r"#[0-9a-f]{3}(?:[0-9a-f]{3})?(?:[0-9a-f]{2})?", lower):
        return parse_css_color(normalized)
    if re.fullmatch(r"[a-z]+", lower):
        return parse_css_color(normalized)
    return None


def _resolve_stop_positions(
    raw_stops: list[tuple[RGBAColor, float | None, str]],
) -> list[GradientStop]:
    count = len(raw_stops)
    if count == 1:
        color, _, unit = raw_stops[0]
        return [
            GradientStop(color=color, position=0.0, unit=unit),
            GradientStop(color=color, position=1.0, unit=unit),
        ]

    positions = [pos for _, pos, _ in raw_stops]
    units = [unit for _, _, unit in raw_stops]

    # Check if any stop uses px – if so, all resolved stops keep px unit
    has_px = any(u == "px" for u in units)
    resolved_unit = "px" if has_px else "%"

    if all(pos is None for pos in positions):
        return [
            GradientStop(color=color, position=index / (count - 1), unit=resolved_unit)
            for index, (color, _, _) in enumerate(raw_stops)
        ]

    if positions[0] is None:
        positions[0] = 0.0
    if positions[-1] is None:
        positions[-1] = 1.0

    last_known = 0
    for index in range(1, count):
        if positions[index] is not None:
            start = positions[last_known]
            end = positions[index]
            assert start is not None and end is not None
            gap = index - last_known
            for fill_index in range(last_known + 1, index):
                ratio = (fill_index - last_known) / gap
                positions[fill_index] = start + (end - start) * ratio
            last_known = index

    resolved: list[GradientStop] = []
    for (color, _, _), position in zip(raw_stops, positions, strict=True):
        resolved.append(
            GradientStop(color=color, position=float(position), unit=resolved_unit)
        )
    return resolved


def _interpolate_stops_vectorized(
    stops: tuple[GradientStop, ...],
    t_values: np.ndarray,
) -> np.ndarray:
    """Vectorized interpolation across all gradient stops.

    Takes a 2-D array of *t* values (shape ``(H, W)``) and returns an
    ``(H, W, 4)`` uint8 RGBA array – no per-pixel Python loop or Pydantic
    construction required.
    """
    shape = t_values.shape
    t = np.clip(t_values, 0.0, 1.0)

    # Pre-extract stop positions and RGBA channels into arrays.
    n_stops = len(stops)
    positions = np.array([s.position for s in stops], dtype=np.float64)
    # Colors: r, g, b as float64 for interpolation; a as float64 [0, 1].
    colors = np.array(
        [[s.color.r, s.color.g, s.color.b, s.color.a] for s in stops],
        dtype=np.float64,
    )

    # For each pixel find the right-side stop index via searchsorted.
    # searchsorted gives the index where t would be inserted to keep order.
    flat_t = t.ravel()
    idx = np.searchsorted(positions, flat_t, side="right")
    # Clamp: if idx==0 use first stop; if idx>=n_stops use last stop.
    idx = np.clip(idx, 1, n_stops - 1)

    lo = idx - 1
    hi = idx

    pos_lo = positions[lo]
    pos_hi = positions[hi]
    span = np.maximum(pos_hi - pos_lo, 1e-6)
    ratio = np.clip((flat_t - pos_lo) / span, 0.0, 1.0)

    # Interpolate each channel.
    c_lo = colors[lo]  # (N, 4)
    c_hi = colors[hi]  # (N, 4)
    ratio_4 = ratio[:, np.newaxis]  # (N, 1) for broadcasting
    interp = c_lo + (c_hi - c_lo) * ratio_4  # (N, 4)

    # Round RGB channels, convert alpha from [0,1] to [0,255].
    result = np.empty_like(interp)
    result[:, 0] = np.round(interp[:, 0])
    result[:, 1] = np.round(interp[:, 1])
    result[:, 2] = np.round(interp[:, 2])
    result[:, 3] = np.round(interp[:, 3] * 255.0)

    return result.reshape(shape[0], shape[1], 4).astype(np.uint8)


def _interpolate_stops(stops: tuple[GradientStop, ...], position: float) -> RGBAColor:
    t = max(0.0, min(position, 1.0))
    if t <= stops[0].position:
        return stops[0].color
    if t >= stops[-1].position:
        return stops[-1].color

    for first, second in zip(stops, stops[1:], strict=False):
        if first.position <= t <= second.position:
            span = max(second.position - first.position, 1e-6)
            ratio = (t - first.position) / span
            return RGBAColor(
                r=round(first.color.r + (second.color.r - first.color.r) * ratio),
                g=round(first.color.g + (second.color.g - first.color.g) * ratio),
                b=round(first.color.b + (second.color.b - first.color.b) * ratio),
                a=first.color.a + (second.color.a - first.color.a) * ratio,
            )

    return stops[-1].color
