import { extractBackgroundImages, extractDirectives } from './backgrounds.js';
import { processElement } from './handlers.js';
import { createRenderContext } from './render-context.js';

export function extractSlides() {
    const sections = document.querySelectorAll('section[id]');
    let slideSections;
    if (sections.length === 0) {
        // Try without id filter
        const allSections = document.querySelectorAll('section');
        // Filter to direct slide sections (not nested)
        slideSections = Array.from(allSections).filter(s => {
            return s.parentElement && (
                s.parentElement.tagName === 'BODY' ||
                s.parentElement.classList.contains('marpit') ||
                s.parentElement.tagName === 'DIV'
            );
        });
        if (slideSections.length === 0) slideSections = Array.from(allSections);
    } else {
        slideSections = Array.from(sections);
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
        const bgImages = extractBackgroundImages(slideRoot, advBg, section);

        // Extract directives
        const directives = extractDirectives(section);

        const slideData = {
            width: slideRect.width,
            height: slideRect.height,
            slideNumber: slideIndex++,
            background: {
                color: cs.backgroundColor,
                backgroundGradient: cs.backgroundImage && cs.backgroundImage.includes('linear-gradient(')
                    ? cs.backgroundImage
                    : null,
                images: bgImages,
            },
            directives: directives,
            elements: [],
        };

        // Process direct children and nested content
        const rootContext = createRenderContext();
        for (const child of section.children) {
            processElement(child, slideRect, slideData, rootContext);
        }

        slides.push(slideData);
    }

    return slides;
}
