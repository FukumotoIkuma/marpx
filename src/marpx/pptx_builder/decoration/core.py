"""Orchestrator and 3D transform helpers for decoration rendering."""

from __future__ import annotations

from lxml import etree
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
from pptx.oxml.ns import qn

from marpx.models import BaseSlideElement, Box, BoxDecoration
from ..scene3d import fit_scene3d_rotations

from .borders import (
    _apply_left_accent_bar,
    _apply_uniform_border,
    _add_side_border_shapes,
    _detect_uniform_border,
    _is_left_accent_only,
)
from .shadows import _create_inset_shadow_shapes, _create_outer_shadow_shapes
from .shapes import _create_background_shape


def _normalize_positive_fixed_angle(angle_deg: float) -> int:
    """Convert degrees to a positive OOXML fixed-angle value."""
    normalized = angle_deg % 360.0
    normalized = (normalized + 360.0) % 360.0  # Ensure positive
    return int(round(normalized * 60000))


def _apply_scene3d(
    sp_pr,
    rotation_3d_x_deg: float = 0.0,
    rotation_3d_y_deg: float = 0.0,
    rotation_3d_z_deg: float = 0.0,
) -> None:
    """Apply PowerPoint 3D scene rotation to a shape properties node."""
    if (
        abs(rotation_3d_x_deg) <= 0.01
        and abs(rotation_3d_y_deg) <= 0.01
        and abs(rotation_3d_z_deg) <= 0.01
    ):
        return

    scene3d = sp_pr.find(qn("a:scene3d"))
    if scene3d is not None:
        sp_pr.remove(scene3d)

    scene3d = etree.SubElement(sp_pr, qn("a:scene3d"))
    camera = etree.SubElement(scene3d, qn("a:camera"))
    camera.set("prst", "orthographicFront")
    rot = etree.SubElement(camera, qn("a:rot"))
    rot.set("lat", str(_normalize_positive_fixed_angle(rotation_3d_y_deg)))
    rot.set("lon", str(_normalize_positive_fixed_angle(rotation_3d_x_deg)))
    rot.set("rev", str(_normalize_positive_fixed_angle(rotation_3d_z_deg)))
    light_rig = etree.SubElement(scene3d, qn("a:lightRig"))
    light_rig.set("rig", "threePt")
    light_rig.set("dir", "t")


def _resolve_scene3d_rotations(element: BaseSlideElement) -> tuple[float, float, float]:
    """Return fitted scene3d angles when projected corners are available."""
    has_explicit_3d_rotation = (
        abs(element.rotation_3d_x_deg) > 0.01
        or abs(element.rotation_3d_y_deg) > 0.01
        or abs(element.rotation_3d_z_deg) > 0.01
    )
    if has_explicit_3d_rotation and element.projected_corners:
        return fit_scene3d_rotations(
            element.projected_corners,
            element.box,
            fallback_x_deg=element.rotation_3d_x_deg,
            fallback_y_deg=element.rotation_3d_y_deg,
            fallback_z_deg=element.rotation_3d_z_deg,
        )
    return (
        element.rotation_3d_x_deg,
        element.rotation_3d_y_deg,
        element.rotation_3d_z_deg,
    )


def _add_decoration_shape(
    slide,
    box: Box,
    decoration: BoxDecoration,
    *,
    rotation_3d_x_deg: float = 0.0,
    rotation_3d_y_deg: float = 0.0,
    rotation_3d_z_deg: float = 0.0,
):
    """Render a generic decorated box and return it as the text container."""
    shape_type = (
        MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE
        if decoration.border_radius_px > 0
        else MSO_AUTO_SHAPE_TYPE.RECTANGLE
    )

    _create_outer_shadow_shapes(slide, box, decoration, shape_type)

    bg_shape = _create_background_shape(slide, box, decoration, shape_type)

    uniform_border = _detect_uniform_border(decoration)
    _apply_uniform_border(slide, box, decoration, shape_type, bg_shape, uniform_border)

    _apply_scene3d(
        bg_shape._element.spPr,
        rotation_3d_x_deg=rotation_3d_x_deg,
        rotation_3d_y_deg=rotation_3d_y_deg,
        rotation_3d_z_deg=rotation_3d_z_deg,
    )

    accent_border = decoration.border_left
    if (
        accent_border.width_px > 0
        and accent_border.color is not None
        and decoration.opacity > 0
        and _is_left_accent_only(decoration)
    ):
        _apply_left_accent_bar(
            slide,
            box,
            decoration,
            rotation_3d_x_deg=rotation_3d_x_deg,
            rotation_3d_y_deg=rotation_3d_y_deg,
            rotation_3d_z_deg=rotation_3d_z_deg,
        )
    elif not uniform_border:
        _add_side_border_shapes(
            slide,
            box,
            decoration,
            rotation_3d_x_deg=rotation_3d_x_deg,
            rotation_3d_y_deg=rotation_3d_y_deg,
            rotation_3d_z_deg=rotation_3d_z_deg,
        )

    _create_inset_shadow_shapes(slide, box, decoration, shape_type)

    return bg_shape
