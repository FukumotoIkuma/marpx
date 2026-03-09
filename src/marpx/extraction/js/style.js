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

/**
 * Determine whether a CSS filter string contains only visually negligible
 * adjustments that can safely be ignored when converting to PPTX.
 *
 * Thresholds per function (identity value → allowed range):
 *   brightness(x)  : 1.0 → [0.9, 1.1]
 *   contrast(x)    : 1.0 → [0.9, 1.1]
 *   saturate(x)    : 1.0 → [0.8, 1.2]
 *   opacity(x)     : 1.0 → [0.95, 1.0]
 *   grayscale(x)   : 0   → [0, 0.05]
 *   sepia(x)       : 0   → [0, 0.05]
 *   hue-rotate(Xdeg): 0  → [-10, 10]
 *
 * Any other filter function (blur, drop-shadow, invert, …)
 * is considered non-negligible and forces fallback.
 */
function _isNegligibleFilter(filterStr) {
    const filters = filterStr.match(/[\w-]+\([^)]*\)/g);
    if (!filters) return false;

    for (const f of filters) {
        const match = f.match(/^([\w-]+)\((.+)\)$/);
        if (!match) return false;
        const [, name, valueStr] = match;
        let value = parseFloat(valueStr);
        if (Number.isNaN(value)) return false;

        if (name === 'hue-rotate') {
            // Convert angle units to degrees
            const trimmed = valueStr.trim();
            if (trimmed.endsWith('rad')) {
                value = value * (180 / Math.PI);
            } else if (trimmed.endsWith('turn')) {
                value = value * 360;
            } else if (trimmed.endsWith('grad')) {
                value = value * 0.9;
            }
            // 'deg' or no unit → value is already in degrees
        } else if (['brightness', 'contrast', 'saturate', 'opacity', 'grayscale', 'sepia'].includes(name)) {
            // Handle percentage values (e.g. "110%" → 1.1)
            if (valueStr.trim().endsWith('%')) {
                value = value / 100;
            }
        }

        switch (name) {
            case 'brightness':
                if (value < 0.9 || value > 1.1) return false;
                break;
            case 'contrast':
                if (value < 0.9 || value > 1.1) return false;
                break;
            case 'saturate':
                if (value < 0.8 || value > 1.2) return false;
                break;
            case 'opacity':
                if (value < 0.95 || value > 1.0) return false;
                break;
            case 'grayscale':
                if (value < 0 || value > 0.05) return false;
                break;
            case 'sepia':
                if (value < 0 || value > 0.05) return false;
                break;
            case 'hue-rotate':
                if (Math.abs(value) > 10) return false;
                break;
            default:
                return false;
        }
    }
    return true;
}

export function getUnsupportedStyleReason(cs) {
    const filter = cs.filter || '';
    if (filter && filter !== 'none' && !_isNegligibleFilter(filter)) {
        return 'CSS filter';
    }

    return null;
}

const _WHITESPACE_RE = /\s/;

function _splitTopLevelBy(value, delimiter) {
    const isSpace = delimiter === ' ';
    const parts = [];
    let current = '';
    let depth = 0;
    for (const char of value) {
        if (char === '(') depth += 1;
        if (char === ')') depth = Math.max(depth - 1, 0);
        const isDelimiter = isSpace ? _WHITESPACE_RE.test(char) : char === delimiter;
        if (isDelimiter && depth === 0) {
            if (isSpace) {
                if (current) parts.push(current);
            } else {
                parts.push(current.trim());
            }
            current = '';
            continue;
        }
        current += char;
    }
    if (isSpace) {
        if (current) parts.push(current);
    } else {
        if (current.trim()) parts.push(current.trim());
    }
    return parts;
}

function _splitTopLevelCommas(value) {
    return _splitTopLevelBy(value, ',');
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
    return _splitTopLevelBy(value, ' ');
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

export function _parseTextShadow(textShadow, fallbackColor, ctx) {
    if (!textShadow || textShadow === 'none') return [];
    return _splitTopLevelCommas(textShadow)
        .map((shadowValue) => {
            const tokens = _splitTopLevelSpaces(shadowValue);
            if (tokens.length < 2) return null;

            const lengthTokens = [];
            const colorTokens = [];
            for (const token of tokens) {
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
                color,
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
    const textShadow = _parseTextShadow(cs.textShadow, cs.color, ctx);
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
        textShadow: textShadow.length > 0 ? textShadow : null,
    };
}

// Re-export internal helpers used by entry.js (decoration extraction)
export { _applyOpacityToGradient, _splitTopLevelCommas };
