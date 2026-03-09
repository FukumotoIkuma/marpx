import { deriveRenderContext, _scaleX, _scaleY, _scaleText } from './render-context.js';
import {
    applyOpacityToColor,
    _parseBoxShadow,
    _applyOpacityToGradient,
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

export function _extractDecorationFromComputedStyle(cs, ctx) {
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
