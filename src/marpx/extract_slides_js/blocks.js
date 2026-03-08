    import { extractDecoration, hasMeaningfulDecoration } from './entry.js';
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

    export function shouldExtractDecoratedBlock(el, decoration) {
        if (!hasMeaningfulDecoration(decoration)) return false;
        if (!isDecoratedBlockContainer(el)) return false;
        const paragraphs = extractParagraphsFromContainer(el);
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

    export function extractListItems(listEl, level) {
        const items = [];
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
                    items.push(...extractListItems(nested, level + 1));
                }
            }
        }
        return items;
    }

    export function extractTable(tableEl, sectionRect) {
        const rows = [];
        const trs = tableEl.querySelectorAll('tr');
        for (const tr of trs) {
            const cells = [];
            const tds = tr.querySelectorAll('th, td');
            for (const td of tds) {
                const cs = window.getComputedStyle(td);
                const rect = td.getBoundingClientRect();
                cells.push({
                    text: td.textContent.trim(),
                    runs: extractTextRuns(td),
                    isHeader: td.tagName === 'TH',
                    colspan: td.colSpan || 1,
                    rowspan: td.rowSpan || 1,
                    backgroundColor: cs.backgroundColor,
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
        if (cs.backgroundImage && cs.backgroundImage !== 'none' &&
            cs.backgroundImage.includes('gradient')) {
            return { reason: 'Gradient background', tagName: tag };
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
