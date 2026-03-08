import {
    createRenderContext,
    isComplexTransform,
    _textScale,
    _scaleX,
    _scaleY,
    _scaleText,
    deriveRenderContext,
    deriveSubtreeRenderContext,
} from './render-context.js';

// Re-export render-context for backward compatibility
export {
    createRenderContext,
    isComplexTransform,
    _textScale,
    _scaleX,
    _scaleY,
    _scaleText,
    deriveRenderContext,
    deriveSubtreeRenderContext,
};

// Re-export style.js for backward compatibility
export {
    applyOpacityToColor,
    getUnsupportedStyleReason,
    styleToRunStyle,
} from './style.js';

// Re-export decoration.js for backward compatibility
export {
    extractDecoration,
    hasMeaningfulDecoration,
    extractPseudoRuns,
    extractBlockPseudoElements,
    normalizeContentValue,
} from './decoration.js';

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
        display: cs.display,
        alignItems: cs.alignItems,
        justifyContent: cs.justifyContent,
        flexDirection: cs.flexDirection,
    };
}

export function resolveVerticalAlign(cs) {
    const display = (cs.display || '').toLowerCase();
    if (display.includes('flex')) {
        const flexDirection = (cs.flexDirection || 'row').toLowerCase();
        const crossAxisAlign = (cs.alignItems || '').toLowerCase();
        const mainAxisJustify = (cs.justifyContent || '').toLowerCase();
        const relevant = flexDirection.startsWith('column')
            ? mainAxisJustify
            : crossAxisAlign;
        if (relevant.includes('center')) return 'middle';
        if (relevant.includes('end')) return 'bottom';
    }
    if (display.includes('grid')) {
        const alignItems = (cs.alignItems || '').toLowerCase();
        if (alignItems.includes('center')) return 'middle';
        if (alignItems.includes('end')) return 'bottom';
    }
    return 'top';
}

export function resolveHorizontalAlign(cs) {
    const textAlign = (cs.textAlign || '').toLowerCase();
    if (
        textAlign &&
        !['start', 'initial', 'auto', 'normal', 'unset'].includes(textAlign)
    ) {
        return textAlign;
    }

    const display = (cs.display || '').toLowerCase();
    if (display.includes('flex')) {
        const flexDirection = (cs.flexDirection || 'row').toLowerCase();
        const crossAxisAlign = (cs.alignItems || '').toLowerCase();
        const mainAxisJustify = (cs.justifyContent || '').toLowerCase();
        const relevant = flexDirection.startsWith('column')
            ? crossAxisAlign
            : mainAxisJustify;
        if (relevant.includes('center')) return 'center';
        if (relevant.includes('end') || relevant.includes('right')) return 'right';
        if (relevant.includes('start') || relevant.includes('left')) return 'left';
    }
    if (display.includes('grid')) {
        const justifyItems = (cs.justifyItems || '').toLowerCase();
        const justifyContent = (cs.justifyContent || '').toLowerCase();
        const relevant = justifyItems || justifyContent;
        if (relevant.includes('center')) return 'center';
        if (relevant.includes('end') || relevant.includes('right')) return 'right';
        if (relevant.includes('start') || relevant.includes('left')) return 'left';
    }
    return null;
}

export function buildTextElement(el, sectionRect, type, extra = {}) {
    const styles = getComputedStyles(el);
    const { renderContext = null, ...restExtra } = extra;
    const ctx = renderContext || deriveRenderContext(el);
        return {
            type: type,
            box: getBox(el, sectionRect),
            zIndex: getZIndex(el),
            alignment: resolveHorizontalAlign(styles) || 'left',
            verticalAlign: resolveVerticalAlign(styles),
            lineHeightPx: parseFloat(styles.lineHeight) ? _scaleY(parseFloat(styles.lineHeight), ctx) : null,
            spaceBeforePx: _scaleY(parseFloat(styles.marginTop) || 0, ctx),
            spaceAfterPx: _scaleY(parseFloat(styles.marginBottom) || 0, ctx),
            ...restExtra,
        };
    }

    export function getZIndex(el) {
        const raw = window.getComputedStyle(el).zIndex;
        const parsed = parseInt(raw, 10);
        return Number.isFinite(parsed) ? parsed : 0;
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

    export function getContentBox(el, sectionRect, renderContext = null) {
        const rect = el.getBoundingClientRect();
        const cs = window.getComputedStyle(el);
        const ctx = renderContext || deriveRenderContext(el, null, cs);
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

    export function normalizeInlineText(text) {
        return text.replace(/\s+/g, ' ');
    }
