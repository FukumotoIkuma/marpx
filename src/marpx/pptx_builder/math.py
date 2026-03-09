"""Editable math equation rendering for pptx_builder."""

from __future__ import annotations

import logging

from lxml import etree
from pptx.util import Emu

from marpx.models import UnsupportedElement
from marpx.utils.common import px_to_emu
from marpx.utils.math import latex_to_omml

_MC_NS = "http://schemas.openxmlformats.org/markup-compatibility/2006"
_A14_NS = "http://schemas.microsoft.com/office/drawing/2010/main"

logger = logging.getLogger(__name__)


def _add_math_equation(slide, element: UnsupportedElement) -> bool:
    """Add an editable math equation to the slide.

    Returns True if successfully added, False if conversion failed
    (caller should fall back to image).
    """
    latex_source = None
    if element.unsupported_info:
        latex_source = element.unsupported_info.latex_source

    if not latex_source:
        return False

    if element.box.width <= 0 or element.box.height <= 0:
        return False

    # Convert LaTeX to OMML
    omml_element = latex_to_omml(latex_source)
    if omml_element is None:
        return False

    # Create textbox at the element's position
    left = Emu(px_to_emu(element.box.x))
    top = Emu(px_to_emu(element.box.y))
    width = Emu(px_to_emu(element.box.width))
    height = Emu(px_to_emu(element.box.height))

    txbox = slide.shapes.add_textbox(left, top, width, height)
    tf = txbox.text_frame
    tf.word_wrap = False

    # Get the first paragraph (auto-created) and inject OMML
    p = tf.paragraphs[0]
    # Wrap in mc:AlternateContent for PowerPoint compatibility
    nsmap_mc = {"mc": _MC_NS, "a14": _A14_NS}
    alt_content = etree.SubElement(
        p._element, f"{{{_MC_NS}}}AlternateContent", nsmap=nsmap_mc
    )
    choice = etree.SubElement(alt_content, f"{{{_MC_NS}}}Choice")
    choice.set("Requires", "a14")
    choice.append(omml_element)

    return True
