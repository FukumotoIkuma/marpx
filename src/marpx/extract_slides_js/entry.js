export function getComputedStyles(el) {
    const cs = window.getComputedStyle(el);
    return {
            fontFamily: cs.fontFamily,
            fontSize: cs.fontSize,
            fontWeight: cs.fontWeight,
            fontStyle: cs.fontStyle,
            textDecoration: cs.textDecorationLine || cs.textDecoration,
            color: cs.color,
            textAlign: cs.textAlign,
        backgroundColor: cs.backgroundColor,
        backgroundImage: cs.backgroundImage,
        backgroundClip: cs.backgroundClip,
        webkitBackgroundClip: cs.webkitBackgroundClip,
        webkitTextFillColor: cs.webkitTextFillColor,
        lineHeight: cs.lineHeight,
        marginTop: cs.marginTop,
        marginBottom: cs.marginBottom,
    };
}

function _parseOpacity(raw) {
    const parsed = parseFloat(raw || '1');
    if (!Number.isFinite(parsed)) return 1;
    return Math.max(0, Math.min(parsed, 1));
}

export function createRenderContext(effectiveOpacity = 1) {
    return {
        effectiveOpacity: Math.max(0, Math.min(effectiveOpacity, 1)),
    };
}

export function deriveRenderContext(el, parentCtx = null, computedStyle = null) {
    if (!el) return parentCtx || createRenderContext();
    const cs = computedStyle || window.getComputedStyle(el);
    const ownOpacity = _parseOpacity(cs.opacity);
    if (parentCtx) {
        return createRenderContext(parentCtx.effectiveOpacity * ownOpacity);
    }

    let effectiveOpacity = ownOpacity;
    let current = el.parentElement;
    while (current) {
        effectiveOpacity *= _parseOpacity(window.getComputedStyle(current).opacity);
        current = current.parentElement;
    }
    return createRenderContext(effectiveOpacity);
}

export function deriveSubtreeRenderContext(target, rootEl, rootContext = null) {
    if (target === rootEl) {
        return rootContext || deriveRenderContext(rootEl);
    }

    const chain = [];
    let current = target;
    while (current && current !== rootEl) {
        chain.push(current);
        current = current.parentElement;
    }
    if (current !== rootEl) {
        return deriveRenderContext(target);
    }

    let context = rootContext || deriveRenderContext(rootEl);
    for (let index = chain.length - 1; index >= 0; index--) {
        context = deriveRenderContext(chain[index], context);
    }
    return context;
}

function _parseCssColor(color) {
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

function _parseBoxShadow(boxShadow, fallbackColor, opacity) {
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
                opacity,
            );
            return {
                offsetXPx: parseFloat(lengthTokens[0]) || 0,
                offsetYPx: parseFloat(lengthTokens[1]) || 0,
                blurRadiusPx: parseFloat(lengthTokens[2]) || 0,
                spreadPx: parseFloat(lengthTokens[3]) || 0,
                color,
                inset,
            };
        })
        .filter((shadow) => shadow !== null);
}

function _resolveRunTextColor(cs, ctx) {
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

export function buildTextElement(el, sectionRect, type, extra = {}) {
    const styles = getComputedStyles(el);
        return {
            type: type,
            box: getBox(el, sectionRect),
            zIndex: getZIndex(el),
            alignment: styles.textAlign,
            lineHeightPx: parseFloat(styles.lineHeight) || null,
            spaceBeforePx: parseFloat(styles.marginTop) || 0,
            spaceAfterPx: parseFloat(styles.marginBottom) || 0,
            ...extra,
        };
    }

    export function getZIndex(el) {
        const raw = window.getComputedStyle(el).zIndex;
        const parsed = parseInt(raw, 10);
        return Number.isFinite(parsed) ? parsed : 0;
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

function _extractDecorationFromComputedStyle(cs, ctx) {
    const backgroundClip = (cs.webkitBackgroundClip || cs.backgroundClip || '').toLowerCase();
    const hasTextClippedGradient = backgroundClip.includes('text');
    const borderSide = (side) => {
        const width = parseFloat(cs[`border${side}Width`]) || 0;
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
        borderRadiusPx: parseFloat(cs.borderTopLeftRadius) || 0,
        padding: {
            topPx: parseFloat(cs.paddingTop) || 0,
            rightPx: parseFloat(cs.paddingRight) || 0,
            bottomPx: parseFloat(cs.paddingBottom) || 0,
            leftPx: parseFloat(cs.paddingLeft) || 0,
        },
        boxShadows: _parseBoxShadow(
            cs.boxShadow,
            cs.color || 'rgba(0, 0, 0, 1)',
            ctx.effectiveOpacity,
        ),
        opacity: 1,
    };
}

export function styleToRunStyle(cs, el = null, renderContext = null) {
    const textDecoration = _resolveEffectiveTextDecoration(el, cs);
    const ctx = renderContext || deriveRenderContext(el, null, cs);
    return {
        fontFamily: cs.fontFamily,
        fontSizePx: parseFloat(cs.fontSize),
        bold: parseInt(cs.fontWeight) >= 600 || cs.fontWeight === 'bold',
        italic: cs.fontStyle === 'italic',
        underline: textDecoration.has('underline'),
        strike: textDecoration.has('line-through'),
        color: _resolveRunTextColor(cs, ctx),
        backgroundColor: applyOpacityToColor(_runBackgroundColor(el, cs), ctx.effectiveOpacity),
    };
}

export function extractPseudoRuns(el, pseudo, renderContext = null) {
    const cs = window.getComputedStyle(el, pseudo);
    const content = normalizeContentValue(cs.content);
    if (!content) return [];
    const ctx = renderContext || deriveRenderContext(el);
    return [{
        text: content,
        style: styleToRunStyle(cs, el, ctx),
        linkUrl: null,
    }];
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

    export function getBox(el, sectionRect) {
        const rect = el.getBoundingClientRect();
        return {
            x: rect.left - sectionRect.left,
            y: rect.top - sectionRect.top,
            width: rect.width,
            height: rect.height,
        };
    }

    export function getContentBox(el, sectionRect) {
        const rect = el.getBoundingClientRect();
        const cs = window.getComputedStyle(el);
        const leftInset = (parseFloat(cs.borderLeftWidth) || 0) + (parseFloat(cs.paddingLeft) || 0);
        const topInset = (parseFloat(cs.borderTopWidth) || 0) + (parseFloat(cs.paddingTop) || 0);
        const rightInset = (parseFloat(cs.borderRightWidth) || 0) + (parseFloat(cs.paddingRight) || 0);
        const bottomInset = (parseFloat(cs.borderBottomWidth) || 0) + (parseFloat(cs.paddingBottom) || 0);
        return {
            x: rect.left - sectionRect.left + leftInset,
            y: rect.top - sectionRect.top + topInset,
            width: Math.max(rect.width - leftInset - rightInset, 1),
            height: Math.max(rect.height - topInset - bottomInset, 1),
        };
    }

    export function normalizeInlineText(text) {
        return text.replace(/\s+/g, ' ');
    }

function _boxFromRect(rect, sectionRect) {
    return {
        x: rect.left - sectionRect.left,
        y: rect.top - sectionRect.top,
        width: rect.width,
        height: rect.height,
    };
}

function _contentBoxFromRectAndStyle(rect, cs, sectionRect) {
    const leftInset = (parseFloat(cs.borderLeftWidth) || 0) + (parseFloat(cs.paddingLeft) || 0);
    const topInset = (parseFloat(cs.borderTopWidth) || 0) + (parseFloat(cs.paddingTop) || 0);
    const rightInset = (parseFloat(cs.borderRightWidth) || 0) + (parseFloat(cs.paddingRight) || 0);
    const bottomInset = (parseFloat(cs.borderBottomWidth) || 0) + (parseFloat(cs.paddingBottom) || 0);
    return {
        x: rect.left - sectionRect.left + leftInset,
        y: rect.top - sectionRect.top + topInset,
        width: Math.max(rect.width - leftInset - rightInset, 1),
        height: Math.max(rect.height - topInset - bottomInset, 1),
    };
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
    const parentZ = getZIndex(el);
    const ctx = renderContext || deriveRenderContext(el);
    for (const pseudo of ['::before', '::after']) {
        const cs = window.getComputedStyle(el, pseudo);
        const content = normalizeContentValue(cs.content) || '';
        if (!['absolute', 'fixed'].includes(cs.position)) continue;
        const decoration = _extractDecorationFromComputedStyle(cs, ctx);
        const hasText = content.length > 0;
        if (!hasText && !hasMeaningfulDecoration(decoration)) continue;

        const rect = _measurePseudoRect(el, pseudo, content);
        if (rect.width <= 0 || rect.height <= 0) continue;

        results.push({
            type: 'decorated_block',
            box: _boxFromRect(rect, sectionRect),
            contentBox: hasMeaningfulDecoration(decoration)
                ? _contentBoxFromRectAndStyle(rect, cs, sectionRect)
                : null,
            zIndex: _parsePseudoZIndex(cs, parentZ),
            paragraphs: hasText ? _buildPseudoParagraph(content, cs, el, ctx) : [],
            decoration: hasMeaningfulDecoration(decoration) ? decoration : null,
        });
    }
    return results;
}
