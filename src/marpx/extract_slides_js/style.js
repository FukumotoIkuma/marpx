import { deriveRenderContext, _scaleX, _scaleY, _scaleText } from './render-context.js';

export function _parseCssColor(color) {
    if (!color) return null;
    const normalized = color.trim().toLowerCase();
    if (!normalized || normalized === 'transparent') {
        return { r: 0, g: 0, b: 0, a: 0 };
    }

    const match = normalized.match(
        /^rgba?\(\s*([0-9.]+)\s*,\s*([0-9.]+)\s*,\s*([0-9.]+)(?:\s*[,/]\s*([0-9.]+))?\s*\)$/
    );
    if (!match) return null;

    return {
        r: Math.max(0, Math.min(parseFloat(match[1]), 255)),
        g: Math.max(0, Math.min(parseFloat(match[2]), 255)),
        b: Math.max(0, Math.min(parseFloat(match[3]), 255)),
        a: match[4] === undefined ? 1 : Math.max(0, Math.min(parseFloat(match[4]), 1)),
    };
}

export function applyOpacityToColor(color, opacity) {
    const parsed = _parseCssColor(color);
    if (!parsed) return color;
    const alpha = Math.max(0, Math.min(parsed.a * opacity, 1));
    return `rgba(${parsed.r}, ${parsed.g}, ${parsed.b}, ${alpha})`;
}

function _isTransparentTextFill(cs) {
    const textFill = _parseCssColor(cs.webkitTextFillColor || '');
    if (textFill) return textFill.a === 0;
    const color = _parseCssColor(cs.color || '');
    return !!color && color.a === 0;
}

function _extractTextGradient(cs, ctx) {
    const backgroundClip = (cs.webkitBackgroundClip || cs.backgroundClip || '').toLowerCase();
    if (
        backgroundClip.includes('text') &&
        cs.backgroundImage &&
        cs.backgroundImage.includes('gradient(') &&
        _isTransparentTextFill(cs)
    ) {
        return _applyOpacityToGradient(cs.backgroundImage, ctx.effectiveOpacity);
    }
    return null;
}

export function getUnsupportedStyleReason(cs) {
    const filter = cs.filter || '';
    if (filter && filter !== 'none') {
        return 'CSS filter';
    }

    return null;
}

function _splitTopLevelCommas(value) {
    const parts = [];
    let current = '';
    let depth = 0;
    for (const char of value) {
        if (char === '(') depth += 1;
        if (char === ')') depth = Math.max(depth - 1, 0);
        if (char === ',' && depth === 0) {
            parts.push(current.trim());
            current = '';
            continue;
        }
        current += char;
    }
    if (current.trim()) parts.push(current.trim());
    return parts;
}

function _extractRepresentativeGradientColor(backgroundImage) {
    if (!backgroundImage || !backgroundImage.includes('gradient(')) return null;
    const open = backgroundImage.indexOf('(');
    const close = backgroundImage.lastIndexOf(')');
    if (open < 0 || close <= open) return null;
    const inner = backgroundImage.slice(open + 1, close);
    const parts = _splitTopLevelCommas(inner);
    const stopParts = parts.filter((part, index) => {
        const lowered = part.trim().toLowerCase();
        if (index === 0 && (lowered.startsWith('to ') || lowered.endsWith('deg') || lowered.startsWith('at '))) {
            return false;
        }
        return true;
    });
    if (stopParts.length === 0) return null;
    const firstStop = stopParts[0].replace(/\s+[0-9.]+%\s*$/, '').trim();
    return firstStop || null;
}

function _applyOpacityToGradient(backgroundImage, opacity) {
    if (!backgroundImage || !backgroundImage.includes('gradient(')) return backgroundImage;
    const open = backgroundImage.indexOf('(');
    const close = backgroundImage.lastIndexOf(')');
    if (open < 0 || close <= open) return backgroundImage;
    const fnName = backgroundImage.slice(0, open);
    const inner = backgroundImage.slice(open + 1, close);
    const parts = _splitTopLevelCommas(inner);
    const rewritten = parts.map((part, index) => {
        const lowered = part.trim().toLowerCase();
        if (index === 0 && (lowered.startsWith('to ') || lowered.endsWith('deg') || lowered.startsWith('at '))) {
            return part.trim();
        }
        const match = part.match(/^(.*?)(\s+[0-9.]+%\s*)?$/);
        if (!match) return part.trim();
        const colorPart = match[1].trim();
        const positionPart = match[2] || '';
        return `${applyOpacityToColor(colorPart, opacity)}${positionPart}`;
    });
    return `${fnName}(${rewritten.join(', ')})`;
}

function _splitTopLevelSpaces(value) {
    const parts = [];
    let current = '';
    let depth = 0;
    for (const char of value) {
        if (char === '(') depth += 1;
        if (char === ')') depth = Math.max(depth - 1, 0);
        if (/\s/.test(char) && depth === 0) {
            if (current) {
                parts.push(current);
                current = '';
            }
            continue;
        }
        current += char;
    }
    if (current) parts.push(current);
    return parts;
}

function _isCssLengthToken(token) {
    return /^-?(?:\d+|\d*\.\d+)(?:px|r?em|%|pt)?$/i.test(token);
}

function _resolveCssColorToken(token, fallbackColor) {
    if (!token) return fallbackColor;
    const probe = document.createElement('span');
    probe.style.color = '';
    probe.style.color = token;
    if (!probe.style.color) return fallbackColor;
    return probe.style.color;
}

export function _parseBoxShadow(boxShadow, fallbackColor, ctx) {
    if (!boxShadow || boxShadow === 'none') return [];
    return _splitTopLevelCommas(boxShadow)
        .map((shadowValue) => {
            const tokens = _splitTopLevelSpaces(shadowValue);
            if (tokens.length < 2) return null;

            let inset = false;
            const lengthTokens = [];
            const colorTokens = [];
            for (const token of tokens) {
                if (token === 'inset') {
                    inset = true;
                    continue;
                }
                if (_isCssLengthToken(token)) {
                    lengthTokens.push(token);
                    continue;
                }
                colorTokens.push(token);
            }

            if (lengthTokens.length < 2) return null;
            const color = applyOpacityToColor(
                _resolveCssColorToken(
                    colorTokens.join(' ').trim(),
                    fallbackColor,
                ),
                ctx.effectiveOpacity,
            );
            return {
                offsetXPx: _scaleX(parseFloat(lengthTokens[0]) || 0, ctx),
                offsetYPx: _scaleY(parseFloat(lengthTokens[1]) || 0, ctx),
                blurRadiusPx: _scaleText(parseFloat(lengthTokens[2]) || 0, ctx),
                spreadPx: _scaleText(parseFloat(lengthTokens[3]) || 0, ctx),
                color,
                inset,
            };
        })
        .filter((shadow) => shadow !== null);
}

export function _resolveRunTextColor(cs, ctx) {
    const textFill = _parseCssColor(cs.webkitTextFillColor || '');
    const backgroundClip = (cs.webkitBackgroundClip || cs.backgroundClip || '').toLowerCase();
    if (
        textFill &&
        textFill.a === 0 &&
        backgroundClip.includes('text') &&
        cs.backgroundImage &&
        cs.backgroundImage.includes('linear-gradient(')
    ) {
        const representative = _extractRepresentativeGradientColor(cs.backgroundImage);
        if (representative) {
            return applyOpacityToColor(representative, ctx.effectiveOpacity);
        }
    }
    return applyOpacityToColor(cs.color, ctx.effectiveOpacity);
}

function _resolveEffectiveTextDecoration(el, cs) {
    const decorations = new Set();
    const addTokens = (value) => {
        for (const token of (value || '').split(/\s+/)) {
            if (token && token !== 'none') decorations.add(token);
        }
    };

    addTokens(cs.textDecorationLine || cs.textDecoration || '');
    let current = el ? el.parentElement : null;
    while (current) {
        const currentStyle = window.getComputedStyle(current);
        addTokens(currentStyle.textDecorationLine || currentStyle.textDecoration || '');
        current = current.parentElement;
    }
    return decorations;
}

function _runBackgroundColor(el, cs) {
    if (!el) return 'transparent';
    const tag = (el.localName || el.tagName || '').toLowerCase();
    const display = cs.display || '';
    if (
        display.startsWith('inline') ||
        ['code', 'mark', 'kbd', 'samp'].includes(tag)
    ) {
        return cs.backgroundColor;
    }
    return 'transparent';
}

export function styleToRunStyle(cs, el = null, renderContext = null) {
    const textDecoration = _resolveEffectiveTextDecoration(el, cs);
    const ctx = renderContext || deriveRenderContext(el, null, cs);
    const textGradient = _extractTextGradient(cs, ctx);
    return {
        fontFamily: cs.fontFamily,
        fontSizePx: _scaleText(parseFloat(cs.fontSize), ctx),
        bold: parseInt(cs.fontWeight) >= 600 || cs.fontWeight === 'bold',
        italic: cs.fontStyle === 'italic',
        underline: textDecoration.has('underline'),
        strike: textDecoration.has('line-through'),
        color: _resolveRunTextColor(cs, ctx),
        backgroundColor: applyOpacityToColor(_runBackgroundColor(el, cs), ctx.effectiveOpacity),
        textGradient,
    };
}

// Re-export internal helpers used by entry.js (decoration extraction)
export { _applyOpacityToGradient, _splitTopLevelCommas };
