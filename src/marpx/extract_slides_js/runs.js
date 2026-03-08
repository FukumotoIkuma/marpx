    import {
        styleToRunStyle,
        extractPseudoRuns,
        extractDecoration,
        normalizeInlineText,
        deriveRenderContext,
    } from './entry.js';

    export function _buildTextRun(text, styleEl, linkUrl = null, options = {}) {
        const {
            normalizeWhitespace = true,
            styleOverride = null,
            renderContext = null,
        } = options;
        const normalizedText = normalizeWhitespace ? normalizeInlineText(text) : text;
        if (!normalizedText || normalizedText.length === 0) return null;
        return {
            text: normalizedText,
            style: styleOverride || styleToRunStyle(window.getComputedStyle(styleEl), styleEl, renderContext),
            linkUrl: linkUrl,
        };
    }

    export function extractInlineRuns(el, options = {}) {
        const {
            normalizeWhitespace = true,
            trimBoundary = true,
            includeRootPseudo = false,
            isStandaloneDecoratedFn = null,
            renderContext = null,
        } = options;
        const runs = [];
        const rootContext = renderContext || deriveRenderContext(el);

        function pushRun(
            text,
            styleEl,
            linkUrl = null,
            styleOverride = null,
            currentContext = rootContext,
        ) {
            const run = _buildTextRun(text, styleEl, linkUrl, {
                normalizeWhitespace,
                styleOverride,
                renderContext: currentContext,
            });
            if (run) runs.push(run);
        }

        function pushRootPseudo(pseudo) {
            const pseudoRuns = extractPseudoRuns(el, pseudo, rootContext);
            for (const run of pseudoRuns) {
                pushRun(run.text, el, run.linkUrl, run.style, rootContext);
            }
        }

        function visit(node, styleEl, linkUrl = null, currentContext = rootContext) {
            if (node.nodeType === Node.TEXT_NODE) {
                pushRun(node.textContent || '', styleEl, linkUrl, null, currentContext);
                return;
            }

            if (node.nodeType !== Node.ELEMENT_NODE) return;

            const nodeContext = node === el
                ? currentContext
                : deriveRenderContext(node, currentContext);

            if (node.tagName === 'BR') {
                runs.push({
                    text: '\n',
                    style: styleToRunStyle(window.getComputedStyle(styleEl), styleEl, currentContext),
                    linkUrl: linkUrl,
                });
                return;
            }

            const decoration = extractDecoration(node, nodeContext);
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
                    renderContext: nodeContext,
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
                visit(child, node, nextLinkUrl, nodeContext);
            }
        }

        if (includeRootPseudo) {
            pushRootPseudo('::before');
        }
        visit(el, el, null, rootContext);
        if (includeRootPseudo) {
            pushRootPseudo('::after');
        }

        return trimBoundary ? trimBoundaryWhitespace(runs) : runs;
    }

    export function extractTextRuns(el, renderContext = null) {
        return extractInlineRuns(el, { renderContext });
    }

    export function extractExactTextRuns(el, renderContext = null) {
        return extractInlineRuns(el, {
            normalizeWhitespace: false,
            trimBoundary: false,
            renderContext,
        });
    }

    export function extractTextRunsWithPseudo(el, renderContext = null) {
        return extractInlineRuns(el, { includeRootPseudo: true, renderContext });
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
