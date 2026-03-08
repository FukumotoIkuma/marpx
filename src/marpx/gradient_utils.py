"""Helpers for parsing and rendering simple CSS gradients."""

from __future__ import annotations

import io
import math
import re
from dataclasses import dataclass

from PIL import Image, ImageDraw

from marpx.models import RGBAColor
from marpx.utils import parse_css_color


@dataclass(frozen=True)
class GradientStop:
    color: RGBAColor
    position: float


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

    raw_stops: list[tuple[RGBAColor, float | None]] = []
    for part in stop_parts:
        parsed = _parse_gradient_stop(part)
        if parsed is None:
            return None
        raw_stops.append(parsed)

    stops = _resolve_stop_positions(raw_stops)
    return ParsedLinearGradient(angle_deg=angle_deg, stops=tuple(stops))


def render_linear_gradient_png(
    css_gradient: str,
    width_px: int,
    height_px: int,
    border_radius_px: float = 0.0,
) -> bytes | None:
    """Render a simple linear gradient rectangle to PNG."""
    parsed = parse_linear_gradient(css_gradient)
    if parsed is None:
        return None

    width = max(int(round(width_px)), 1)
    height = max(int(round(height_px)), 1)
    image = Image.new("RGBA", (width, height))

    radians = math.radians(parsed.angle_deg)
    dx = math.sin(radians)
    dy = -math.cos(radians)

    corners = ((0.0, 0.0), (1.0, 0.0), (0.0, 1.0), (1.0, 1.0))
    projections = [x * dx + y * dy for x, y in corners]
    min_proj = min(projections)
    max_proj = max(projections)
    span = max(max_proj - min_proj, 1e-6)

    pixels = image.load()
    for y in range(height):
        yn = 0.5 if height == 1 else y / (height - 1)
        for x in range(width):
            xn = 0.5 if width == 1 else x / (width - 1)
            t = ((xn * dx + yn * dy) - min_proj) / span
            color = _interpolate_stops(parsed.stops, t)
            pixels[x, y] = (
                color.r,
                color.g,
                color.b,
                int(round(color.a * 255)),
            )

    if border_radius_px > 0:
        mask = Image.new("L", (width, height), 0)
        radius = min(border_radius_px, width / 2, height / 2)
        ImageDraw.Draw(mask).rounded_rectangle(
            (0, 0, width - 1, height - 1),
            radius=int(round(radius)),
            fill=255,
        )
        image.putalpha(mask)

    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return buf.getvalue()


def parse_radial_gradient(css_gradient: str) -> ParsedRadialGradient | None:
    """Parse a simple CSS radial-gradient() string."""
    gradient = css_gradient.strip()
    if not gradient.lower().startswith("radial-gradient(") or not gradient.endswith(")"):
        return None

    inner = gradient[len("radial-gradient(") : -1]
    parts = _split_top_level_commas(inner)
    if len(parts) < 2:
        return None

    descriptor = parts[0].strip().lower()
    stop_parts = parts
    center_x = 0.5
    center_y = 0.5
    if "at " in descriptor:
        parsed_center = _parse_radial_center(descriptor)
        if parsed_center is not None:
            center_x, center_y = parsed_center
            stop_parts = parts[1:]

    raw_stops: list[tuple[RGBAColor, float | None]] = []
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
    parsed = parse_radial_gradient(css_gradient)
    if parsed is None:
        return None

    width = max(int(round(width_px)), 1)
    height = max(int(round(height_px)), 1)
    image = Image.new("RGBA", (width, height))
    pixels = image.load()

    cx = parsed.center_x
    cy = parsed.center_y
    rx = max(cx, 1.0 - cx, 1e-6)
    ry = max(cy, 1.0 - cy, 1e-6)

    for y in range(height):
        yn = 0.5 if height == 1 else y / (height - 1)
        dy = (yn - cy) / ry
        for x in range(width):
            xn = 0.5 if width == 1 else x / (width - 1)
            dx = (xn - cx) / rx
            t = math.sqrt((dx * dx) + (dy * dy))
            color = _interpolate_stops(parsed.stops, t)
            pixels[x, y] = (
                color.r,
                color.g,
                color.b,
                int(round(color.a * 255)),
            )

    if border_radius_px > 0:
        mask = Image.new("L", (width, height), 0)
        radius = min(border_radius_px, width / 2, height / 2)
        ImageDraw.Draw(mask).rounded_rectangle(
            (0, 0, width - 1, height - 1),
            radius=int(round(radius)),
            fill=255,
        )
        image.putalpha(mask)

    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return buf.getvalue()


def render_gradient_png(
    css_gradient: str,
    width_px: int,
    height_px: int,
    border_radius_px: float = 0.0,
) -> bytes | None:
    """Render a supported CSS gradient rectangle to PNG."""
    gradient = css_gradient.strip().lower()
    if gradient.startswith("linear-gradient("):
        return render_linear_gradient_png(
            css_gradient,
            width_px,
            height_px,
            border_radius_px=border_radius_px,
        )
    if gradient.startswith("radial-gradient("):
        return render_radial_gradient_png(
            css_gradient,
            width_px,
            height_px,
            border_radius_px=border_radius_px,
        )
    return None


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


def _parse_gradient_stop(value: str) -> tuple[RGBAColor, float | None] | None:
    stop = value.strip()
    if not stop:
        return None

    match = re.search(r"\s+([0-9.]+%)\s*$", stop)
    position = None
    if match:
        position = max(0.0, min(float(match.group(1)[:-1]) / 100.0, 1.0))
        stop = stop[: match.start()].strip()

    return parse_css_color(stop), position


def _resolve_stop_positions(
    raw_stops: list[tuple[RGBAColor, float | None]],
) -> list[GradientStop]:
    count = len(raw_stops)
    if count == 1:
        color, _ = raw_stops[0]
        return [
            GradientStop(color=color, position=0.0),
            GradientStop(color=color, position=1.0),
        ]

    positions = [pos for _, pos in raw_stops]
    if all(pos is None for pos in positions):
        return [
            GradientStop(color=color, position=index / (count - 1))
            for index, (color, _) in enumerate(raw_stops)
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
    for (color, _), position in zip(raw_stops, positions, strict=True):
        resolved.append(GradientStop(color=color, position=float(position)))
    return resolved


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
