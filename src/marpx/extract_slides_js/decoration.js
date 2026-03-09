import { deriveRenderContext, _scaleX, _scaleY, _scaleText } from './render-context.js';
import {
    styleToRunStyle,
    applyOpacityToColor,
    _parseBoxShadow,
    _applyOpacityToGradient,
    getUnsupportedStyleReason,
} from './style.js';

function _parseClipPathPolygon(clipPathStr) {
    if (!clipPathStr || clipPathStr === 'none') return null;
    const match = clipPathStr.match(/^polygon\((.+)\)$/);
    if (!match) return null;
    const pointsStr = match[1];
    const pairs = pointsStr.split(',').map((p) => p.trim()).filter(Boolean);
    const points = [];
    for (const pair of pairs) {
        const parts = pair.split(/\s+/);
        if (parts.length !== 2) return null;
        const parseValue = (token) => {
            if (token.endsWith('%')) {
                return { value: parseFloat(token), unit: '%' };
            }
            if (token.endsWith('px')) {
                return { value: parseFloat(token), unit: 'px' };
            }
            // Bare number — treat as px
            const num = parseFloat(token);
            if (!isNaN(num)) return { value: num, unit: 'px' };
            return null;
        };
        const xParsed = parseValue(parts[0]);
        const yParsed = parseValue(parts[1]);
        if (!xParsed || !yParsed) return null;
        points.push({
            x: xParsed.unit === '%' ? xParsed.value : xParsed.value,
            y: yParsed.unit === '%' ? yParsed.value : yParsed.value,
            xUnit: xParsed.unit,
            yUnit: yParsed.unit,
        });
    }
    if (points.length < 3) return null;
    return { type: 'polygon', points };
}

function _extractDecorationFromComputedStyle(cs, ctx) {
    const backgroundClip = (cs.webkitBackgroundClip || cs.backgroundClip || '').toLowerCase();
    const hasTextClippedGradient = backgroundClip.includes('text');
    const borderSide = (side) => {
        const width = side === 'Left' || side === 'Right'
            ? _scaleX(parseFloat(cs[`border${side}Width`]) || 0, ctx)
            : _scaleY(parseFloat(cs[`border${side}Width`]) || 0, ctx);
        return {
            widthPx: width,
            style: cs[`border${side}Style`] || 'none',
            color: width > 0
                ? applyOpacityToColor(cs[`border${side}Color`], ctx.effectiveOpacity)
                : null,
        };
    };
    return {
        backgroundColor: applyOpacityToColor(cs.backgroundColor, ctx.effectiveOpacity),
        backgroundGradient: !hasTextClippedGradient && cs.backgroundImage && cs.backgroundImage.includes('gradient(')
            ? _applyOpacityToGradient(cs.backgroundImage, ctx.effectiveOpacity)
            : null,
        borderTop: borderSide('Top'),
        borderRight: borderSide('Right'),
        borderBottom: borderSide('Bottom'),
        borderLeft: borderSide('Left'),
        borderRadiusPx: _scaleText(parseFloat(cs.borderTopLeftRadius) || 0, ctx),
        padding: {
            topPx: _scaleY(parseFloat(cs.paddingTop) || 0, ctx),
            rightPx: _scaleX(parseFloat(cs.paddingRight) || 0, ctx),
            bottomPx: _scaleY(parseFloat(cs.paddingBottom) || 0, ctx),
            leftPx: _scaleX(parseFloat(cs.paddingLeft) || 0, ctx),
        },
        boxShadows: _parseBoxShadow(
            cs.boxShadow,
            cs.color || 'rgba(0, 0, 0, 1)',
            ctx,
        ),
        clipPath: _parseClipPathPolygon(cs.clipPath) || undefined,
        opacity: 1,
    };
}

export function extractDecoration(el, renderContext = null) {
    const cs = window.getComputedStyle(el);
    const ctx = renderContext || deriveRenderContext(el, null, cs);
    return _extractDecorationFromComputedStyle(cs, ctx);
}

export function hasMeaningfulDecoration(decoration) {
    const normalizedBg = decoration.backgroundColor
        ? decoration.backgroundColor.replace(/\s+/g, '').toLowerCase()
        : '';
    const hasVisibleBackground = normalizedBg &&
        normalizedBg !== 'rgba(0,0,0,0)' &&
        normalizedBg !== 'transparent';
    const hasGradientBackground = !!(
        decoration.backgroundGradient &&
        decoration.backgroundGradient !== 'none'
    );
    const hasBoxShadow = (decoration.boxShadows || []).some((shadow) => {
        if (shadow.inset || !shadow.color) return false;
        const normalized = shadow.color.replace(/\s+/g, '').toLowerCase();
        return (
            normalized !== 'transparent' &&
            normalized !== 'rgba(0,0,0,0)' &&
            normalized !== 'rgb(0,0,0,0)'
        );
    });
        const borders = [
            decoration.borderTop,
            decoration.borderRight,
            decoration.borderBottom,
            decoration.borderLeft,
        ];
        const hasVisibleBorder = borders.some(
            (b) => b.widthPx > 0 && b.style && b.style !== 'none'
        );
        const hasRadius = decoration.borderRadiusPx > 0;
    return (
        hasVisibleBackground ||
        hasGradientBackground ||
        hasVisibleBorder ||
        hasRadius ||
        hasBoxShadow
    );
}

export function normalizeContentValue(content) {
    if (!content || content === 'none' || content === 'normal') return null;
    if (
        (content.startsWith('"') && content.endsWith('"')) ||
        (content.startsWith("'") && content.endsWith("'"))
    ) {
        try {
            return JSON.parse(content);
        } catch (_err) {
            return content.slice(1, -1);
        }
    }
    return content;
}

export function extractPseudoRuns(el, pseudo, renderContext = null) {
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
 * **Why this workaround is needed:**
 * Browsers do not expose geometry (position, size) for pseudo-elements through
 * any standard DOM API. `getComputedStyle(el, '::before')` returns *style*
 * properties (colors, fonts, dimensions as authored) but there is no equivalent
 * of `getBoundingClientRect()` for pseudo-elements — they are not real DOM nodes.
 *
 * **What this workaround does:**
 * 1. Reads the full computed style of the target pseudo-element.
 * 2. Creates a temporary "probe" DOM element (`<span>` for text content,
 *    `<div>` for purely decorative pseudo-elements).
 * 3. Copies all layout-affecting and visual CSS properties from the
 *    pseudo-element's computed style onto the probe.
 * 4. Appends the probe as a child of the original element so it participates
 *    in the same containing-block / positioning context.
 * 5. Calls `getBoundingClientRect()` on the probe to obtain real geometry.
 * 6. Immediately removes the probe from the DOM to avoid side effects.
 *
 * **Known limitations:**
 * - The probe is appended as a *child* of `el`, not inserted at the exact
 *   position where the browser places the pseudo-element. For absolutely/fixed
 *   positioned pseudo-elements (the only ones this function is called for),
 *   this is acceptable because their position is determined by the containing
 *   block, not document flow.
 * - Complex `content` values (e.g. `counter()`, `attr()`, images) are not
 *   fully replicated; only the resolved text string is used.
 * - CSS properties not explicitly copied (e.g. `clip`, `filter`) may cause
 *   minor measurement discrepancies.
 *
 * @param {Element} el      - The parent DOM element that owns the pseudo-element.
 * @param {string}  pseudo  - The pseudo-element selector, e.g. `'::before'` or `'::after'`.
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

export function extractBlockPseudoElements(el, sectionRect, renderContext = null) {
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

// Private helpers used by extractBlockPseudoElements
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
