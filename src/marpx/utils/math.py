"""LaTeX to OMML conversion for editable PowerPoint equations."""

from __future__ import annotations

import logging
from pathlib import Path

from lxml import etree

logger = logging.getLogger(__name__)

# Path to the bundled MML2OMML XSLT stylesheet
_XSL_PATH = Path(__file__).parent / "MML2OMML.XSL"

# OMML namespace
_OMML_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
_A14_NS = "http://schemas.microsoft.com/office/drawing/2010/main"

# Lazy-loaded XSLT transform
_xslt_transform: etree.XSLT | None = None


def _get_xslt_transform() -> etree.XSLT:
    """Load and cache the MML2OMML XSLT transform."""
    global _xslt_transform
    if _xslt_transform is None:
        xslt_doc = etree.parse(str(_XSL_PATH))
        _xslt_transform = etree.XSLT(xslt_doc)
    return _xslt_transform


def latex_to_omml(latex: str) -> etree._Element | None:
    """Convert LaTeX string to OMML element for PowerPoint.

    Returns an <a14:m> element containing
    <m:oMathPara><m:oMath>...</m:oMath></m:oMathPara>,
    or None if conversion fails.
    """
    try:
        import latex2mathml.converter

        # Step 1: LaTeX -> MathML
        mathml_str = latex2mathml.converter.convert(latex)

        # Step 2: Parse MathML
        mathml_tree = etree.fromstring(mathml_str.encode("utf-8"))

        # Step 3: MathML -> OMML via XSLT
        transform = _get_xslt_transform()
        omml_tree = transform(mathml_tree)
        omml_root = omml_tree.getroot()
        if omml_root is None:
            logger.warning("XSLT produced empty result for: %s", latex)
            return None

        # Step 4: Wrap in a14:m > m:oMathPara
        # The XSLT produces m:oMath or m:oMathPara depending on input
        # We need: <a14:m><m:oMathPara><m:oMath>...</m:oMath></m:oMathPara></a14:m>

        nsmap = {"a14": _A14_NS, "m": _OMML_NS}
        a14_m = etree.Element(f"{{{_A14_NS}}}m", nsmap=nsmap)

        # Check if result is already oMathPara
        if omml_root.tag == f"{{{_OMML_NS}}}oMathPara":
            a14_m.append(omml_root)
        elif omml_root.tag == f"{{{_OMML_NS}}}oMath":
            omath_para = etree.SubElement(a14_m, f"{{{_OMML_NS}}}oMathPara")
            omath_para.append(omml_root)
        else:
            # Wrap in both
            omath_para = etree.SubElement(a14_m, f"{{{_OMML_NS}}}oMathPara")
            omath = etree.SubElement(omath_para, f"{{{_OMML_NS}}}oMath")
            for child in list(omml_root):
                omath.append(child)

        return a14_m

    except ImportError:
        logger.warning("latex2mathml not installed, cannot convert: %s", latex)
        return None
    except (etree.Error, etree.XSLTError) as exc:
        logger.warning(
            "Failed to convert LaTeX to OMML (XML/XSLT): %s (%s)", latex, exc
        )
        return None
    except (ValueError, TypeError) as exc:
        logger.warning("Failed to convert LaTeX to OMML: %s (%s)", latex, exc)
        return None
    except Exception as exc:
        # Catch latex2mathml-specific errors (NoAvailableTokensError, etc.)
        mod = type(exc).__module__ or ""
        if mod.startswith("latex2mathml"):
            logger.warning("Failed to convert LaTeX to OMML: %s (%s)", latex, exc)
            return None
        raise
