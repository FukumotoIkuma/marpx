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
            box: getBox(el, sectionRect, ctx),
            zIndex: getZIndex(el),
            alignment: resolveHorizontalAlign(styles) || 'left',
            verticalAlign: resolveVerticalAlign(styles),
            rotationDeg: ctx.effectiveRotationDeg,
            rotation3dXDeg: ctx.effectiveRotation3dXDeg,
            rotation3dYDeg: ctx.effectiveRotation3dYDeg,
            rotation3dZDeg: ctx.effectiveRotation3dZDeg,
            projectedCorners: getProjectedCorners(el, sectionRect, ctx),
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

    export function getBox(el, sectionRect, renderContext = null) {
        const rect = el.getBoundingClientRect();
        const cs = window.getComputedStyle(el);
        const ctx = renderContext || deriveRenderContext(el, null, cs);
        const hasRotation = Math.abs(ctx.effectiveRotationDeg) > 0.01;
        const has3dRotation = (
            Math.abs(ctx.effectiveRotation3dXDeg) > 0.01 ||
            Math.abs(ctx.effectiveRotation3dYDeg) > 0.01 ||
            Math.abs(ctx.effectiveRotation3dZDeg) > 0.01
        );
        if (hasRotation || has3dRotation) {
            const width = Math.max(
                (el.offsetWidth || parseFloat(cs.width) || rect.width) * ctx.effectiveScaleX,
                1,
            );
            const height = Math.max(
                (el.offsetHeight || parseFloat(cs.height) || rect.height) * ctx.effectiveScaleY,
                1,
            );
            const centerX = rect.left + (rect.width / 2);
            const centerY = rect.top + (rect.height / 2);
            return {
                x: centerX - (width / 2) - sectionRect.left,
                y: centerY - (height / 2) - sectionRect.top,
                width,
                height,
            };
        }
        return {
            x: rect.left - sectionRect.left,
            y: rect.top - sectionRect.top,
            width: rect.width,
            height: rect.height,
        };
    }

    export function getContentBox(el, sectionRect, renderContext = null) {
        const cs = window.getComputedStyle(el);
        const ctx = renderContext || deriveRenderContext(el, null, cs);
        const box = getBox(el, sectionRect, ctx);
        const leftInset = _scaleX((parseFloat(cs.borderLeftWidth) || 0) + (parseFloat(cs.paddingLeft) || 0), ctx);
        const topInset = _scaleY((parseFloat(cs.borderTopWidth) || 0) + (parseFloat(cs.paddingTop) || 0), ctx);
        const rightInset = _scaleX((parseFloat(cs.borderRightWidth) || 0) + (parseFloat(cs.paddingRight) || 0), ctx);
        const bottomInset = _scaleY((parseFloat(cs.borderBottomWidth) || 0) + (parseFloat(cs.paddingBottom) || 0), ctx);
        return {
            x: box.x + leftInset,
            y: box.y + topInset,
            width: Math.max(box.width - leftInset - rightInset, 1),
            height: Math.max(box.height - topInset - bottomInset, 1),
        };
    }

    export function getProjectedCorners(el, sectionRect, renderContext = null) {
        const cs = window.getComputedStyle(el);
        const transform = cs.transform;
        if (!transform || transform === 'none') return [];

        let matrix;
        try {
            matrix = new DOMMatrixReadOnly(transform);
        } catch {
            return [];
        }

        const rect = el.getBoundingClientRect();
        const ctx = renderContext || deriveRenderContext(el, null, cs);
        const width = Math.max(
            (el.offsetWidth || parseFloat(cs.width) || rect.width) * ctx.effectiveScaleX,
            1,
        );
        const height = Math.max(
            (el.offsetHeight || parseFloat(cs.height) || rect.height) * ctx.effectiveScaleY,
            1,
        );

        const originParts = (cs.transformOrigin || '50% 50%')
            .split(/\s+/)
            .slice(0, 2)
            .map((value, index) => {
                if (!value) return index === 0 ? width / 2 : height / 2;
                if (value.endsWith('%')) {
                    const pct = parseFloat(value);
                    if (!Number.isFinite(pct)) return index === 0 ? width / 2 : height / 2;
                    return (index === 0 ? width : height) * pct / 100;
                }
                const parsed = parseFloat(value);
                return Number.isFinite(parsed) ? parsed : (index === 0 ? width / 2 : height / 2);
            });
        const originX = originParts[0];
        const originY = originParts[1];

        const relCorners = [
            { x: 0, y: 0 },
            { x: width, y: 0 },
            { x: width, y: height },
            { x: 0, y: height },
        ].map((corner) => {
            const point = matrix.transformPoint(
                new DOMPoint(corner.x - originX, corner.y - originY, 0, 1),
            );
            const w = point.w && Math.abs(point.w) > 1e-6 ? point.w : 1;
            return {
                x: (point.x / w) + originX,
                y: (point.y / w) + originY,
            };
        });

        const minX = Math.min(...relCorners.map((corner) => corner.x));
        const minY = Math.min(...relCorners.map((corner) => corner.y));
        const pageOriginX = rect.left - minX;
        const pageOriginY = rect.top - minY;

        return relCorners.map((corner) => ({
            x: pageOriginX + corner.x - sectionRect.left,
            y: pageOriginY + corner.y - sectionRect.top,
        }));
    }

    export function normalizeInlineText(text) {
        return text.replace(/\s+/g, ' ');
    }
