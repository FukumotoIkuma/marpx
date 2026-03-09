/**
 * Extract background images from Marp's advanced background structure.
 * @param {Element} slideRoot - The slide root element (svg or section)
 * @param {string|null} advBg - The data-marpit-advanced-background attribute value
 * @param {Element} section - The content section element
 * @returns {Array} bgImages array
 */
export function extractBackgroundImages(slideRoot, advBg, section) {
    const bgImages = [];
    if (advBg === 'content') {
        const slideRect = slideRoot.getBoundingClientRect();
        const splitValue = window.getComputedStyle(section)
            .getPropertyValue('--marpit-advanced-background-split')
            .trim();
        const splitRatio = splitValue.endsWith('%')
            ? Math.max(0, Math.min(parseFloat(splitValue) / 100, 1))
            : null;
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
                        const figRect = fig.getBoundingClientRect();
                        bgImages.push({
                            url: urlMatch[1],
                            size: figCs.backgroundSize || 'cover',
                            position: figCs.backgroundPosition || 'center',
                            splitRatio: splitRatio,
                            box: {
                                x: figRect.left - slideRect.left,
                                y: figRect.top - slideRect.top,
                                width: figRect.width,
                                height: figRect.height,
                            },
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
    return bgImages;
}

/**
 * Extract directives (paginate, page numbers, headers, footers) from a section.
 * @param {Element} section - The slide section element
 * @returns {object} { paginate, pageNumber, pageTotal, headerText, footerText }
 */
export function extractDirectives(section) {
    const paginate = section.getAttribute('data-paginate') === 'true';
    const paginationNum = section.getAttribute('data-marpit-pagination');
    const paginationTotal = section.getAttribute('data-marpit-pagination-total');

    // Extract header/footer elements
    const headerEl = section.querySelector(':scope > header');
    const footerEl = section.querySelector(':scope > footer');

    return {
        paginate: paginate,
        pageNumber: paginationNum ? parseInt(paginationNum) : null,
        pageTotal: paginationTotal ? parseInt(paginationTotal) : null,
        headerText: headerEl ? headerEl.textContent.trim() : null,
        footerText: footerEl ? footerEl.textContent.trim() : null,
    };
}
