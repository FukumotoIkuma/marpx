    import { deriveRenderContext } from './render-context.js';
    import { styleToRunStyle } from './style.js';
    import { extractPseudoRuns, extractDecoration } from './decoration.js';
    import { _buildTextRun, extractInlineRuns, extractTextRunsWithPseudo } from './runs.js';
    import { _buildParagraph, extractParagraphsFromLines, getParagraphMetrics } from './paragraphs.js';
    import { shouldExtractStandaloneDecoratedText } from './classify.js';
    import { resolveHorizontalAlign } from './entry.js';

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

        function buildTextRunFromNode(node, styleEl) {
            const run = _buildTextRun(node.textContent || '', styleEl, null, {
                renderContext: containerContext,
            });
            if (!run || !run.text.trim()) return null;
            return run;
        }

        function isInlineLikeElement(child) {
            const display = window.getComputedStyle(child).display;
            return (
                display.startsWith('inline') ||
                display === 'contents' ||
                child.tagName === 'BR'
            );
        }

        function hasUnsupportedBlockDescendants(child) {
            const tag = child.tagName.toLowerCase();
            if (tag === 'table' || tag === 'img' || tag === 'pre' || tag === 'marp-pre' || tag === 'blockquote') {
                return true;
            }
            return !!child.querySelector('table, img, pre, marp-pre, blockquote');
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
                const run = buildTextRunFromNode(child, el);
                if (run) {
                    inlineRuns.push(run);
                }
                continue;
            }
            if (child.nodeType !== Node.ELEMENT_NODE) continue;

            const tag = child.tagName.toLowerCase();
            const childContext = deriveRenderContext(child, containerContext);
            const childDecoration = extractDecoration(child, childContext);
            if (tag === 'ul' || tag === 'ol') {
                flushInlineParagraph();
                pushListParagraphs(child, 0, childContext);
            } else if (shouldExtractStandaloneDecoratedText(child, childDecoration)) {
                flushInlineParagraph();
            } else if (isInlineLikeElement(child)) {
                if (tag === 'br') {
                    flushInlineParagraph();
                } else {
                    const inlineChildContext = deriveRenderContext(child, containerContext);
                    inlineRuns.push(...extractInlineRuns(child, {
                        includeRootPseudo: true,
                        renderContext: inlineChildContext,
                    }));
                }
            } else if (!hasUnsupportedBlockDescendants(child)) {
                flushInlineParagraph();
                pushParagraphFromNode(child);
            }
        }
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

        if (el.querySelector('blockquote')) {
            return [];
        }

        if (cs.whiteSpace.includes('pre') || el.querySelector('br')) {
            return extractParagraphsFromLines(
                el.innerText,
                styleToRunStyle(cs, el, containerContext),
                alignment,
            );
        }

        const runs = extractTextRunsWithPseudo(el, containerContext);
        if (runs.length === 0) return [];
        const scaledMetrics = getParagraphMetrics(el, cs, containerContext);
        const paragraph = _buildParagraph(runs, alignment, scaledMetrics);
        return paragraph ? [paragraph] : [];
    }
