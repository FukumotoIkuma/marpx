    import { deriveRenderContext, styleToRunStyle } from './entry.js';
    import { trimBoundaryWhitespace } from './runs.js';

    export function _buildParagraph(runs, alignment, metrics, extra = {}) {
        const { trimRuns = true, ...paragraphExtra } = extra;
        const normalizedRuns = trimRuns ? trimBoundaryWhitespace(runs) : runs
            .map((run) => ({ ...run }))
            .filter((run) => run.text && run.text.length > 0);
        if (normalizedRuns.length === 0) return null;
        return {
            runs: normalizedRuns,
            alignment: alignment,
            lineHeightPx: metrics.lineHeightPx,
            spaceBeforePx: metrics.spaceBeforePx,
            spaceAfterPx: metrics.spaceAfterPx,
            listLevel: null,
            listOrdered: false,
            ...paragraphExtra,
        };
    }

    export function buildParagraphsFromRuns(runs, alignment, metrics, defaultStyle, extra = {}) {
        const paragraphs = [];
        let currentRuns = [];

        function pushParagraph() {
            const paragraph = _buildParagraph(
                currentRuns.length > 0
                    ? currentRuns
                    : [{ text: ' ', style: defaultStyle, linkUrl: null }],
                alignment,
                {
                    lineHeightPx: metrics.lineHeightPx,
                    spaceBeforePx: 0,
                    spaceAfterPx: 0,
                },
                extra,
            );
            if (paragraph) paragraphs.push(paragraph);
            currentRuns = [];
        }

        for (const run of runs) {
            const parts = run.text.split('\n');
            for (let i = 0; i < parts.length; i++) {
                if (parts[i].length > 0) {
                    currentRuns.push({
                        text: parts[i],
                        style: run.style,
                        linkUrl: run.linkUrl,
                    });
                }
                if (i < parts.length - 1) {
                    pushParagraph();
                }
            }
        }

        if (currentRuns.length > 0 || paragraphs.length === 0) {
            pushParagraph();
        }

        const last = paragraphs[paragraphs.length - 1];
        if (
            last &&
            last.runs.length === 1 &&
            last.runs[0].text === ' ' &&
            runs.length > 0 &&
            runs[runs.length - 1].text.endsWith('\n')
        ) {
            paragraphs.pop();
        }

        return paragraphs;
    }

    export function extractParagraphsFromLines(text, style, alignment) {
        const lines = text
            .split(/\r?\n/)
            .map((line) => line.trimEnd())
            .filter((line, index, all) => line.length > 0 || (all.length === 1 && index === 0));
        return lines.map((line) => ({
            runs: [{ text: line || ' ', style: style, linkUrl: null }],
            alignment: alignment,
            lineHeightPx: style.lineHeightPx || null,
            spaceBeforePx: 0,
            spaceAfterPx: 0,
            listLevel: null,
            listOrdered: false,
        }));
    }

    export function getParagraphMetrics(el, fallbackCs = null, renderContext = null) {
        const cs = fallbackCs || window.getComputedStyle(el);
        const ctx = renderContext || deriveRenderContext(el, null, cs);
        const lineHeight = parseFloat(cs.lineHeight);
        return {
            lineHeightPx: Number.isFinite(lineHeight)
                ? lineHeight * ctx.effectiveScaleY
                : null,
            spaceBeforePx: (parseFloat(cs.marginTop) || 0) * ctx.effectiveScaleY,
            spaceAfterPx: (parseFloat(cs.marginBottom) || 0) * ctx.effectiveScaleY,
        };
    }
