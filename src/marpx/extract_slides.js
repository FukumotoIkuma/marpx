() => {
    const sections = document.querySelectorAll('section[id]');
    if (sections.length === 0) {
        // Try without id filter
        const allSections = document.querySelectorAll('section');
        // Filter to direct slide sections (not nested)
        var slideSections = Array.from(allSections).filter(s => {
            return s.parentElement && (
                s.parentElement.tagName === 'BODY' ||
                s.parentElement.classList.contains('marpit') ||
                s.parentElement.tagName === 'DIV'
            );
        });
        if (slideSections.length === 0) slideSections = Array.from(allSections);
    } else {
        var slideSections = Array.from(sections);
    }

    function getComputedStyles(el) {
        const cs = window.getComputedStyle(el);
        return {
            fontFamily: cs.fontFamily,
            fontSize: cs.fontSize,
            fontWeight: cs.fontWeight,
            fontStyle: cs.fontStyle,
            textDecoration: cs.textDecorationLine || cs.textDecoration,
            color: cs.color,
            textAlign: cs.textAlign,
            backgroundColor: cs.backgroundColor,
            lineHeight: cs.lineHeight,
            marginTop: cs.marginTop,
            marginBottom: cs.marginBottom,
        };
    }

    function buildTextElement(el, sectionRect, type, extra = {}) {
        const styles = getComputedStyles(el);
        return {
            type: type,
            box: getBox(el, sectionRect),
            zIndex: getZIndex(el),
            alignment: styles.textAlign,
            lineHeightPx: parseFloat(styles.lineHeight) || null,
            spaceBeforePx: parseFloat(styles.marginTop) || 0,
            spaceAfterPx: parseFloat(styles.marginBottom) || 0,
            ...extra,
        };
    }

    function getZIndex(el) {
        const raw = window.getComputedStyle(el).zIndex;
        const parsed = parseInt(raw, 10);
        return Number.isFinite(parsed) ? parsed : 0;
    }

    function normalizeContentValue(content) {
        if (!content || content === 'none' || content === 'normal') return null;
        if (
            (content.startsWith('"') && content.endsWith('"')) ||
            (content.startsWith("'") && content.endsWith("'"))
        ) {
            try {
                return JSON.parse(content);
            } catch (_err) {
                return content.slice(1, -1);
            }
        }
        return content;
    }

    function _runBackgroundColor(el, cs) {
        if (!el) return 'transparent';
        const tag = (el.localName || el.tagName || '').toLowerCase();
        const display = cs.display || '';
        if (
            display.startsWith('inline') ||
            ['code', 'mark', 'kbd', 'samp'].includes(tag)
        ) {
            return cs.backgroundColor;
        }
        return 'transparent';
    }

    function styleToRunStyle(cs, el = null) {
        return {
            fontFamily: cs.fontFamily,
            fontSizePx: parseFloat(cs.fontSize),
            bold: parseInt(cs.fontWeight) >= 600 || cs.fontWeight === 'bold',
            italic: cs.fontStyle === 'italic',
            underline: (cs.textDecorationLine || cs.textDecoration || '').includes('underline'),
            color: cs.color,
            backgroundColor: _runBackgroundColor(el, cs),
        };
    }

    function extractPseudoRuns(el, pseudo) {
        const cs = window.getComputedStyle(el, pseudo);
        const content = normalizeContentValue(cs.content);
        if (!content) return [];
        return [{
            text: content,
            style: styleToRunStyle(cs, el),
            linkUrl: null,
        }];
    }

    function extractDecoration(el) {
        const cs = window.getComputedStyle(el);
        const borderSide = (side) => {
            const width = parseFloat(cs[`border${side}Width`]) || 0;
            return {
                widthPx: width,
                style: cs[`border${side}Style`] || 'none',
                color: width > 0 ? cs[`border${side}Color`] : null,
            };
        };
        return {
            backgroundColor: cs.backgroundColor,
            borderTop: borderSide('Top'),
            borderRight: borderSide('Right'),
            borderBottom: borderSide('Bottom'),
            borderLeft: borderSide('Left'),
            borderRadiusPx: parseFloat(cs.borderTopLeftRadius) || 0,
            padding: {
                topPx: parseFloat(cs.paddingTop) || 0,
                rightPx: parseFloat(cs.paddingRight) || 0,
                bottomPx: parseFloat(cs.paddingBottom) || 0,
                leftPx: parseFloat(cs.paddingLeft) || 0,
            },
            opacity: parseFloat(cs.opacity || '1') || 1,
        };
    }

    function hasMeaningfulDecoration(decoration) {
        const normalizedBg = decoration.backgroundColor
            ? decoration.backgroundColor.replace(/\s+/g, '').toLowerCase()
            : '';
        const hasVisibleBackground = normalizedBg &&
            normalizedBg !== 'rgba(0,0,0,0)' &&
            normalizedBg !== 'transparent';
        const borders = [
            decoration.borderTop,
            decoration.borderRight,
            decoration.borderBottom,
            decoration.borderLeft,
        ];
        const hasVisibleBorder = borders.some(
            (b) => b.widthPx > 0 && b.style && b.style !== 'none'
        );
        const hasRadius = decoration.borderRadiusPx > 0;
        return hasVisibleBackground || hasVisibleBorder || hasRadius;
    }

    function getBox(el, sectionRect) {
        const rect = el.getBoundingClientRect();
        return {
            x: rect.left - sectionRect.left,
            y: rect.top - sectionRect.top,
            width: rect.width,
            height: rect.height,
        };
    }

    function extractTextRuns(el) {
        const runs = [];
        const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, null);
        let node;
        while (node = walker.nextNode()) {
            const text = normalizeInlineText(node.textContent || '');
            if (!text) continue;

            const parent = node.parentElement;
            const cs = window.getComputedStyle(parent);

            // Check for link
            let linkUrl = null;
            let ancestor = parent;
            while (ancestor && ancestor !== el) {
                if (ancestor.tagName === 'A' && ancestor.href) {
                    linkUrl = ancestor.href;
                    break;
                }
                ancestor = ancestor.parentElement;
            }

            runs.push({
                text: text,
                style: styleToRunStyle(cs, parent),
                linkUrl: linkUrl,
            });
        }
        return trimBoundaryWhitespace(runs);
    }

    function extractExactTextRuns(el) {
        const runs = [];

        function visit(node, styleEl, linkUrl = null) {
            if (node.nodeType === Node.TEXT_NODE) {
                const text = node.textContent || '';
                if (text.length === 0) return;
                runs.push({
                    text: text,
                    style: styleToRunStyle(window.getComputedStyle(styleEl), styleEl),
                    linkUrl: linkUrl,
                });
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

            let nextLinkUrl = linkUrl;
            if (node.tagName === 'A' && node.href) {
                nextLinkUrl = node.href;
            }

            for (const child of node.childNodes) {
                visit(child, node, nextLinkUrl);
            }
        }

        visit(el, el, null);
        return runs;
    }

    function splitRunsIntoParagraphs(runs, alignment, metrics, defaultStyle) {
        const paragraphs = [];
        let currentRuns = [];

        function pushParagraph() {
            paragraphs.push({
                runs: currentRuns.length > 0
                    ? currentRuns
                    : [{ text: ' ', style: defaultStyle, linkUrl: null }],
                alignment: alignment,
                lineHeightPx: metrics.lineHeightPx,
                spaceBeforePx: 0,
                spaceAfterPx: 0,
                listLevel: null,
                listOrdered: false,
            });
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

    function extractTextRunsWithPseudo(el) {
        return trimBoundaryWhitespace([
            ...extractPseudoRuns(el, '::before'),
            ...extractTextRuns(el),
            ...extractPseudoRuns(el, '::after'),
        ]);
    }

    function _hiddenRunStyle(style) {
        return {
            ...style,
            color: 'rgba(0, 0, 0, 0)',
            backgroundColor: 'transparent',
        };
    }

    function normalizeInlineText(text) {
        return text.replace(/\s+/g, ' ');
    }

    function trimBoundaryWhitespace(runs) {
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
        return trimmed.filter((run) => run.text.length > 0);
    }

    function extractTextRunsWithHiddenDecorated(el) {
        const runs = [];

        function visit(node, styleEl, linkUrl = null) {
            if (node.nodeType === Node.TEXT_NODE) {
                const text = normalizeInlineText(node.textContent || '');
                if (!text) return;
                runs.push({
                    text: text,
                    style: styleToRunStyle(window.getComputedStyle(styleEl), styleEl),
                    linkUrl: linkUrl,
                });
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
            if (shouldExtractStandaloneDecoratedText(node, decoration)) {
                for (const run of extractTextRunsWithPseudo(node)) {
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

        visit(el, el, null);
        return trimBoundaryWhitespace(runs);
    }

    function extractParagraphsFromLines(text, style, alignment) {
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

    function getParagraphMetrics(el, fallbackCs = null) {
        const cs = fallbackCs || window.getComputedStyle(el);
        const lineHeight = parseFloat(cs.lineHeight);
        return {
            lineHeightPx: Number.isFinite(lineHeight) ? lineHeight : null,
            spaceBeforePx: parseFloat(cs.marginTop) || 0,
            spaceAfterPx: parseFloat(cs.marginBottom) || 0,
        };
    }

    function extractParagraphsFromContainer(el) {
        const cs = window.getComputedStyle(el);
        const alignment = cs.textAlign;
        const paragraphs = [];
        const containerMetrics = {
            lineHeightPx: getParagraphMetrics(el, cs).lineHeightPx,
            spaceBeforePx: 0,
            spaceAfterPx: 0,
        };

        function pushParagraph(runs, metrics = containerMetrics, paragraphAlignment = alignment) {
            const normalizedRuns = trimBoundaryWhitespace(runs);
            if (normalizedRuns.length === 0) return;
            paragraphs.push({
                runs: normalizedRuns,
                alignment: paragraphAlignment,
                lineHeightPx: metrics.lineHeightPx,
                spaceBeforePx: metrics.spaceBeforePx,
                spaceAfterPx: metrics.spaceAfterPx,
                listLevel: null,
                listOrdered: false,
            });
        }

        function pushParagraphFromNode(child) {
            const childRuns = extractTextRunsWithPseudo(child);
            if (childRuns.length === 0) return;
            const metrics = getParagraphMetrics(child);
            pushParagraph(
                childRuns,
                metrics,
                window.getComputedStyle(child).textAlign || alignment,
            );
        }

        function buildTextRunFromNode(node, styleEl) {
            const text = normalizeInlineText(node.textContent || '');
            if (!text.trim()) return null;
            return {
                text: text,
                style: styleToRunStyle(window.getComputedStyle(styleEl)),
                linkUrl: null,
            };
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
                const itemCs = window.getComputedStyle(item);
                const currentOrder = listEl.tagName === 'OL'
                    ? (parseInt(item.value, 10) || orderedIndex)
                    : null;
                if (listEl.tagName === 'OL') {
                    orderedIndex = currentOrder + 1;
                }
                const runs = [];
                const nestedLists = [];
                for (const node of item.childNodes) {
                    if (node.nodeType === Node.TEXT_NODE) {
                        const text = node.textContent.trim();
                        if (text) {
                            runs.push({
                                text,
                                style: styleToRunStyle(itemCs),
                                linkUrl: null,
                            });
                        }
                    } else if (node.nodeType === Node.ELEMENT_NODE) {
                        if (node.tagName === 'UL' || node.tagName === 'OL') {
                            nestedLists.push(node);
                        } else {
                            runs.push(...extractTextRunsWithPseudo(node));
                        }
                    }
                }
                if (runs.length > 0) {
                    const metrics = getParagraphMetrics(item);
                    paragraphs.push({
                        runs: [
                            ...extractPseudoRuns(item, '::before'),
                            ...runs,
                            ...extractPseudoRuns(item, '::after'),
                        ],
                        alignment: window.getComputedStyle(item).textAlign || alignment,
                        lineHeightPx: metrics.lineHeightPx,
                        spaceBeforePx: metrics.spaceBeforePx,
                        spaceAfterPx: metrics.spaceAfterPx,
                        listLevel: level,
                        listOrdered: listEl.tagName === 'OL',
                        listStyleType: itemCs.listStyleType || window.getComputedStyle(listEl).listStyleType || null,
                        orderNumber: currentOrder,
                    });
                }
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
                    inlineRuns.push(...extractTextRunsWithPseudo(child));
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
        return [{
            runs: runs,
            alignment: alignment,
            lineHeightPx: metrics.lineHeightPx,
            spaceBeforePx: metrics.spaceBeforePx,
            spaceAfterPx: metrics.spaceAfterPx,
            listLevel: null,
            listOrdered: false,
        }];
    }

    function isDecoratedBlockContainer(el) {
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

    function shouldExtractDecoratedBlock(el, decoration) {
        if (!hasMeaningfulDecoration(decoration)) return false;
        if (!isDecoratedBlockContainer(el)) return false;
        const paragraphs = extractParagraphsFromContainer(el);
        return paragraphs.length > 0 || shouldDecomposeDecoratedBlock(el);
    }

    function shouldExtractStandaloneDecoratedText(el, decoration) {
        if (!hasMeaningfulDecoration(decoration)) return false;
        const tag = (el.localName || el.tagName).toLowerCase();
        if (tag === 'code') return false;
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

    function shouldDecomposeDecoratedBlock(el) {
        return Array.from(el.children).some((child) =>
            shouldExtractStandaloneDecoratedText(child, extractDecoration(child)) ||
            ['table', 'img', 'pre', 'marp-pre'].includes(
                (child.localName || child.tagName).toLowerCase()
            ) ||
            !!child.querySelector('table, img, pre, marp-pre')
        );
    }

    function extractListItems(listEl, level) {
        const items = [];
        let orderedIndex = listEl.tagName === 'OL' ? (listEl.start || 1) : 1;
        for (const child of listEl.children) {
            if (child.tagName === 'LI') {
                const childCs = window.getComputedStyle(child);
                const childMetrics = getParagraphMetrics(child, childCs);
                const currentOrder = listEl.tagName === 'OL'
                    ? (parseInt(child.value, 10) || orderedIndex)
                    : null;
                if (listEl.tagName === 'OL') {
                    orderedIndex = currentOrder + 1;
                }
                // Two-pass: first collect runs, then collect nested lists
                const runs = [];
                const nestedLists = [];
                for (const node of child.childNodes) {
                    if (node.nodeType === Node.TEXT_NODE) {
                        const text = normalizeInlineText(node.textContent || '');
                        if (text.trim()) {
                            runs.push({
                                text: text,
                                style: {
                                    fontFamily: childCs.fontFamily,
                                    fontSizePx: parseFloat(childCs.fontSize),
                                    bold: parseInt(childCs.fontWeight) >= 600,
                                    italic: childCs.fontStyle === 'italic',
                                    underline: false,
                                    color: childCs.color,
                                    backgroundColor: _runBackgroundColor(child, childCs),
                                },
                                linkUrl: null,
                            });
                        }
                    } else if (node.nodeType === Node.ELEMENT_NODE) {
                        if (node.tagName === 'UL' || node.tagName === 'OL') {
                            nestedLists.push(node);
                        } else {
                            // Inline elements within li
                            const inlineRuns = extractTextRuns(node);
                            runs.push(...inlineRuns);
                        }
                    }
                }
                // Push parent item first
                const normalizedRuns = trimBoundaryWhitespace(runs);
                if (normalizedRuns.length > 0) {
                    const beforeRuns = extractPseudoRuns(child, '::before');
                    const afterRuns = extractPseudoRuns(child, '::after');
                    items.push({
                        runs: [...beforeRuns, ...normalizedRuns, ...afterRuns],
                        level: level,
                        isOrdered: listEl.tagName === 'OL',
                        orderNumber: currentOrder,
                        listStyleType: childCs.listStyleType || window.getComputedStyle(listEl).listStyleType || null,
                        alignment: childCs.textAlign || 'left',
                        lineHeightPx: childMetrics.lineHeightPx,
                        spaceBeforePx: childMetrics.spaceBeforePx,
                        spaceAfterPx: childMetrics.spaceAfterPx,
                    });
                }
                // Then push nested list items
                for (const nested of nestedLists) {
                    items.push(...extractListItems(nested, level + 1));
                }
            }
        }
        return items;
    }

    function extractTable(tableEl, sectionRect) {
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

    function _findSingleImageChild(el) {
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

    function isUnsupported(el) {
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

    const slides = [];
    let slideIndex = 0;

    for (let i = 0; i < slideSections.length; i++) {
        const section = slideSections[i];

        // Check if this section is part of Marp's advanced background structure
        const advBg = section.getAttribute('data-marpit-advanced-background');
        if (advBg === 'background' || advBg === 'pseudo') {
            // Skip - we process these when we find the 'content' section
            continue;
        }

        const sectionRect = section.getBoundingClientRect();
        const slideRoot = section.closest('svg') || section;
        const slideRect = slideRoot.getBoundingClientRect();
        const cs = window.getComputedStyle(section);

        // Extract background images from advanced background structure
        let bgImages = [];
        if (advBg === 'content') {
            // Find the matching background section within the same slide root.
            const bgSection = slideRoot.querySelector(
                'section[data-marpit-advanced-background="background"]'
            );
            if (bgSection) {
                const figures = bgSection.querySelectorAll('figure');
                for (const fig of figures) {
                    const figCs = window.getComputedStyle(fig);
                    const bgImg = figCs.backgroundImage;
                    if (bgImg && bgImg !== 'none') {
                        // Extract URL from url("...")
                        const urlMatch = bgImg.match(/url\(["']?([^"')]+)["']?\)/);
                        if (urlMatch) {
                            bgImages.push({
                                url: urlMatch[1],
                                size: figCs.backgroundSize || 'cover',
                                position: figCs.backgroundPosition || 'center',
                            });
                        }
                    }
                }
            }
            // Check for split background
            const split = section.getAttribute('data-marpit-advanced-background-split');
            if (split) {
                for (const bg of bgImages) {
                    bg.split = split;
                }
            }
        }

        // Extract directives
        const paginate = section.getAttribute('data-paginate') === 'true';
        const paginationNum = section.getAttribute('data-marpit-pagination');
        const paginationTotal = section.getAttribute('data-marpit-pagination-total');

        // Extract header/footer elements
        const headerEl = section.querySelector(':scope > header');
        const footerEl = section.querySelector(':scope > footer');

        const slideData = {
            width: slideRect.width,
            height: slideRect.height,
            slideNumber: slideIndex++,
            background: {
                color: cs.backgroundColor,
                images: bgImages,
            },
            directives: {
                paginate: paginate,
                pageNumber: paginationNum ? parseInt(paginationNum) : null,
                pageTotal: paginationTotal ? parseInt(paginationTotal) : null,
                headerText: headerEl ? headerEl.textContent.trim() : null,
                footerText: footerEl ? footerEl.textContent.trim() : null,
            },
            elements: [],
        };

        // Process direct children and nested content
        const processElement = (el) => {
            const tag = (el.localName || el.tagName).toLowerCase();

            // Skip script, style, header, footer, etc.
            if (['script', 'style', 'link', 'meta', 'header', 'footer'].includes(tag)) return;

            // Check for unsupported
            const unsup = isUnsupported(el);
            if (unsup) {
                slideData.elements.push({
                    type: 'unsupported',
                    box: getBox(el, slideRect),
                    zIndex: getZIndex(el),
                    unsupportedInfo: unsup,
                });
                return; // Don't descend into unsupported subtrees
            }

            // Math containers (MathJax)
            if (tag === 'mjx-container' || (el.classList && el.classList.contains('MathJax'))) {
                slideData.elements.push({
                    type: 'math',
                    box: getBox(el, slideRect),
                    zIndex: getZIndex(el),
                    unsupportedInfo: { reason: 'Math expression (MathJax)', tagName: tag },
                });
                return; // Don't descend into MathJax SVG
            }

            const decoration = extractDecoration(el);

            if (shouldExtractStandaloneDecoratedText(el, decoration)) {
                slideData.elements.push({
                    type: 'decorated_block',
                    box: getBox(el, slideRect),
                    zIndex: getZIndex(el),
                    paragraphs: extractParagraphsFromContainer(el),
                    decoration: decoration,
                });
                return;
            }

            const singleImageChild = _findSingleImageChild(el);
            if (singleImageChild && hasMeaningfulDecoration(decoration)) {
                const box = getBox(el, slideRect);
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
                        decoration: decoration,
                    });
                }
                return;
            }

            if (shouldExtractDecoratedBlock(el, decoration)) {
                const decomposeDecoratedBlock = shouldDecomposeDecoratedBlock(el);
                slideData.elements.push({
                    type: 'decorated_block',
                    box: getBox(el, slideRect),
                    zIndex: getZIndex(el),
                    paragraphs: decomposeDecoratedBlock ? [] : extractParagraphsFromContainer(el),
                    decoration: decoration,
                });
                if (decomposeDecoratedBlock) {
                    for (const child of el.children) {
                        processElement(child);
                    }
                }
                return;
            }

            // Headings
            if (/^h[1-6]$/.test(tag)) {
                const level = parseInt(tag[1]);
                slideData.elements.push(
                    buildTextElement(el, slideRect, 'heading', {
                        headingLevel: level,
                        runs: extractTextRuns(el),
                    })
                );
                return;
            }

            // Paragraphs
            if (tag === 'p' || tag === 'figcaption') {
                if (el.querySelector('img') && !el.textContent.trim()) {
                    for (const child of el.children) {
                        processElement(child);
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
                    shouldExtractStandaloneDecoratedText(child, extractDecoration(child))
                );

                slideData.elements.push(
                    buildTextElement(el, slideRect, 'paragraph', {
                        runs: decoratedChildren.length > 0
                            ? extractTextRunsWithHiddenDecorated(el)
                            : extractTextRunsWithPseudo(el),
                    })
                );
                for (const child of decoratedChildren) {
                    processElement(child);
                }
                return;
            }

            // Blockquote
            if (tag === 'blockquote') {
                slideData.elements.push(
                    buildTextElement(el, slideRect, 'blockquote', {
                        runs: extractTextRunsWithPseudo(el),
                        decoration: hasMeaningfulDecoration(decoration)
                            ? decoration
                            : null,
                    })
                );
                return;
            }

            // Lists
            if (tag === 'ul') {
                slideData.elements.push({
                    type: 'unordered_list',
                    box: getBox(el, slideRect),
                    zIndex: getZIndex(el),
                    listItems: extractListItems(el, 0),
                });
                return;
            }
            if (tag === 'ol') {
                slideData.elements.push({
                    type: 'ordered_list',
                    box: getBox(el, slideRect),
                    zIndex: getZIndex(el),
                    listItems: extractListItems(el, 0),
                });
                return;
            }

            // Code blocks
            if (tag === 'pre' || tag === 'marp-pre') {
                const codeEl = el.querySelector('code');
                if (codeEl) {
                    const styles = getComputedStyles(el);
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
                        zIndex: getZIndex(el),
                        paragraphs: splitRunsIntoParagraphs(
                            extractExactTextRuns(codeEl),
                            alignment,
                            metrics,
                            styleToRunStyle(window.getComputedStyle(codeEl)),
                        ),
                        codeLanguage: lang ? lang.replace('language-', '') : null,
                        codeBackground: styles.backgroundColor,
                    });
                    return;
                }
            }

            // Images
            if (tag === 'img') {
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
                        decoration: hasMeaningfulDecoration(decoration)
                            ? decoration
                            : null,
                    });
                }
                return;
            }

            // Tables
            if (tag === 'table') {
                slideData.elements.push({
                    type: 'table',
                    box: getBox(el, slideRect),
                    zIndex: getZIndex(el),
                    tableRows: extractTable(el, slideRect),
                });
                return;
            }

            // For other elements, recurse into children
            for (const child of el.children) {
                processElement(child);
            }
        };

        for (const child of section.children) {
            processElement(child);
        }

        slides.push(slideData);
    }

    return slides;
}
