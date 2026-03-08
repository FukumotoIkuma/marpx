    import {
        extractDecoration,
        hasMeaningfulDecoration,
        deriveRenderContext,
        deriveSubtreeRenderContext,
    } from './entry.js';
    import { extractTextRuns } from './runs.js';
    import { extractListItemContent, extractParagraphsFromContainer } from './containers.js';
    import { shouldExtractStandaloneDecoratedText } from './classify.js';

    export function isDecoratedBlockContainer(el) {
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
        return !display.startsWith('inline');
    }

    export function shouldExtractDecoratedBlock(el, decoration, renderContext = null) {
        if (!hasMeaningfulDecoration(decoration)) return false;
        if (!isDecoratedBlockContainer(el)) return false;
        const paragraphs = extractParagraphsFromContainer(el, renderContext);
        return paragraphs.length > 0 || shouldDecomposeDecoratedBlock(el);
    }

    export function shouldDecomposeDecoratedBlock(el) {
        return Array.from(el.children).some((child) =>
            shouldExtractStandaloneDecoratedText(child, extractDecoration(child)) ||
            ['table', 'img', 'pre', 'marp-pre'].includes(
                (child.localName || child.tagName).toLowerCase()
            ) ||
            !!child.querySelector('table, img, pre, marp-pre')
        );
    }

    export function extractListItems(listEl, level, renderContext = null) {
        const items = [];
        const listContext = renderContext || deriveRenderContext(listEl);
        let orderedIndex = listEl.tagName === 'OL' ? (listEl.start || 1) : 1;
        for (const child of listEl.children) {
            if (child.tagName === 'LI') {
                const currentOrder = listEl.tagName === 'OL'
                    ? (parseInt(child.value, 10) || orderedIndex)
                    : null;
                if (listEl.tagName === 'OL') {
                    orderedIndex = currentOrder + 1;
                }
                const { paragraph, nestedLists } = extractListItemContent(
                    child,
                    listEl,
                    level,
                    currentOrder,
                    listContext,
                );
                if (paragraph) {
                    items.push({
                        runs: paragraph.runs,
                        level: paragraph.listLevel,
                        isOrdered: paragraph.listOrdered,
                        orderNumber: paragraph.orderNumber,
                        listStyleType: paragraph.listStyleType,
                        alignment: paragraph.alignment,
                        lineHeightPx: paragraph.lineHeightPx,
                        spaceBeforePx: paragraph.spaceBeforePx,
                        spaceAfterPx: paragraph.spaceAfterPx,
                    });
                }
                for (const nested of nestedLists) {
                    const nestedListContext = deriveRenderContext(nested, listContext);
                    items.push(...extractListItems(nested, level + 1, nestedListContext));
                }
            }
        }
        return items;
    }

    function _hasVisibleBackground(backgroundColor, backgroundGradient) {
        if (backgroundGradient && backgroundGradient !== 'none') return true;
        const normalized = backgroundColor
            ? backgroundColor.replace(/\s+/g, '').toLowerCase()
            : '';
        return !!(
            normalized &&
            normalized !== 'transparent' &&
            normalized !== 'rgba(0,0,0,0)'
        );
    }

    function _resolveTableCellBackground(td, tableEl, tableContext) {
        let current = td;
        while (current && tableEl.contains(current)) {
            const currentContext = deriveSubtreeRenderContext(current, tableEl, tableContext);
            const decoration = extractDecoration(current, currentContext);
            if (_hasVisibleBackground(decoration.backgroundColor, decoration.backgroundGradient)) {
                return decoration;
            }
            if (current === tableEl) {
                break;
            }
            current = current.parentElement;
        }
        return null;
    }

    export function extractTable(tableEl, sectionRect, renderContext = null) {
        const rows = [];
        const tableContext = renderContext || deriveRenderContext(tableEl);
        const trs = tableEl.querySelectorAll('tr');
        for (const tr of trs) {
            const rowContext = deriveSubtreeRenderContext(tr, tableEl, tableContext);
            const cells = [];
            const tds = tr.querySelectorAll('th, td');
            for (const td of tds) {
                const cs = window.getComputedStyle(td);
                const cellContext = deriveRenderContext(td, rowContext, cs);
                const rect = td.getBoundingClientRect();
                const cellDecoration = extractDecoration(td, cellContext);
                const effectiveBackground = _resolveTableCellBackground(
                    td,
                    tableEl,
                    tableContext,
                );
                cells.push({
                    text: td.textContent.trim(),
                    runs: extractTextRuns(td, cellContext),
                    isHeader: td.tagName === 'TH',
                    colspan: td.colSpan || 1,
                    rowspan: td.rowSpan || 1,
                    backgroundColor: effectiveBackground ? effectiveBackground.backgroundColor : 'transparent',
                    backgroundGradient: effectiveBackground ? effectiveBackground.backgroundGradient : null,
                    padding: cellDecoration.padding,
                    borderTop: cellDecoration.borderTop,
                    borderRight: cellDecoration.borderRight,
                    borderBottom: cellDecoration.borderBottom,
                    borderLeft: cellDecoration.borderLeft,
                    widthPx: rect.width,
                });
            }
            rows.push({ cells: cells });
        }
        return rows;
    }

    export function _findSingleImageChild(el) {
        const images = el.querySelectorAll(':scope > img');
        if (images.length !== 1) return null;
        const directChildren = Array.from(el.children);
        if (directChildren.length !== 1) return null;
        const text = Array.from(el.childNodes)
            .filter((node) => node.nodeType === Node.TEXT_NODE)
            .map((node) => node.textContent || '')
            .join('')
            .trim();
        if (text.length > 0) return null;
        return images[0];
    }

    export function isUnsupported(el) {
        const tag = (el.localName || el.tagName).toLowerCase();
        if (['svg', 'math', 'canvas'].includes(tag)) {
            return {
                reason: 'Unsupported element: ' + tag,
                tagName: tag,
                svgMarkup: tag === 'svg' ? el.outerHTML : null,
            };
        }
        const cs = window.getComputedStyle(el);
        if (
            cs.backgroundImage &&
            cs.backgroundImage !== 'none' &&
            cs.backgroundImage.includes('gradient') &&
            !cs.backgroundImage.includes('linear-gradient(')
        ) {
            return { reason: 'Unsupported gradient background', tagName: tag };
        }
        const transform = cs.transform;
        if (transform && transform !== 'none' && transform !== 'matrix(1, 0, 0, 1, 0, 0)') {
            // Check if it's a significant transform (rotation or skew)
            const m = transform.match(/matrix\(([^)]+)\)/);
            if (m) {
                const vals = m[1].split(',').map(Number);
                // Significant rotation or skew
                if (Math.abs(vals[1]) > 0.01 || Math.abs(vals[2]) > 0.01) {
                    return { reason: 'Complex CSS transform', tagName: tag };
                }
            }
        }
        return null;
    }
