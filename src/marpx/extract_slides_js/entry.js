    export function getComputedStyles(el) {
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

    export function buildTextElement(el, sectionRect, type, extra = {}) {
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

    export function getZIndex(el) {
        const raw = window.getComputedStyle(el).zIndex;
        const parsed = parseInt(raw, 10);
        return Number.isFinite(parsed) ? parsed : 0;
    }

    export function normalizeContentValue(content) {
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

    export function styleToRunStyle(cs, el = null) {
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

    export function extractPseudoRuns(el, pseudo) {
        const cs = window.getComputedStyle(el, pseudo);
        const content = normalizeContentValue(cs.content);
        if (!content) return [];
        return [{
            text: content,
            style: styleToRunStyle(cs, el),
            linkUrl: null,
        }];
    }

    export function extractDecoration(el) {
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

    export function hasMeaningfulDecoration(decoration) {
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

    export function getBox(el, sectionRect) {
        const rect = el.getBoundingClientRect();
        return {
            x: rect.left - sectionRect.left,
            y: rect.top - sectionRect.top,
            width: rect.width,
            height: rect.height,
        };
    }

    export function getContentBox(el, sectionRect) {
        const rect = el.getBoundingClientRect();
        const cs = window.getComputedStyle(el);
        const leftInset = (parseFloat(cs.borderLeftWidth) || 0) + (parseFloat(cs.paddingLeft) || 0);
        const topInset = (parseFloat(cs.borderTopWidth) || 0) + (parseFloat(cs.paddingTop) || 0);
        const rightInset = (parseFloat(cs.borderRightWidth) || 0) + (parseFloat(cs.paddingRight) || 0);
        const bottomInset = (parseFloat(cs.borderBottomWidth) || 0) + (parseFloat(cs.paddingBottom) || 0);
        return {
            x: rect.left - sectionRect.left + leftInset,
            y: rect.top - sectionRect.top + topInset,
            width: Math.max(rect.width - leftInset - rightInset, 1),
            height: Math.max(rect.height - topInset - bottomInset, 1),
        };
    }

    export function normalizeInlineText(text) {
        return text.replace(/\s+/g, ' ');
    }
