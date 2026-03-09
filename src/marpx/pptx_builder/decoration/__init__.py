"""Decoration shape rendering package for pptx_builder."""

from .core import _add_decoration_shape, _resolve_scene3d_rotations
from .shapes import _apply_round_rect_radius_to_geom

__all__ = [
    "_add_decoration_shape",
    "_resolve_scene3d_rotations",
    "_apply_round_rect_radius_to_geom",
]
