"""Helpers for approximating CSS 3D transforms using PowerPoint scene3d."""

from __future__ import annotations

import math

from marpx.models import Box, Point


def css_perspective_to_ooxml_fov(
    perspective_px: float, element_height_px: float
) -> int:
    """Convert CSS perspective distance to OOXML camera fov value.

    PowerPoint's fov is vertical field of view in 60,000ths of a degree.
    CSS perspective(d) sets viewer distance to d pixels from the z=0 plane.
    """
    if perspective_px <= 0 or element_height_px <= 0:
        return 0
    fov_rad = 2 * math.atan(element_height_px / (2 * perspective_px))
    fov_deg = math.degrees(fov_rad)
    # Clamp to PowerPoint's valid range (roughly 0.57° to 179.43°)
    fov_deg = max(0.57, min(fov_deg, 179.43))
    return int(round(fov_deg * 60000))


def _deg_to_rad(value: float) -> float:
    return value * math.pi / 180.0


def _rotate_xyz(
    x: float,
    y: float,
    z: float,
    rotation_x_deg: float,
    rotation_y_deg: float,
    rotation_z_deg: float,
) -> tuple[float, float, float]:
    rx = _deg_to_rad(rotation_x_deg)
    ry = _deg_to_rad(rotation_y_deg)
    rz = _deg_to_rad(rotation_z_deg)

    # X
    cos_x = math.cos(rx)
    sin_x = math.sin(rx)
    y, z = (y * cos_x) - (z * sin_x), (y * sin_x) + (z * cos_x)

    # Y
    cos_y = math.cos(ry)
    sin_y = math.sin(ry)
    x, z = (x * cos_y) + (z * sin_y), (-x * sin_y) + (z * cos_y)

    # Z
    cos_z = math.cos(rz)
    sin_z = math.sin(rz)
    x, y = (x * cos_z) - (y * sin_z), (x * sin_z) + (y * cos_z)

    return x, y, z


def _project_rotated_rect(
    width: float,
    height: float,
    rotation_x_deg: float,
    rotation_y_deg: float,
    rotation_z_deg: float,
) -> list[tuple[float, float]]:
    corners = [
        (-width / 2.0, -height / 2.0, 0.0),
        (width / 2.0, -height / 2.0, 0.0),
        (width / 2.0, height / 2.0, 0.0),
        (-width / 2.0, height / 2.0, 0.0),
    ]
    projected: list[tuple[float, float]] = []
    for x, y, z in corners:
        px, py, _pz = _rotate_xyz(
            x,
            y,
            z,
            rotation_x_deg,
            rotation_y_deg,
            rotation_z_deg,
        )
        projected.append((px, py))
    return projected


def _normalize_points(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    min_x = min(x for x, _ in points)
    max_x = max(x for x, _ in points)
    min_y = min(y for _, y in points)
    max_y = max(y for _, y in points)
    width = max(max_x - min_x, 1e-6)
    height = max(max_y - min_y, 1e-6)
    return [((x - min_x) / width, (y - min_y) / height) for x, y in points]


def _normalize_target_to_box(
    projected_corners: list[Point],
    box: Box,
) -> list[tuple[float, float]]:
    width = max(box.width, 1e-6)
    height = max(box.height, 1e-6)
    return [
        ((corner.x - box.x) / width, (corner.y - box.y) / height)
        for corner in projected_corners
    ]


def _quad_error(
    candidate: list[tuple[float, float]],
    target: list[tuple[float, float]],
) -> float:
    total = 0.0
    for (cx, cy), (tx, ty) in zip(candidate, target, strict=False):
        dx = cx - tx
        dy = cy - ty
        total += (dx * dx) + (dy * dy)
    return total


def fit_scene3d_rotations(
    projected_corners: list[Point],
    box: Box,
    fallback_x_deg: float = 0.0,
    fallback_y_deg: float = 0.0,
    fallback_z_deg: float = 0.0,
) -> tuple[float, float, float]:
    """Fit PowerPoint scene3d rotations to an extracted CSS projected quad."""
    if len(projected_corners) != 4 or box.width <= 0 or box.height <= 0:
        return fallback_x_deg, fallback_y_deg, fallback_z_deg

    target = _normalize_target_to_box(projected_corners, box)

    best_x = fallback_x_deg
    best_y = fallback_y_deg
    best_z = fallback_z_deg
    best_error = float("inf")

    def search(
        x_center: float,
        y_center: float,
        z_center: float,
        x_span: float,
        y_span: float,
        z_span: float,
        step: float,
    ) -> None:
        nonlocal best_x, best_y, best_z, best_error
        x = x_center - x_span
        while x <= x_center + x_span + 1e-6:
            y = y_center - y_span
            while y <= y_center + y_span + 1e-6:
                z = z_center - z_span
                while z <= z_center + z_span + 1e-6:
                    projected = _project_rotated_rect(box.width, box.height, x, y, z)
                    normalized = _normalize_points(projected)
                    error = _quad_error(normalized, target)
                    if error < best_error:
                        best_error = error
                        best_x = x
                        best_y = y
                        best_z = z
                    z += step
                y += step
            x += step

    search(fallback_x_deg, fallback_y_deg, fallback_z_deg, 70, 70, 90, 10)
    search(best_x, best_y, best_z, 12, 12, 20, 2)
    search(best_x, best_y, best_z, 3, 3, 6, 1)

    return best_x, best_y, best_z
