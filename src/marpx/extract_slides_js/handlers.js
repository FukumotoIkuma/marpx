import {
    getComputedStyles,
    buildTextElement,
    getZIndex,
    styleToRunStyle,
    extractDecoration,
    hasMeaningfulDecoration,
    getBox,
    getContentBox,
    deriveRenderContext,
    applyOpacityToColor,
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

export function handleUnsupported(el, slideRect, slideData, unsup) {
    slideData.elements.push({
        type: 'unsupported',
        box: getBox(el, slideRect),
        zIndex: getZIndex(el),
        unsupportedInfo: unsup,
    });
}

export function handleMath(el, slideRect, slideData, tag) {
    slideData.elements.push({
        type: 'math',
        box: getBox(el, slideRect),
        zIndex: getZIndex(el),
        unsupportedInfo: { reason: 'Math expression (MathJax)', tagName: tag },
    });
}

export function handleDecoratedStandalone(el, slideRect, slideData, decoration, renderContext) {
    slideData.elements.push({
        type: 'decorated_block',
        box: getBox(el, slideRect),
        zIndex: getZIndex(el),
        paragraphs: extractParagraphsFromContainer(el, renderContext),
        decoration: decoration,
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
    const box = getBox(el, slideRect);
    const imageContext = deriveRenderContext(singleImageChild, renderContext);
    if (box.width > 0 && box.height > 0) {
        slideData.elements.push({
            type: 'image',
            box: box,
            zIndex: getZIndex(el),
            imageSrc: singleImageChild.src,
            imageNaturalWidthPx: singleImageChild.naturalWidth || null,
            imageNaturalHeightPx: singleImageChild.naturalHeight || null,
            objectFit: window.getComputedStyle(singleImageChild).objectFit || null,
            objectPosition: window.getComputedStyle(singleImageChild).objectPosition || null,
            imageOpacity: imageContext.effectiveOpacity,
            decoration: decoration,
        });
    }
}

export function handleDecoratedBlock(el, slideRect, slideData, decoration, renderContext) {
    const decomposeDecoratedBlock = shouldDecomposeDecoratedBlock(el);
    slideData.elements.push({
        type: 'decorated_block',
        box: getBox(el, slideRect),
        contentBox: getContentBox(el, slideRect),
        zIndex: getZIndex(el),
        paragraphs: decomposeDecoratedBlock ? [] : extractParagraphsFromContainer(el, renderContext),
        decoration: decoration,
    });
    if (decomposeDecoratedBlock) {
        for (const child of el.children) {
            processElement(child, slideRect, slideData, renderContext);
        }
    }
}

export function handleHeading(el, slideRect, slideData, tag, renderContext) {
    const level = parseInt(tag[1]);
    slideData.elements.push(
        buildTextElement(el, slideRect, 'heading', {
            headingLevel: level,
            runs: extractTextRuns(el, renderContext),
        })
    );
}

export function handleParagraph(el, slideRect, slideData, renderContext) {
    if (el.querySelector('img') && !el.textContent.trim()) {
        for (const child of el.children) {
            processElement(child, slideRect, slideData, renderContext);
        }
        return;
    }

    // Check for math containers within paragraph
    const mathContainers = el.querySelectorAll('mjx-container');
    if (mathContainers.length > 0) {
        // If paragraph contains ONLY math (block math), treat as math element
        const nonMathText = Array.from(el.childNodes)
            .filter(n => n.nodeType === Node.TEXT_NODE && n.textContent.trim())
            .length;

        if (nonMathText === 0 && el.children.length === mathContainers.length) {
            // Pure math paragraph - extract as math
            slideData.elements.push({
                type: 'math',
                box: getBox(el, slideRect),
                zIndex: getZIndex(el),
                unsupportedInfo: { reason: 'Math expression (MathJax)', tagName: 'mjx-container' },
            });
            return;
        }
        // Mixed content: fall through to normal paragraph handling
        // Math will be handled as unsupported subtree
    }

    const decoratedChildren = Array.from(el.children).filter((child) =>
        shouldExtractStandaloneDecoratedText(
            child,
            extractDecoration(child, deriveRenderContext(child, renderContext)),
        )
    );

    slideData.elements.push(
        buildTextElement(el, slideRect, 'paragraph', {
            runs: decoratedChildren.length > 0
                ? extractTextRunsWithHiddenDecorated(el, renderContext)
                : extractTextRunsWithPseudo(el, renderContext),
        })
    );
    for (const child of decoratedChildren) {
        processElement(child, slideRect, slideData, renderContext);
    }
}

export function handleBlockquote(el, slideRect, slideData, decoration, renderContext) {
    const hasDecoration = hasMeaningfulDecoration(decoration);
    slideData.elements.push(
        buildTextElement(el, slideRect, 'blockquote', {
            runs: extractTextRunsWithPseudo(el, renderContext),
            decoration: hasDecoration ? decoration : null,
            contentBox: hasDecoration ? getContentBox(el, slideRect) : null,
        })
    );
}

export function handleList(el, slideRect, slideData, tag, renderContext) {
    slideData.elements.push({
        type: tag === 'ul' ? 'unordered_list' : 'ordered_list',
        box: getBox(el, slideRect),
        zIndex: getZIndex(el),
        listItems: extractListItems(el, 0, renderContext),
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
            lineHeightPx: parseFloat(styles.lineHeight) || null,
            spaceBeforePx: parseFloat(styles.marginTop) || 0,
            spaceAfterPx: parseFloat(styles.marginBottom) || 0,
        };
        slideData.elements.push({
            type: 'code_block',
            box: getBox(el, slideRect),
            contentBox: hasDecoration ? getContentBox(el, slideRect) : null,
            zIndex: getZIndex(el),
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
        });
        return true; // handled
    }
    return false; // no code element found, caller should recurse
}

export function handleImage(el, slideRect, slideData, decoration, renderContext) {
    const box = getBox(el, slideRect);
    if (box.width > 0 && box.height > 0) {
        slideData.elements.push({
            type: 'image',
            box: box,
            zIndex: getZIndex(el),
            imageSrc: el.src,
            imageNaturalWidthPx: el.naturalWidth || null,
            imageNaturalHeightPx: el.naturalHeight || null,
            objectFit: window.getComputedStyle(el).objectFit || null,
            objectPosition: window.getComputedStyle(el).objectPosition || null,
            imageOpacity: renderContext.effectiveOpacity,
            decoration: hasMeaningfulDecoration(decoration)
                ? decoration
                : null,
        });
    }
}

export function handleTable(el, slideRect, slideData, renderContext) {
    slideData.elements.push({
        type: 'table',
        box: getBox(el, slideRect),
        zIndex: getZIndex(el),
        tableRows: extractTable(el, slideRect, renderContext),
    });
}

/**
 * Dispatch logic: checks element type and calls appropriate handler.
 * @param {Element} el
 * @param {DOMRect} slideRect
 * @param {object} slideData
 */
export function processElement(el, slideRect, slideData, parentContext = null) {
    const tag = (el.localName || el.tagName).toLowerCase();

    // Skip script, style, header, footer, etc.
    if (['script', 'style', 'link', 'meta', 'header', 'footer'].includes(tag)) return;

    // Check for unsupported
    const unsup = isUnsupported(el);
    if (unsup) {
        handleUnsupported(el, slideRect, slideData, unsup);
        return; // Don't descend into unsupported subtrees
    }

    // Math containers (MathJax)
    if (tag === 'mjx-container' || (el.classList && el.classList.contains('MathJax'))) {
        handleMath(el, slideRect, slideData, tag);
        return; // Don't descend into MathJax SVG
    }

    const renderContext = deriveRenderContext(el, parentContext);
    const decoration = extractDecoration(el, renderContext);

    if (shouldExtractStandaloneDecoratedText(el, decoration)) {
        handleDecoratedStandalone(el, slideRect, slideData, decoration, renderContext);
        return;
    }

    const singleImageChild = _findSingleImageChild(el);
    if (singleImageChild && hasMeaningfulDecoration(decoration)) {
        handleImageWithDecoration(
            el,
            slideRect,
            slideData,
            decoration,
            singleImageChild,
            renderContext,
        );
        return;
    }

    if (shouldExtractDecoratedBlock(el, decoration, renderContext)) {
        handleDecoratedBlock(el, slideRect, slideData, decoration, renderContext);
        return;
    }

    // Headings
    if (/^h[1-6]$/.test(tag)) {
        handleHeading(el, slideRect, slideData, tag, renderContext);
        return;
    }

    // Paragraphs
    if (tag === 'p' || tag === 'figcaption') {
        handleParagraph(el, slideRect, slideData, renderContext);
        return;
    }

    // Blockquote
    if (tag === 'blockquote') {
        handleBlockquote(el, slideRect, slideData, decoration, renderContext);
        return;
    }

    // Lists
    if (tag === 'ul' || tag === 'ol') {
        handleList(el, slideRect, slideData, tag, renderContext);
        return;
    }

    // Code blocks
    if (tag === 'pre' || tag === 'marp-pre') {
        if (handleCodeBlock(el, slideRect, slideData, renderContext)) {
            return;
        }
    }

    // Images
    if (tag === 'img') {
        handleImage(el, slideRect, slideData, decoration, renderContext);
        return;
    }

    // Tables
    if (tag === 'table') {
        handleTable(el, slideRect, slideData, renderContext);
        return;
    }

    // For other elements, recurse into children
    for (const child of el.children) {
        processElement(child, slideRect, slideData, renderContext);
    }
}
