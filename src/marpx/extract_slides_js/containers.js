import { deriveRenderContext } from './render-context.js';
import { styleToRunStyle } from './style.js';
import { extractPseudoRuns } from './pseudo.js';
import { extractDecoration } from './decoration.js';
import { _buildTextRun, extractInlineRuns, extractTextRunsWithPseudo } from './runs.js';
import { _buildParagraph, extractParagraphsFromLines, getParagraphMetrics } from './paragraphs.js';
import { shouldExtractStandaloneDecoratedText } from './classify.js';
import { resolveHorizontalAlign } from './entry.js';

// --- Module-level helper functions (stateless) ---

/**
 * Determine whether a DOM element should be treated as inline content.
 * Returns true for inline/inline-block/contents display or <br> tags.
 */
function isInlineLikeElement(child) {
    const display = window.getComputedStyle(child).display;
    return (
        display.startsWith('inline') ||
        display === 'contents' ||
        child.tagName === 'BR'
    );
}

/**
 * Check if an element is or contains block-level elements that cannot
 * be rendered as simple text paragraphs (tables, images, code blocks, blockquotes).
 */
function hasUnsupportedBlockDescendants(child) {
    const tag = child.tagName.toLowerCase();
    if (tag === 'table' || tag === 'img' || tag === 'pre' || tag === 'marp-pre' || tag === 'blockquote') {
        return true;
    }
    return !!child.querySelector('table, img, pre, marp-pre, blockquote');
}

/**
 * Build a text run from a DOM node (typically a text node).
 * Returns null if the node produces no visible text.
 */
function buildTextRunFromNode(node, styleEl, renderContext) {
    const run = _buildTextRun(node.textContent || '', styleEl, null, {
        renderContext: renderContext,
    });
    if (!run || !run.text.trim()) return null;
    return run;
}

/**
 * Determine whether accumulated inline runs should be flushed into a paragraph
 * before processing the given child element node.
 *
 * Flush occurs when:
 *  - The child is a list element (ul/ol) — lists are block-level structures
 *  - The child is a standalone decorated text element — rendered separately
 *  - The child is a <br> — forces a line break (new paragraph)
 *  - The child is a non-inline block element without unsupported descendants
 *    — rendered as its own paragraph via pushParagraphFromNode
 */
function shouldFlushInlineRuns(child, childDecoration) {
    const tag = child.tagName.toLowerCase();

    // List elements always start a new block context
    if (tag === 'ul' || tag === 'ol') return true;

    // Standalone decorated text is extracted separately
    if (shouldExtractStandaloneDecoratedText(child, childDecoration)) return true;

    // <br> forces a paragraph break
    if (isInlineLikeElement(child) && tag === 'br') return true;

    // Non-inline block elements without unsupported descendants become their own paragraph
    if (!isInlineLikeElement(child) && !hasUnsupportedBlockDescendants(child)) return true;

    return false;
}

export function extractListItemContent(item, listEl, level, currentOrder, renderContext = null) {
    const itemCs = window.getComputedStyle(item);
    const itemContext = renderContext
        ? deriveRenderContext(item, renderContext, itemCs)
        : deriveRenderContext(item, null, itemCs);
    const metrics = getParagraphMetrics(item, itemCs, itemContext);
    const runs = [];
    const nestedLists = [];

    for (const node of item.childNodes) {
        if (node.nodeType === Node.TEXT_NODE) {
            const run = _buildTextRun(node.textContent || '', item, null, {
                renderContext: itemContext,
            });
            if (run && run.text.trim()) runs.push(run);
            continue;
        }
        if (node.nodeType !== Node.ELEMENT_NODE) continue;
        if (node.tagName === 'UL' || node.tagName === 'OL') {
            nestedLists.push(node);
            continue;
        }
        const childContext = deriveRenderContext(node, itemContext);
        runs.push(...extractInlineRuns(node, {
            includeRootPseudo: true,
            renderContext: childContext,
        }));
    }

    const paragraph = _buildParagraph(
        [
            ...extractPseudoRuns(item, '::before', itemContext),
            ...runs,
            ...extractPseudoRuns(item, '::after', itemContext),
        ],
        resolveHorizontalAlign(itemCs) || resolveHorizontalAlign(window.getComputedStyle(listEl)) || 'left',
        metrics,
        {
            listLevel: level,
            listOrdered: listEl.tagName === 'OL',
            listStyleType: itemCs.listStyleType || window.getComputedStyle(listEl).listStyleType || null,
            orderNumber: currentOrder,
        },
    );

    return { paragraph, nestedLists };
}

export function extractParagraphsFromContainer(el, renderContext = null) {
    const cs = window.getComputedStyle(el);
    const containerContext = renderContext || deriveRenderContext(el, null, cs);
    const alignment = resolveHorizontalAlign(cs) || 'left';
    const paragraphs = [];
    const containerMetrics = {
        lineHeightPx: getParagraphMetrics(el, cs, containerContext).lineHeightPx,
        spaceBeforePx: 0,
        spaceAfterPx: 0,
    };

    function pushParagraph(runs, metrics = containerMetrics, paragraphAlignment = alignment) {
        const paragraph = _buildParagraph(runs, paragraphAlignment, metrics);
        if (paragraph) paragraphs.push(paragraph);
    }

    function pushParagraphFromNode(child) {
        const childContext = deriveRenderContext(child, containerContext);
        const childRuns = extractInlineRuns(child, {
            includeRootPseudo: true,
            renderContext: childContext,
        });
        if (childRuns.length === 0) return;
        const metrics = getParagraphMetrics(child, null, childContext);
        pushParagraph(
            childRuns,
            metrics,
            resolveHorizontalAlign(window.getComputedStyle(child)) || alignment,
        );
    }

    function pushListParagraphs(listEl, level, listContext) {
        const listItems = Array.from(listEl.children).filter((child) => child.tagName === 'LI');
        let orderedIndex = listEl.tagName === 'OL' ? (listEl.start || 1) : 1;
        for (const item of listItems) {
            const currentOrder = listEl.tagName === 'OL'
                ? (parseInt(item.value, 10) || orderedIndex)
                : null;
            if (listEl.tagName === 'OL') {
                orderedIndex = currentOrder + 1;
            }
            const { paragraph, nestedLists } = extractListItemContent(
                item,
                listEl,
                level,
                currentOrder,
                listContext,
            );
            if (paragraph) paragraphs.push(paragraph);
            for (const nested of nestedLists) {
                pushListParagraphs(
                    nested,
                    level + 1,
                    deriveRenderContext(nested, listContext),
                );
            }
        }
    }

    let inlineRuns = [];

    function flushInlineParagraph() {
        if (inlineRuns.length === 0) return;
        pushParagraph(inlineRuns);
        inlineRuns = [];
    }

    for (const child of el.childNodes) {
        if (child.nodeType === Node.TEXT_NODE) {
            const run = buildTextRunFromNode(child, el, containerContext);
            if (run) {
                inlineRuns.push(run);
            }
            continue;
        }
        if (child.nodeType !== Node.ELEMENT_NODE) continue;

        const tag = child.tagName.toLowerCase();
        const childContext = deriveRenderContext(child, containerContext);
        const childDecoration = extractDecoration(child, childContext);

        // Centralized flush decision: flush accumulated inline runs before
        // any block-level or paragraph-breaking element
        if (shouldFlushInlineRuns(child, childDecoration)) {
            flushInlineParagraph();
        }

        // Element-specific actions (flush already handled above)
        if (tag === 'ul' || tag === 'ol') {
            pushListParagraphs(child, 0, childContext);
        } else if (shouldExtractStandaloneDecoratedText(child, childDecoration)) {
            // Standalone decorated text — no further action needed
        } else if (tag === 'br') {
            // Line break — paragraph break already flushed above
        } else if (isInlineLikeElement(child)) {
            const inlineChildContext = deriveRenderContext(child, containerContext);
            inlineRuns.push(...extractInlineRuns(child, {
                includeRootPseudo: true,
                renderContext: inlineChildContext,
            }));
        } else if (!hasUnsupportedBlockDescendants(child)) {
            pushParagraphFromNode(child);
        }
    }
    // Flush: end of container — any remaining inline runs become a final paragraph
    flushInlineParagraph();

    if (paragraphs.length > 0) {
        const beforeRuns = extractPseudoRuns(el, '::before', containerContext);
        const afterRuns = extractPseudoRuns(el, '::after', containerContext);
        if (beforeRuns.length > 0) {
            paragraphs[0].runs = [...beforeRuns, ...paragraphs[0].runs];
        }
        if (afterRuns.length > 0) {
            paragraphs[paragraphs.length - 1].runs = [
                ...paragraphs[paragraphs.length - 1].runs,
                ...afterRuns,
            ];
        }
        return paragraphs;
    }

    // --- 3-stage fallback when no paragraphs were extracted from DOM traversal ---

    // Step 1: blockquote check — blockquotes are handled by the capability
    // classifier and should not produce fallback text paragraphs
    if (el.querySelector('blockquote')) {
        return [];
    }

    // Step 2: innerText fallback — for preformatted text or elements containing
    // <br> tags, split by lines to preserve whitespace/line breaks
    if (cs.whiteSpace.includes('pre') || el.querySelector('br')) {
        return extractParagraphsFromLines(
            el.innerText,
            styleToRunStyle(cs, el, containerContext),
            alignment,
        );
    }

    // Step 3: textRuns fallback — extract inline runs with pseudo-elements
    // as a last resort for simple text content
    const runs = extractTextRunsWithPseudo(el, containerContext);
    if (runs.length === 0) return [];
    const scaledMetrics = getParagraphMetrics(el, cs, containerContext);
    const paragraph = _buildParagraph(runs, alignment, scaledMetrics);
    return paragraph ? [paragraph] : [];
}
