function _parseOpacity(raw) {
    const parsed = parseFloat(raw || '1');
    if (!Number.isFinite(parsed)) return 1;
    return Math.max(0, Math.min(parsed, 1));
}

export function createRenderContext(effectiveOpacity = 1) {
    return {
        effectiveOpacity: Math.max(0, Math.min(effectiveOpacity, 1)),
        effectiveScaleX: 1,
        effectiveScaleY: 1,
    };
}

function _parseTransformScale(transform) {
    if (!transform || transform === 'none' || transform === 'matrix(1, 0, 0, 1, 0, 0)') {
        return { scaleX: 1, scaleY: 1, complex: false };
    }

    if (transform.startsWith('matrix3d(')) {
        return { scaleX: 1, scaleY: 1, complex: true };
    }

    const matrixMatch = transform.match(/matrix\(([^)]+)\)/);
    if (!matrixMatch) {
        return { scaleX: 1, scaleY: 1, complex: true };
    }

    const vals = matrixMatch[1].split(',').map((value) => parseFloat(value.trim()));
    if (vals.length !== 6 || vals.some((value) => !Number.isFinite(value))) {
        return { scaleX: 1, scaleY: 1, complex: true };
    }

    const [a, b, c, d] = vals;
    if (Math.abs(b) > 0.01 || Math.abs(c) > 0.01) {
        return { scaleX: 1, scaleY: 1, complex: true };
    }

    return {
        scaleX: Math.abs(a) || 1,
        scaleY: Math.abs(d) || 1,
        complex: false,
    };
}

export function isComplexTransform(transform) {
    return _parseTransformScale(transform).complex;
}

function _copyContextWithScale(base, scaleX, scaleY) {
    return {
        effectiveOpacity: base.effectiveOpacity,
        effectiveScaleX: base.effectiveScaleX * scaleX,
        effectiveScaleY: base.effectiveScaleY * scaleY,
    };
}

export function _textScale(ctx) {
    return (ctx.effectiveScaleX + ctx.effectiveScaleY) / 2;
}

export function _scaleX(value, ctx) {
    return value * ctx.effectiveScaleX;
}

export function _scaleY(value, ctx) {
    return value * ctx.effectiveScaleY;
}

export function _scaleText(value, ctx) {
    return value * _textScale(ctx);
}

export function deriveRenderContext(el, parentCtx = null, computedStyle = null) {
    if (!el) return parentCtx || createRenderContext();
    const cs = computedStyle || window.getComputedStyle(el);
    const ownOpacity = _parseOpacity(cs.opacity);
    const ownTransform = _parseTransformScale(cs.transform);
    if (parentCtx) {
        const ctx = createRenderContext(parentCtx.effectiveOpacity * ownOpacity);
        ctx.effectiveScaleX = parentCtx.effectiveScaleX * ownTransform.scaleX;
        ctx.effectiveScaleY = parentCtx.effectiveScaleY * ownTransform.scaleY;
        return ctx;
    }

    let effectiveOpacity = ownOpacity;
    let effectiveScaleX = ownTransform.scaleX;
    let effectiveScaleY = ownTransform.scaleY;
    let current = el.parentElement;
    while (current) {
        const currentStyle = window.getComputedStyle(current);
        effectiveOpacity *= _parseOpacity(currentStyle.opacity);
        const currentTransform = _parseTransformScale(currentStyle.transform);
        effectiveScaleX *= currentTransform.scaleX;
        effectiveScaleY *= currentTransform.scaleY;
        current = current.parentElement;
    }
    const ctx = createRenderContext(effectiveOpacity);
    ctx.effectiveScaleX = effectiveScaleX;
    ctx.effectiveScaleY = effectiveScaleY;
    return ctx;
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
