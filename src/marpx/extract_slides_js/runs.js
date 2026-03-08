    import { styleToRunStyle, extractPseudoRuns, extractDecoration, normalizeInlineText } from './entry.js';

    export function _buildTextRun(text, styleEl, linkUrl = null, options = {}) {
        const { normalizeWhitespace = true, styleOverride = null } = options;
        const normalizedText = normalizeWhitespace ? normalizeInlineText(text) : text;
        if (!normalizedText || normalizedText.length === 0) return null;
        return {
            text: normalizedText,
            style: styleOverride || styleToRunStyle(window.getComputedStyle(styleEl), styleEl),
            linkUrl: linkUrl,
        };
    }

    export function extractInlineRuns(el, options = {}) {
        const {
            normalizeWhitespace = true,
            trimBoundary = true,
            includeRootPseudo = false,
            isStandaloneDecoratedFn = null,
        } = options;
        const runs = [];

        function pushRun(text, styleEl, linkUrl = null, styleOverride = null) {
            const run = _buildTextRun(text, styleEl, linkUrl, {
                normalizeWhitespace,
                styleOverride,
            });
            if (run) runs.push(run);
        }

        function pushRootPseudo(pseudo) {
            const pseudoRuns = extractPseudoRuns(el, pseudo);
            for (const run of pseudoRuns) {
                pushRun(run.text, el, run.linkUrl, run.style);
            }
        }

        function visit(node, styleEl, linkUrl = null) {
            if (node.nodeType === Node.TEXT_NODE) {
                pushRun(node.textContent || '', styleEl, linkUrl);
                return;
            }

            if (node.nodeType !== Node.ELEMENT_NODE) return;

            if (node.tagName === 'BR') {
                runs.push({
                    text: '\n',
                    style: styleToRunStyle(window.getComputedStyle(styleEl), styleEl),
                    linkUrl: linkUrl,
                });
                return;
            }

            const decoration = extractDecoration(node);
            if (
                isStandaloneDecoratedFn &&
                node !== el &&
                isStandaloneDecoratedFn(node, decoration)
            ) {
                const hiddenRuns = extractInlineRuns(node, {
                    normalizeWhitespace,
                    trimBoundary: false,
                    includeRootPseudo: true,
                    isStandaloneDecoratedFn: null,
                });
                for (const run of hiddenRuns) {
                    runs.push({
                        text: run.text,
                        style: _hiddenRunStyle(run.style),
                        linkUrl: run.linkUrl,
                    });
                }
                return;
            }

            let nextLinkUrl = linkUrl;
            if (node.tagName === 'A' && node.href) {
                nextLinkUrl = node.href;
            }

            for (const child of node.childNodes) {
                visit(child, node, nextLinkUrl);
            }
        }

        if (includeRootPseudo) {
            pushRootPseudo('::before');
        }
        visit(el, el, null);
        if (includeRootPseudo) {
            pushRootPseudo('::after');
        }

        return trimBoundary ? trimBoundaryWhitespace(runs) : runs;
    }

    export function extractTextRuns(el) {
        return extractInlineRuns(el);
    }

    export function extractExactTextRuns(el) {
        return extractInlineRuns(el, {
            normalizeWhitespace: false,
            trimBoundary: false,
        });
    }

    export function extractTextRunsWithPseudo(el) {
        return extractInlineRuns(el, { includeRootPseudo: true });
    }

    function _hiddenRunStyle(style) {
        return {
            ...style,
            color: 'rgba(0, 0, 0, 0)',
            backgroundColor: 'transparent',
        };
    }

    export function trimBoundaryWhitespace(runs) {
        const trimmed = runs
            .map((run) => ({ ...run }))
            .filter((run) => run.text && run.text.length > 0);
        while (trimmed.length > 0 && trimmed[0].text.trim() === '') {
            trimmed.shift();
        }
        while (
            trimmed.length > 0 &&
            trimmed[trimmed.length - 1].text.trim() === ''
        ) {
            trimmed.pop();
        }
        if (trimmed.length === 0) return [];
        trimmed[0].text = trimmed[0].text.replace(/^\s+/, '');
        trimmed[trimmed.length - 1].text = trimmed[
            trimmed.length - 1
        ].text.replace(/\s+$/, '');
        for (let i = 1; i < trimmed.length; i++) {
            if (trimmed[i - 1].text.endsWith('\n')) {
                trimmed[i].text = trimmed[i].text.replace(/^\s+/, '');
            }
        }
        return trimmed.filter((run) => run.text.length > 0);
    }

