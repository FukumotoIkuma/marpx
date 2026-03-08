    import { styleToRunStyle, extractPseudoRuns, extractDecoration } from './entry.js';
    import { _buildTextRun, extractInlineRuns, extractTextRunsWithPseudo } from './runs.js';
    import { _buildParagraph, extractParagraphsFromLines, getParagraphMetrics } from './paragraphs.js';
    import { shouldExtractStandaloneDecoratedText } from './classify.js';

    export function extractListItemContent(item, listEl, level, currentOrder) {
        const itemCs = window.getComputedStyle(item);
        const metrics = getParagraphMetrics(item, itemCs);
        const runs = [];
        const nestedLists = [];

        for (const node of item.childNodes) {
            if (node.nodeType === Node.TEXT_NODE) {
                const run = _buildTextRun(node.textContent || '', item, null);
                if (run && run.text.trim()) runs.push(run);
                continue;
            }
            if (node.nodeType !== Node.ELEMENT_NODE) continue;
            if (node.tagName === 'UL' || node.tagName === 'OL') {
                nestedLists.push(node);
                continue;
            }
            runs.push(...extractInlineRuns(node, { includeRootPseudo: true }));
        }

        const paragraph = _buildParagraph(
            [
                ...extractPseudoRuns(item, '::before'),
                ...runs,
                ...extractPseudoRuns(item, '::after'),
            ],
            itemCs.textAlign || window.getComputedStyle(listEl).textAlign || 'left',
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

    export function extractParagraphsFromContainer(el) {
        const cs = window.getComputedStyle(el);
        const alignment = cs.textAlign;
        const paragraphs = [];
        const containerMetrics = {
            lineHeightPx: getParagraphMetrics(el, cs).lineHeightPx,
            spaceBeforePx: 0,
            spaceAfterPx: 0,
        };

        function pushParagraph(runs, metrics = containerMetrics, paragraphAlignment = alignment) {
            const paragraph = _buildParagraph(runs, paragraphAlignment, metrics);
            if (paragraph) paragraphs.push(paragraph);
        }

        function pushParagraphFromNode(child) {
            const childRuns = extractInlineRuns(child, { includeRootPseudo: true });
            if (childRuns.length === 0) return;
            const metrics = getParagraphMetrics(child);
            pushParagraph(
                childRuns,
                metrics,
                window.getComputedStyle(child).textAlign || alignment,
            );
        }

        function buildTextRunFromNode(node, styleEl) {
            const run = _buildTextRun(node.textContent || '', styleEl);
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
            return !!child.querySelector('table, img, pre, marp-pre, blockquote');
        }

        function pushListParagraphs(listEl, level) {
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
                );
                if (paragraph) paragraphs.push(paragraph);
                for (const nested of nestedLists) {
                    pushListParagraphs(nested, level + 1);
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
            const childDecoration = extractDecoration(child);
            if (tag === 'ul' || tag === 'ol') {
                flushInlineParagraph();
                pushListParagraphs(child, 0);
            } else if (shouldExtractStandaloneDecoratedText(child, childDecoration)) {
                flushInlineParagraph();
            } else if (isInlineLikeElement(child)) {
                if (tag === 'br') {
                    flushInlineParagraph();
                } else {
                    inlineRuns.push(...extractInlineRuns(child, { includeRootPseudo: true }));
                }
            } else if (!hasUnsupportedBlockDescendants(child)) {
                flushInlineParagraph();
                pushParagraphFromNode(child);
            }
        }
        flushInlineParagraph();

        if (paragraphs.length > 0) {
            const beforeRuns = extractPseudoRuns(el, '::before');
            const afterRuns = extractPseudoRuns(el, '::after');
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

        if (cs.whiteSpace.includes('pre') || el.querySelector('br')) {
            return extractParagraphsFromLines(el.innerText, styleToRunStyle(cs), alignment);
        }

        const runs = extractTextRunsWithPseudo(el);
        if (runs.length === 0) return [];
        const metrics = getParagraphMetrics(el, cs);
        const paragraph = _buildParagraph(runs, alignment, metrics);
        return paragraph ? [paragraph] : [];
    }
