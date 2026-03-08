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
        effectiveRotationDeg: 0,
        effectiveRotation3dXDeg: 0,
        effectiveRotation3dYDeg: 0,
        effectiveRotation3dZDeg: 0,
    };
}

function _clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
}

function _parseTransformScale(transform) {
    if (!transform || transform === 'none' || transform === 'matrix(1, 0, 0, 1, 0, 0)') {
        return {
            scaleX: 1,
            scaleY: 1,
            rotationDeg: 0,
            rotation3dXDeg: 0,
            rotation3dYDeg: 0,
            rotation3dZDeg: 0,
            complex: false,
        };
    }

    if (transform.startsWith('matrix3d(')) {
        const vals = transform
            .slice(9, -1)
            .split(',')
            .map((value) => parseFloat(value.trim()));
        if (vals.length !== 16 || vals.some((value) => !Number.isFinite(value))) {
            return {
                scaleX: 1,
                scaleY: 1,
                rotationDeg: 0,
                rotation3dXDeg: 0,
                rotation3dYDeg: 0,
                rotation3dZDeg: 0,
                complex: true,
            };
        }
        return {
            scaleX: 1,
            scaleY: 1,
            rotationDeg: 0,
            rotation3dXDeg: Math.asin(_clamp(-vals[9], -1, 1)) * (180 / Math.PI),
            rotation3dYDeg: Math.asin(_clamp(vals[2], -1, 1)) * (180 / Math.PI),
            rotation3dZDeg: 0,
            complex: false,
        };
    }

    const matrixMatch = transform.match(/matrix\(([^)]+)\)/);
    if (!matrixMatch) {
        return {
            scaleX: 1,
            scaleY: 1,
            rotationDeg: 0,
            rotation3dXDeg: 0,
            rotation3dYDeg: 0,
            rotation3dZDeg: 0,
            complex: true,
        };
    }

    const vals = matrixMatch[1].split(',').map((value) => parseFloat(value.trim()));
    if (vals.length !== 6 || vals.some((value) => !Number.isFinite(value))) {
        return {
            scaleX: 1,
            scaleY: 1,
            rotationDeg: 0,
            rotation3dXDeg: 0,
            rotation3dYDeg: 0,
            rotation3dZDeg: 0,
            complex: true,
        };
    }

    const [a, b, c, d] = vals;
    const scaleX = Math.hypot(a, b);
    const scaleY = Math.hypot(c, d);
    const dot = a * c + b * d;
    if (
        scaleX <= 0.0001 ||
        scaleY <= 0.0001 ||
        Math.abs(dot) > 0.01
    ) {
        return {
            scaleX: 1,
            scaleY: 1,
            rotationDeg: 0,
            rotation3dXDeg: 0,
            rotation3dYDeg: 0,
            rotation3dZDeg: 0,
            complex: true,
        };
    }

    return {
        scaleX,
        scaleY,
        rotationDeg: Math.atan2(b, a) * (180 / Math.PI),
        rotation3dXDeg: 0,
        rotation3dYDeg: 0,
        rotation3dZDeg: 0,
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
        ctx.effectiveRotationDeg =
            parentCtx.effectiveRotationDeg + ownTransform.rotationDeg;
        ctx.effectiveRotation3dXDeg =
            parentCtx.effectiveRotation3dXDeg + ownTransform.rotation3dXDeg;
        ctx.effectiveRotation3dYDeg =
            parentCtx.effectiveRotation3dYDeg + ownTransform.rotation3dYDeg;
        ctx.effectiveRotation3dZDeg =
            parentCtx.effectiveRotation3dZDeg + ownTransform.rotation3dZDeg;
        return ctx;
    }

    let effectiveOpacity = ownOpacity;
    let effectiveScaleX = ownTransform.scaleX;
    let effectiveScaleY = ownTransform.scaleY;
    let effectiveRotationDeg = ownTransform.rotationDeg;
    let effectiveRotation3dXDeg = ownTransform.rotation3dXDeg;
    let effectiveRotation3dYDeg = ownTransform.rotation3dYDeg;
    let effectiveRotation3dZDeg = ownTransform.rotation3dZDeg;
    let current = el.parentElement;
    while (current) {
        const currentStyle = window.getComputedStyle(current);
        effectiveOpacity *= _parseOpacity(currentStyle.opacity);
        const currentTransform = _parseTransformScale(currentStyle.transform);
        effectiveScaleX *= currentTransform.scaleX;
        effectiveScaleY *= currentTransform.scaleY;
        effectiveRotationDeg += currentTransform.rotationDeg;
        effectiveRotation3dXDeg += currentTransform.rotation3dXDeg;
        effectiveRotation3dYDeg += currentTransform.rotation3dYDeg;
        effectiveRotation3dZDeg += currentTransform.rotation3dZDeg;
        current = current.parentElement;
    }
    const ctx = createRenderContext(effectiveOpacity);
    ctx.effectiveScaleX = effectiveScaleX;
    ctx.effectiveScaleY = effectiveScaleY;
    ctx.effectiveRotationDeg = effectiveRotationDeg;
    ctx.effectiveRotation3dXDeg = effectiveRotation3dXDeg;
    ctx.effectiveRotation3dYDeg = effectiveRotation3dYDeg;
    ctx.effectiveRotation3dZDeg = effectiveRotation3dZDeg;
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
