import { deriveRenderContext } from './render-context.js';
import { styleToRunStyle, applyOpacityToColor } from './style.js';
import { extractDecoration, hasMeaningfulDecoration } from './decoration.js';
import { extractBlockPseudoElements } from './pseudo.js';
import {
    getComputedStyles,
    buildTextElement,
    getBox,
    getContentBox,
    getProjectedCorners,
    resolveVerticalAlign,
    resolveEffectiveZIndex,
} from './entry.js';
import {
    extractTextRuns,
    extractExactTextRuns,
    extractTextRunsWithPseudo,
} from './runs.js';
import {
    shouldExtractStandaloneDecoratedText,
    extractTextRunsWithHiddenDecorated,
} from './classify.js';
import { buildParagraphsFromRuns } from './paragraphs.js';
import {
    extractParagraphsFromContainer,
} from './containers.js';
import {
    isUnsupported,
    shouldExtractDecoratedBlock,
    shouldDecomposeDecoratedBlock,
    extractListItems,
    extractTable,
    _findSingleImageChild,
} from './blocks.js';

function _normalizeCssColorValue(value) {
    return (value || '').replace(/\s+/g, '').toLowerCase();
}

function _stripContainerBackgroundFromParagraphs(paragraphs, decoration) {
    if (!decoration || !decoration.backgroundColor) return paragraphs;
    const containerBg = _normalizeCssColorValue(decoration.backgroundColor);
    if (!containerBg || containerBg === 'transparent' || containerBg === 'rgba(0,0,0,0)') {
        return paragraphs;
    }
    return paragraphs.map((paragraph) => ({
        ...paragraph,
        runs: paragraph.runs.map((run) => {
            const runBg = _normalizeCssColorValue(run.style?.backgroundColor);
            if (runBg !== containerBg) return run;
            return {
                ...run,
                style: {
                    ...run.style,
                    backgroundColor: null,
                },
            };
        }),
    }));
}

function _isInlineStandaloneUnsupported(el) {
    const tag = (el.localName || el.tagName).toLowerCase();
    if (
        [
            'section', 'blockquote', 'ul', 'ol', 'li', 'table', 'thead', 'tbody', 'tr', 'td',
            'th', 'img', 'pre', 'marp-pre', 'script', 'style', 'link', 'meta',
            'header', 'footer'
        ].includes(tag)
    ) {
        return false;
    }
    const display = window.getComputedStyle(el).display;
    if (!display.startsWith('inline')) return false;
    if (el.querySelector('table, img, pre, marp-pre, blockquote, ul, ol')) return false;
    return !!isUnsupported(el);
}

/**
 * Single-pass recursive walk that classifies paragraph descendants.
 * Priority: math > decorated > unsupported > normal.
 * Once classified, the subtree is skipped (no descendant can match another category).
 */
function _classifyParagraphDescendants(el, renderContext) {
    const mathEls = [];
    const decoratedEls = [];
    const unsupportedEls = [];

    function walk(node) {
        for (const child of node.children) {
            const tag = (child.localName || child.tagName).toLowerCase();

            // Priority 1: Math container — claim entire subtree
            if (tag === 'mjx-container' || (child.classList && child.classList.contains('MathJax'))) {
                mathEls.push(child);
                continue;
            }

            // Priority 2: Standalone decorated (direct children only — expensive check)
            if (child.parentElement === el) {
                const childCtx = deriveRenderContext(child, renderContext);
                const childDec = extractDecoration(child, childCtx);
                if (shouldExtractStandaloneDecoratedText(child, childDec)) {
                    decoratedEls.push(child);
                    continue;
                }
            }

            // Priority 3: Inline unsupported
            if (_isInlineStandaloneUnsupported(child)) {
                unsupportedEls.push(child);
                continue;
            }

            // Normal: recurse into children
            walk(child);
        }
    }

    walk(el);
    return { mathEls, decoratedEls, unsupportedEls };
}

/**
 * Resolve render context with optional parent.
 * Consolidates the repeated `parentContext ? deriveRenderContext(el, parentContext) : deriveRenderContext(el)` pattern.
 */
function _resolveRenderContext(el, parentContext) {
    return parentContext ? deriveRenderContext(el, parentContext) : deriveRenderContext(el);
}

export function handleUnsupported(el, slideRect, slideData, unsup, parentContext = null) {
    const renderContext = _resolveRenderContext(el, parentContext);
    slideData.elements.push({
        type: 'unsupported',
        box: getBox(el, slideRect, renderContext),
        zIndex: resolveEffectiveZIndex(el, renderContext),
        rotationDeg: renderContext.effectiveRotationDeg,
        rotation3dXDeg: renderContext.effectiveRotation3dXDeg,
        rotation3dYDeg: renderContext.effectiveRotation3dYDeg,
        rotation3dZDeg: renderContext.effectiveRotation3dZDeg,
        projectedCorners: getProjectedCorners(el, slideRect, renderContext),
        unsupportedInfo: unsup,
    });
}

export function handleMath(el, slideRect, slideData, tag, parentContext = null) {
    const svg = el.querySelector('svg');
    const renderContext = _resolveRenderContext(el, parentContext);

    // Extract LaTeX source from data-latex attribute on wrapper element
    const latexWrapper = el.closest('[data-latex]');
    const latexSource = latexWrapper ? latexWrapper.getAttribute('data-latex') : null;

    slideData.elements.push({
        type: 'math',
        box: getBox(el, slideRect, renderContext),
        zIndex: resolveEffectiveZIndex(el, renderContext),
        rotationDeg: renderContext.effectiveRotationDeg,
        rotation3dXDeg: renderContext.effectiveRotation3dXDeg,
        rotation3dYDeg: renderContext.effectiveRotation3dYDeg,
        rotation3dZDeg: renderContext.effectiveRotation3dZDeg,
        projectedCorners: getProjectedCorners(el, slideRect, renderContext),
        latexSource: latexSource,
        unsupportedInfo: {
            reason: 'Math expression (MathJax)',
            tagName: tag,
            svgMarkup: svg ? svg.outerHTML : null,
        },
    });
}

export function handleDecoratedStandalone(el, slideRect, slideData, decoration, renderContext) {
    const cs = window.getComputedStyle(el);
    const paragraphs = _stripContainerBackgroundFromParagraphs(
        extractParagraphsFromContainer(el, renderContext),
        decoration,
    );
    slideData.elements.push({
        type: 'decorated_block',
        box: getBox(el, slideRect, renderContext),
        zIndex: resolveEffectiveZIndex(el, renderContext),
        paragraphs,
        decoration: decoration,
        verticalAlign: resolveVerticalAlign(cs),
        rotationDeg: renderContext.effectiveRotationDeg,
        rotation3dXDeg: renderContext.effectiveRotation3dXDeg,
        rotation3dYDeg: renderContext.effectiveRotation3dYDeg,
        rotation3dZDeg: renderContext.effectiveRotation3dZDeg,
        projectedCorners: getProjectedCorners(el, slideRect, renderContext),
    });
}

export function handleImageWithDecoration(
    el,
    slideRect,
    slideData,
    decoration,
    singleImageChild,
    renderContext,
) {
    const box = getBox(el, slideRect, renderContext);
    const imageContext = deriveRenderContext(singleImageChild, renderContext);
    if (box.width > 0 && box.height > 0) {
        slideData.elements.push({
            type: 'image',
            box: box,
            zIndex: resolveEffectiveZIndex(el, renderContext),
            imageSrc: singleImageChild.src,
            imageNaturalWidthPx: singleImageChild.naturalWidth || null,
            imageNaturalHeightPx: singleImageChild.naturalHeight || null,
            objectFit: window.getComputedStyle(singleImageChild).objectFit || null,
            objectPosition: window.getComputedStyle(singleImageChild).objectPosition || null,
            imageOpacity: imageContext.effectiveOpacity,
            decoration: decoration,
            rotationDeg: renderContext.effectiveRotationDeg,
            rotation3dXDeg: renderContext.effectiveRotation3dXDeg,
            rotation3dYDeg: renderContext.effectiveRotation3dYDeg,
            rotation3dZDeg: renderContext.effectiveRotation3dZDeg,
            projectedCorners: getProjectedCorners(el, slideRect, renderContext),
        });
    }
}

export function handleDecoratedBlock(el, slideRect, slideData, decoration, renderContext, shouldDecompose) {
    const cs = window.getComputedStyle(el);
    const containerEffectiveZ = resolveEffectiveZIndex(el, renderContext);
    const paragraphs = shouldDecompose
        ? []
        : _stripContainerBackgroundFromParagraphs(
            extractParagraphsFromContainer(el, renderContext),
            decoration,
        );
    slideData.elements.push({
        type: 'decorated_block',
        box: getBox(el, slideRect, renderContext),
        contentBox: getContentBox(el, slideRect, renderContext),
        zIndex: containerEffectiveZ,
        paragraphs,
        decoration: decoration,
        verticalAlign: resolveVerticalAlign(cs),
        rotationDeg: renderContext.effectiveRotationDeg,
        rotation3dXDeg: renderContext.effectiveRotation3dXDeg,
        rotation3dYDeg: renderContext.effectiveRotation3dYDeg,
        rotation3dZDeg: renderContext.effectiveRotation3dZDeg,
        projectedCorners: getProjectedCorners(el, slideRect, renderContext),
    });
    if (shouldDecompose) {
        const childContext = { ...renderContext, baseZIndex: containerEffectiveZ + 1 };
        for (const child of el.children) {
            processElement(child, slideRect, slideData, childContext);
        }
    }
}

export function handleHeading(el, slideRect, slideData, tag, renderContext) {
    const level = parseInt(tag[1]);
    slideData.elements.push(
        buildTextElement(el, slideRect, 'heading', {
            headingLevel: level,
            runs: extractTextRuns(el, renderContext),
            renderContext,
        })
    );
}

export function handleParagraph(el, slideRect, slideData, renderContext) {
    // Early return: image-only paragraphs (unchanged)
    if (el.querySelector('img') && !el.textContent.trim()) {
        for (const child of el.children) {
            processElement(child, slideRect, slideData, renderContext);
        }
        return;
    }

    // Single-pass classification
    const { mathEls, decoratedEls, unsupportedEls } = _classifyParagraphDescendants(el, renderContext);

    // Pure math paragraph: all direct children are math containers, no text
    if (mathEls.length > 0 && decoratedEls.length === 0 && unsupportedEls.length === 0) {
        const nonMathText = Array.from(el.childNodes)
            .filter(n => n.nodeType === Node.TEXT_NODE && n.textContent.trim())
            .length;
        const directMath = mathEls.filter(m => m.parentElement === el);
        if (nonMathText === 0 && el.children.length === directMath.length) {
            handleMath(el, slideRect, slideData, 'mjx-container', renderContext);
            return;
        }
    }

    // Build paragraph text (with hidden placeholders for standalone children)
    const hasStandalone = mathEls.length > 0 || decoratedEls.length > 0 || unsupportedEls.length > 0;
    slideData.elements.push(
        buildTextElement(el, slideRect, 'paragraph', {
            runs: hasStandalone
                ? extractTextRunsWithHiddenDecorated(
                    el, renderContext, mathEls.length > 0, _isInlineStandaloneUnsupported,
                )
                : extractTextRunsWithPseudo(el, renderContext, false),
            renderContext,
        })
    );

    // Extract standalone children as separate elements
    for (const mathEl of mathEls) {
        handleMath(mathEl, slideRect, slideData, 'mjx-container', renderContext);
    }
    for (const child of decoratedEls) {
        processElement(child, slideRect, slideData, renderContext);
    }
    for (const child of unsupportedEls) {
        processElement(child, slideRect, slideData, renderContext);
    }
}

function _isLeafTextBlock(el) {
    if (el.children.length > 0) return false;
    return !!el.textContent && el.textContent.trim().length > 0;
}

function _isPresentationalList(el) {
    const cs = window.getComputedStyle(el);
    const listStyleType = (cs.listStyleType || '').toLowerCase();
    if (listStyleType !== 'none') return false;
    const items = Array.from(el.children).filter(
        (child) => (child.localName || child.tagName).toLowerCase() === 'li'
    );
    const hasPseudoMarkers = items.some((item) => {
        const before = window.getComputedStyle(item, '::before').content;
        const after = window.getComputedStyle(item, '::after').content;
        return [before, after].some(
            (content) =>
                content &&
                content !== 'none' &&
                content !== 'normal' &&
                content !== '""' &&
                content !== "''"
        );
    });
    return !hasPseudoMarkers;
}

export function handleBlockquote(el, slideRect, slideData, decoration, renderContext) {
    const hasDecoration = hasMeaningfulDecoration(decoration);
    const cs = window.getComputedStyle(el);
    const paragraphs = _stripContainerBackgroundFromParagraphs(
        extractParagraphsFromContainer(el, renderContext),
        decoration,
    );
    slideData.elements.push({
        type: 'blockquote',
        box: getBox(el, slideRect, renderContext),
        contentBox: hasDecoration ? getContentBox(el, slideRect, renderContext) : null,
        zIndex: resolveEffectiveZIndex(el, renderContext),
        paragraphs,
        decoration: hasDecoration ? decoration : null,
        verticalAlign: resolveVerticalAlign(cs),
        rotationDeg: renderContext.effectiveRotationDeg,
        rotation3dXDeg: renderContext.effectiveRotation3dXDeg,
        rotation3dYDeg: renderContext.effectiveRotation3dYDeg,
        rotation3dZDeg: renderContext.effectiveRotation3dZDeg,
        projectedCorners: getProjectedCorners(el, slideRect, renderContext),
    });
    for (const child of Array.from(el.children)) {
        if ((child.localName || child.tagName).toLowerCase() === 'blockquote') {
            processElement(child, slideRect, slideData, renderContext);
        }
    }
}

export function handleList(el, slideRect, slideData, tag, renderContext) {
    slideData.elements.push({
        type: tag === 'ul' ? 'unordered_list' : 'ordered_list',
        box: getBox(el, slideRect, renderContext),
        zIndex: resolveEffectiveZIndex(el, renderContext),
        listItems: extractListItems(el, 0, renderContext),
        rotationDeg: renderContext.effectiveRotationDeg,
        rotation3dXDeg: renderContext.effectiveRotation3dXDeg,
        rotation3dYDeg: renderContext.effectiveRotation3dYDeg,
        rotation3dZDeg: renderContext.effectiveRotation3dZDeg,
        projectedCorners: getProjectedCorners(el, slideRect, renderContext),
    });
}

export function handleCodeBlock(el, slideRect, slideData, renderContext) {
    const codeEl = el.querySelector('code');
    if (codeEl) {
        const styles = getComputedStyles(el);
        const decoration = extractDecoration(el, renderContext);
        const hasDecoration = hasMeaningfulDecoration(decoration);
        const lang = Array.from(codeEl.classList)
            .find(c => c.startsWith('language-'));
        const alignment = window.getComputedStyle(codeEl).textAlign || styles.textAlign;
        const metrics = {
            lineHeightPx: parseFloat(styles.lineHeight)
                ? parseFloat(styles.lineHeight) * renderContext.effectiveScaleY
                : null,
            spaceBeforePx: (parseFloat(styles.marginTop) || 0) * renderContext.effectiveScaleY,
            spaceAfterPx: (parseFloat(styles.marginBottom) || 0) * renderContext.effectiveScaleY,
        };
        slideData.elements.push({
            type: 'code_block',
            box: getBox(el, slideRect, renderContext),
            contentBox: hasDecoration ? getContentBox(el, slideRect, renderContext) : null,
            zIndex: resolveEffectiveZIndex(el, renderContext),
            paragraphs: buildParagraphsFromRuns(
                extractExactTextRuns(codeEl, deriveRenderContext(codeEl, renderContext)),
                alignment,
                metrics,
                styleToRunStyle(window.getComputedStyle(codeEl), codeEl, deriveRenderContext(codeEl, renderContext)),
                { trimRuns: false },
            ),
            codeLanguage: lang ? lang.replace('language-', '') : null,
            decoration: hasDecoration ? decoration : null,
            codeBackground: applyOpacityToColor(styles.backgroundColor, renderContext.effectiveOpacity),
            verticalAlign: resolveVerticalAlign(styles),
            rotationDeg: renderContext.effectiveRotationDeg,
            rotation3dXDeg: renderContext.effectiveRotation3dXDeg,
            rotation3dYDeg: renderContext.effectiveRotation3dYDeg,
            rotation3dZDeg: renderContext.effectiveRotation3dZDeg,
            projectedCorners: getProjectedCorners(el, slideRect, renderContext),
        });
        return true; // handled
    }
    return false; // no code element found, caller should recurse
}

export function handleImage(el, slideRect, slideData, decoration, renderContext) {
    const box = getBox(el, slideRect, renderContext);
    if (box.width > 0 && box.height > 0) {
        slideData.elements.push({
            type: 'image',
            box: box,
            zIndex: resolveEffectiveZIndex(el, renderContext),
            imageSrc: el.src,
            imageNaturalWidthPx: el.naturalWidth || null,
            imageNaturalHeightPx: el.naturalHeight || null,
            objectFit: window.getComputedStyle(el).objectFit || null,
            objectPosition: window.getComputedStyle(el).objectPosition || null,
            imageOpacity: renderContext.effectiveOpacity,
            decoration: hasMeaningfulDecoration(decoration)
                ? decoration
                : null,
            rotationDeg: renderContext.effectiveRotationDeg,
            rotation3dXDeg: renderContext.effectiveRotation3dXDeg,
            rotation3dYDeg: renderContext.effectiveRotation3dYDeg,
            rotation3dZDeg: renderContext.effectiveRotation3dZDeg,
        });
    }
}

export function handleTable(el, slideRect, slideData, renderContext, decoration) {
    slideData.elements.push({
        type: 'table',
        box: getBox(el, slideRect, renderContext),
        zIndex: resolveEffectiveZIndex(el, renderContext),
        tableRows: extractTable(el, slideRect, renderContext),
        decoration: hasMeaningfulDecoration(decoration) ? decoration : null,
        rotationDeg: renderContext.effectiveRotationDeg,
        rotation3dXDeg: renderContext.effectiveRotation3dXDeg,
        rotation3dYDeg: renderContext.effectiveRotation3dYDeg,
        rotation3dZDeg: renderContext.effectiveRotation3dZDeg,
    });
}

const SKIP_TAGS = new Set(['script', 'style', 'link', 'meta', 'header', 'footer']);
const HEADING_RE = /^h[1-6]$/;

/**
 * Pre-context dispatch table: entries evaluated BEFORE deriving renderContext.
 * These use parentContext directly and short-circuit on match.
 * Each entry: { match(el, tag) -> truthy, handler(el, slideRect, slideData, tag, parentContext) }
 */
const preContextDispatch = [
    {
        // Skip non-renderable elements
        match: (_el, tag) => SKIP_TAGS.has(tag),
        handler: () => {},
    },
    {
        // Unsupported elements - match returns the unsupported info object
        match: (el) => isUnsupported(el),
        handler: (el, slideRect, slideData, _tag, parentContext, matchResult) => {
            handleUnsupported(el, slideRect, slideData, matchResult, parentContext);
        },
    },
    {
        // Math containers (MathJax)
        match: (el, tag) => tag === 'mjx-container' || (el.classList && el.classList.contains('MathJax')),
        handler: (el, slideRect, slideData, tag, parentContext) => {
            handleMath(el, slideRect, slideData, tag, parentContext);
        },
    },
];

/**
 * Post-context dispatch table: entries evaluated AFTER deriving renderContext/decoration.
 * Each entry: { match(el, ctx) -> truthy, handler(el, slideRect, slideData, ctx) -> boolean }
 * handler returns true if handled (stop), false to continue to next entry.
 * ctx = { tag, renderContext, decoration }
 */
const postContextDispatch = [
    {
        // Standalone decorated text (e.g., inline code with background)
        match: (_el, ctx) => shouldExtractStandaloneDecoratedText(_el, ctx.decoration),
        handler: (el, slideRect, slideData, ctx) => {
            handleDecoratedStandalone(el, slideRect, slideData, ctx.decoration, ctx.renderContext);
            return true;
        },
    },
    {
        // Image wrapped in a decorated container - match returns the img element
        match: (el, ctx) => {
            const img = _findSingleImageChild(el);
            return img && hasMeaningfulDecoration(ctx.decoration) ? img : false;
        },
        handler: (el, slideRect, slideData, ctx, matchResult) => {
            handleImageWithDecoration(el, slideRect, slideData, ctx.decoration, matchResult, ctx.renderContext);
            return true;
        },
    },
    {
        // Decorated block (blockquote-like containers with meaningful decoration)
        match: (el, ctx) => shouldExtractDecoratedBlock(el, ctx.decoration, ctx.renderContext),
        handler: (el, slideRect, slideData, ctx) => {
            handleDecoratedBlock(el, slideRect, slideData, ctx.decoration, ctx.renderContext, shouldDecomposeDecoratedBlock(el));
            return true;
        },
    },
    {
        // Headings (h1-h6)
        match: (_el, ctx) => HEADING_RE.test(ctx.tag),
        handler: (el, slideRect, slideData, ctx) => {
            handleHeading(el, slideRect, slideData, ctx.tag, ctx.renderContext);
            return true;
        },
    },
    {
        // Paragraphs and figcaptions
        match: (_el, ctx) => ctx.tag === 'p' || ctx.tag === 'figcaption',
        handler: (el, slideRect, slideData, ctx) => {
            handleParagraph(el, slideRect, slideData, ctx.renderContext);
            return true;
        },
    },
    {
        // Leaf text blocks (no children, has text content)
        match: (el) => _isLeafTextBlock(el),
        handler: (el, slideRect, slideData, ctx) => {
            handleParagraph(el, slideRect, slideData, ctx.renderContext);
            return true;
        },
    },
    {
        // Blockquotes
        match: (_el, ctx) => ctx.tag === 'blockquote',
        handler: (el, slideRect, slideData, ctx) => {
            handleBlockquote(el, slideRect, slideData, ctx.decoration, ctx.renderContext);
            return true;
        },
    },
    {
        // Lists (ul/ol) - presentational lists recurse, normal lists extract
        match: (_el, ctx) => ctx.tag === 'ul' || ctx.tag === 'ol',
        handler: (el, slideRect, slideData, ctx) => {
            if (_isPresentationalList(el)) {
                for (const child of el.children) {
                    processElement(child, slideRect, slideData, ctx.renderContext);
                }
            } else {
                handleList(el, slideRect, slideData, ctx.tag, ctx.renderContext);
            }
            return true;
        },
    },
    {
        // Code blocks (pre/marp-pre) - may fall through if no <code> child
        match: (_el, ctx) => ctx.tag === 'pre' || ctx.tag === 'marp-pre',
        handler: (el, slideRect, slideData, ctx) => {
            return handleCodeBlock(el, slideRect, slideData, ctx.renderContext);
        },
    },
    {
        // Images
        match: (_el, ctx) => ctx.tag === 'img',
        handler: (el, slideRect, slideData, ctx) => {
            handleImage(el, slideRect, slideData, ctx.decoration, ctx.renderContext);
            return true;
        },
    },
    {
        // Tables
        match: (_el, ctx) => ctx.tag === 'table',
        handler: (el, slideRect, slideData, ctx) => {
            handleTable(el, slideRect, slideData, ctx.renderContext, ctx.decoration);
            return true;
        },
    },
];

/**
 * Dispatch logic: checks element type and calls appropriate handler.
 * Uses a two-phase dispatch table to determine handling:
 *   1. Pre-context phase: checks before deriving renderContext (skip tags, unsupported, math)
 *   2. Post-context phase: checks after deriving renderContext and decoration
 * @param {Element} el
 * @param {DOMRect} slideRect
 * @param {object} slideData
 * @param {object|null} parentContext
 */
export function processElement(el, slideRect, slideData, parentContext = null) {
    const tag = (el.localName || el.tagName).toLowerCase();

    // Phase 1: Pre-context dispatch (no renderContext needed)
    for (const { match, handler } of preContextDispatch) {
        const matchResult = match(el, tag);
        if (matchResult) {
            handler(el, slideRect, slideData, tag, parentContext, matchResult);
            return;
        }
    }

    // Derive shared context for post-context dispatch
    const renderContext = _resolveRenderContext(el, parentContext);
    slideData.elements.push(...extractBlockPseudoElements(el, slideRect, renderContext));
    const decoration = extractDecoration(el, renderContext);
    const ctx = { tag, renderContext, decoration };

    // Phase 2: Post-context dispatch
    for (const { match, handler } of postContextDispatch) {
        const matchResult = match(el, ctx);
        if (matchResult) {
            if (handler(el, slideRect, slideData, ctx, matchResult)) {
                return;
            }
        }
    }

    // Fallback: recurse into children
    for (const child of el.children) {
        processElement(child, slideRect, slideData, renderContext);
    }
}
