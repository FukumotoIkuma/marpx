import { deriveRenderContext, _scaleX, _scaleY, _scaleText } from './render-context.js';
import {
    styleToRunStyle,
    applyOpacityToColor,
    getUnsupportedStyleReason,
} from './style.js';
import {
    _extractDecorationFromComputedStyle,
    hasMeaningfulDecoration,
    normalizeContentValue,
} from './decoration.js';

/**
 * WeakSet to track elements whose block pseudo-elements have already been
 * extracted. Prevents double-processing when both main.js (slide-level) and
 * handlers.js (element-level) call extractBlockPseudoElements on the same node.
 */
const _processedBlockPseudo = new WeakSet();

/**
 * Quick check whether an element has visible pseudo-element content on the
 * given side (::before or ::after) without performing full extraction.
 *
 * @param {Element} el    - The DOM element to check.
 * @param {string}  side  - The pseudo-element selector, e.g. '::before' or '::after'.
 * @returns {boolean} True if the pseudo-element has non-empty content.
 */
export function hasPseudoContent(el, side) {
    const cs = window.getComputedStyle(el, side);
    return !!normalizeContentValue(cs.content);
}

/**
 * Extract inline pseudo-element text runs for prepending/appending to a
 * parent element's run list. Only extracts non-positioned pseudo-elements
 * (i.e. skips absolute/fixed which are handled as block pseudo-elements).
 *
 * Moved from decoration.js extractPseudoRuns().
 *
 * @param {Element}      el            - The parent DOM element.
 * @param {string}       pseudo        - '::before' or '::after'.
 * @param {object|null}  renderContext - Optional render context.
 * @returns {Array} Array of run objects [{text, style, linkUrl}].
 */
export function getInlinePseudoRuns(el, pseudo, renderContext = null) {
    const cs = window.getComputedStyle(el, pseudo);
    if (['absolute', 'fixed'].includes(cs.position)) return [];
    const content = normalizeContentValue(cs.content);
    if (!content) return [];
    const ctx = renderContext || deriveRenderContext(el);
    return [{
        text: content,
        style: styleToRunStyle(cs, el, ctx),
        linkUrl: null,
    }];
}

/**
 * Backward-compatible alias for getInlinePseudoRuns.
 * Preserves the original extractPseudoRuns signature so existing callers
 * (runs.js, containers.js) do not need to change their call sites.
 */
export const extractPseudoRuns = getInlinePseudoRuns;

// --- Block pseudo-element helpers (moved from decoration.js) ---

function _parsePseudoZIndex(cs, fallbackZ) {
    const parsed = parseInt(cs.zIndex, 10);
    return Number.isFinite(parsed) ? parsed : fallbackZ;
}

function _buildPseudoParagraph(content, cs, el, ctx) {
    return [{
        runs: [{
            text: content,
            style: styleToRunStyle(cs, el, ctx),
            linkUrl: null,
        }],
        alignment: cs.textAlign || 'left',
        lineHeightPx: parseFloat(cs.lineHeight) || null,
        spaceBeforePx: 0,
        spaceAfterPx: 0,
    }];
}

/**
 * Measures the bounding rectangle of a CSS pseudo-element (::before / ::after).
 *
 * Browsers do not expose geometry for pseudo-elements through any standard DOM
 * API. This workaround creates a temporary probe element that mimics the
 * pseudo-element's computed style, measures it via getBoundingClientRect(),
 * and immediately removes it.
 *
 * @param {Element} el      - The parent DOM element that owns the pseudo-element.
 * @param {string}  pseudo  - The pseudo-element selector, e.g. '::before' or '::after'.
 * @param {string}  content - The resolved text content of the pseudo-element.
 * @returns {DOMRect} The bounding client rect of the measured probe element.
 */
function _measurePseudoRect(el, pseudo, content) {
    const pseudoCs = window.getComputedStyle(el, pseudo);
    const probe = document.createElement(content ? 'span' : 'div');
    probe.textContent = content || '';
    probe.setAttribute('aria-hidden', 'true');
    probe.style.position = pseudoCs.position;
    probe.style.display = content ? 'inline-block' : 'block';
    probe.style.visibility = 'hidden';
    probe.style.pointerEvents = 'none';
    probe.style.margin = '0';
    probe.style.left = pseudoCs.left;
    probe.style.right = pseudoCs.right;
    probe.style.top = pseudoCs.top;
    probe.style.bottom = pseudoCs.bottom;
    probe.style.width = pseudoCs.width;
    probe.style.height = pseudoCs.height;
    probe.style.minWidth = pseudoCs.minWidth;
    probe.style.minHeight = pseudoCs.minHeight;
    probe.style.maxWidth = pseudoCs.maxWidth;
    probe.style.maxHeight = pseudoCs.maxHeight;
    probe.style.boxSizing = pseudoCs.boxSizing;
    probe.style.paddingTop = pseudoCs.paddingTop;
    probe.style.paddingRight = pseudoCs.paddingRight;
    probe.style.paddingBottom = pseudoCs.paddingBottom;
    probe.style.paddingLeft = pseudoCs.paddingLeft;
    probe.style.borderTopWidth = pseudoCs.borderTopWidth;
    probe.style.borderRightWidth = pseudoCs.borderRightWidth;
    probe.style.borderBottomWidth = pseudoCs.borderBottomWidth;
    probe.style.borderLeftWidth = pseudoCs.borderLeftWidth;
    probe.style.borderTopStyle = pseudoCs.borderTopStyle;
    probe.style.borderRightStyle = pseudoCs.borderRightStyle;
    probe.style.borderBottomStyle = pseudoCs.borderBottomStyle;
    probe.style.borderLeftStyle = pseudoCs.borderLeftStyle;
    probe.style.borderTopColor = pseudoCs.borderTopColor;
    probe.style.borderRightColor = pseudoCs.borderRightColor;
    probe.style.borderBottomColor = pseudoCs.borderBottomColor;
    probe.style.borderLeftColor = pseudoCs.borderLeftColor;
    probe.style.borderTopLeftRadius = pseudoCs.borderTopLeftRadius;
    probe.style.borderTopRightRadius = pseudoCs.borderTopRightRadius;
    probe.style.borderBottomRightRadius = pseudoCs.borderBottomRightRadius;
    probe.style.borderBottomLeftRadius = pseudoCs.borderBottomLeftRadius;
    probe.style.backgroundColor = pseudoCs.backgroundColor;
    probe.style.backgroundImage = pseudoCs.backgroundImage;
    probe.style.color = pseudoCs.color;
    probe.style.fontFamily = pseudoCs.fontFamily;
    probe.style.fontSize = pseudoCs.fontSize;
    probe.style.fontWeight = pseudoCs.fontWeight;
    probe.style.fontStyle = pseudoCs.fontStyle;
    probe.style.lineHeight = pseudoCs.lineHeight;
    probe.style.letterSpacing = pseudoCs.letterSpacing;
    probe.style.whiteSpace = pseudoCs.whiteSpace;
    probe.style.textAlign = pseudoCs.textAlign;
    probe.style.transform = pseudoCs.transform;
    probe.style.transformOrigin = pseudoCs.transformOrigin;
    probe.style.opacity = pseudoCs.opacity;
    el.appendChild(probe);
    const rect = probe.getBoundingClientRect();
    probe.remove();
    return rect;
}

function _getZIndex(el) {
    const raw = window.getComputedStyle(el).zIndex;
    const parsed = parseInt(raw, 10);
    return Number.isFinite(parsed) ? parsed : 0;
}

function _boxFromRect(rect, sectionRect) {
    return {
        x: rect.left - sectionRect.left,
        y: rect.top - sectionRect.top,
        width: rect.width,
        height: rect.height,
    };
}

function _contentBoxFromRectAndStyle(rect, cs, sectionRect, ctx) {
    const leftInset = _scaleX((parseFloat(cs.borderLeftWidth) || 0) + (parseFloat(cs.paddingLeft) || 0), ctx);
    const topInset = _scaleY((parseFloat(cs.borderTopWidth) || 0) + (parseFloat(cs.paddingTop) || 0), ctx);
    const rightInset = _scaleX((parseFloat(cs.borderRightWidth) || 0) + (parseFloat(cs.paddingRight) || 0), ctx);
    const bottomInset = _scaleY((parseFloat(cs.borderBottomWidth) || 0) + (parseFloat(cs.paddingBottom) || 0), ctx);
    return {
        x: rect.left - sectionRect.left + leftInset,
        y: rect.top - sectionRect.top + topInset,
        width: Math.max(rect.width - leftInset - rightInset, 1),
        height: Math.max(rect.height - topInset - bottomInset, 1),
    };
}

/**
 * Extract positioned (absolute/fixed) pseudo-elements as separate slide
 * elements (decorated blocks or unsupported). These are fundamentally
 * different from inline pseudo-elements — they render as independent
 * visual elements on the slide (decorative bars, accents, etc.).
 *
 * Includes a deduplication guard: if this function has already been called
 * for a given element, subsequent calls return an empty array. This prevents
 * double-processing when both main.js (slide section level) and handlers.js
 * (per-element level) invoke this function on the same DOM node.
 *
 * Moved from decoration.js extractBlockPseudoElements().
 *
 * @param {Element}      el            - The DOM element to inspect.
 * @param {DOMRect}      sectionRect   - The slide's bounding rect for coordinate calculation.
 * @param {object|null}  renderContext - Optional render context.
 * @returns {Array} Array of slide element objects.
 */
export function extractBlockPseudoElements(el, sectionRect, renderContext = null) {
    // Deduplication guard: skip if already processed
    if (_processedBlockPseudo.has(el)) return [];
    _processedBlockPseudo.add(el);

    const results = [];
    const parentZ = _getZIndex(el);
    const ctx = renderContext || deriveRenderContext(el);
    const baseZ = (ctx.baseZIndex || 0);
    for (const pseudo of ['::before', '::after']) {
        const cs = window.getComputedStyle(el, pseudo);
        const content = normalizeContentValue(cs.content) || '';
        const unsupportedReason = getUnsupportedStyleReason(cs);
        if (!['absolute', 'fixed'].includes(cs.position)) continue;
        const decoration = _extractDecorationFromComputedStyle(cs, ctx);
        const hasText = content.length > 0;
        if (!hasText && !hasMeaningfulDecoration(decoration) && !unsupportedReason) continue;

        const rect = _measurePseudoRect(el, pseudo, content);
        if (rect.width <= 0 || rect.height <= 0) continue;

        if (unsupportedReason) {
            results.push({
                type: 'unsupported',
                box: _boxFromRect(rect, sectionRect),
                zIndex: baseZ + _parsePseudoZIndex(cs, parentZ),
                unsupportedInfo: {
                    reason: unsupportedReason,
                    tagName: 'pseudo',
                },
            });
            continue;
        }

        results.push({
            type: 'decorated_block',
            box: _boxFromRect(rect, sectionRect),
            contentBox: hasMeaningfulDecoration(decoration)
                ? _contentBoxFromRectAndStyle(rect, cs, sectionRect, ctx)
                : null,
            zIndex: baseZ + _parsePseudoZIndex(cs, parentZ),
            paragraphs: hasText ? _buildPseudoParagraph(content, cs, el, ctx) : [],
            decoration: hasMeaningfulDecoration(decoration) ? decoration : null,
        });
    }
    return results;
}
