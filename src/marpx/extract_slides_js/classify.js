    import { extractDecoration, hasMeaningfulDecoration } from './entry.js';
    import { extractParagraphsFromContainer } from './containers.js';
    import { extractInlineRuns } from './runs.js';

export function shouldExtractStandaloneDecoratedText(el, decoration) {
    if (!hasMeaningfulDecoration(decoration)) return false;
    const tag = (el.localName || el.tagName).toLowerCase();
    if (tag === 'code' || tag === 'mark') return false;
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
        return extractParagraphsFromContainer(el).length > 0;
    }

export function extractTextRunsWithHiddenDecorated(
    el,
    renderContext = null,
    includeMathPlaceholders = false,
    extraStandaloneFn = null,
) {
    return extractInlineRuns(el, {
        renderContext,
        includeMathPlaceholders,
        isStandaloneDecoratedFn: (node, decoration) =>
            shouldExtractStandaloneDecoratedText(node, decoration) ||
            (extraStandaloneFn ? extraStandaloneFn(node) : false),
    });
}
