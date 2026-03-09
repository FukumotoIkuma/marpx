/**
 * Visual line break detection using the Range/getClientRects API.
 *
 * When CSS causes text to wrap (e.g., large headings), the DOM still reports
 * a single text string.  This module detects where visual line breaks occur
 * by walking text nodes word-by-word and checking for y-coordinate changes.
 */

const Y_THRESHOLD = 2; // px – accounts for sub-pixel rendering

/**
 * Detect visual line breaks inside an element's text content.
 *
 * @param {Element} element - The element whose text may wrap visually.
 * @returns {number[]} An array of *global* character offsets where the
 *   browser wrapped to a new line.  Empty if no wrapping occurred.
 */
export function detectVisualLineBreaks(element) {
    // Quick exit: check if the whole element spans multiple lines.
    const outerRange = document.createRange();
    outerRange.selectNodeContents(element);
    const outerRects = outerRange.getClientRects();
    if (outerRects.length <= 1) return [];

    const treeWalker = document.createTreeWalker(
        element,
        NodeFilter.SHOW_TEXT,
    );

    let globalOffset = 0;
    const breakPositions = [];
    let lastTop = null;

    while (treeWalker.nextNode()) {
        const textNode = treeWalker.currentNode;
        const text = textNode.textContent;
        if (!text || text.length === 0) continue;

        let i = 0;
        while (i < text.length) {
            // Skip leading whitespace attached to the current position
            while (i < text.length && text[i] === ' ') i++;
            if (i >= text.length) break;

            // Find end of current word
            let wordEnd = text.indexOf(' ', i);
            if (wordEnd === -1) wordEnd = text.length;

            // Measure the word's bounding rect
            const wordRange = document.createRange();
            wordRange.setStart(textNode, i);
            wordRange.setEnd(textNode, wordEnd);
            const wordRect = wordRange.getBoundingClientRect();

            if (wordRect.height > 0) {
                if (lastTop !== null && wordRect.top - lastTop > Y_THRESHOLD) {
                    // Line break detected just before this word.
                    // The break position is the global offset of the whitespace
                    // before the current word (or the start of the word itself).
                    const breakPos = globalOffset + i;
                    // Walk back to the space that caused the wrap
                    if (breakPos > 0) {
                        breakPositions.push(breakPos);
                    }
                }
                lastTop = wordRect.top;
            }

            i = wordEnd;
        }

        globalOffset += text.length;
    }

    return breakPositions;
}

/**
 * Insert `\n` into the collected runs at the detected break positions.
 *
 * Each break position is a global character offset across all runs.
 * When a break falls on a space character, that space is replaced with `\n`.
 * Otherwise `\n` is inserted at the position.
 *
 * @param {Array<{text: string}>} runs - The text runs (mutated in place).
 * @param {number[]} breakPositions - Sorted global offsets.
 */
export function insertLineBreaksIntoRuns(runs, breakPositions) {
    if (!breakPositions || breakPositions.length === 0) return;

    // Build a set for O(1) lookup and track which we've consumed.
    let bpIdx = 0;
    let cumOffset = 0;

    for (let r = 0; r < runs.length && bpIdx < breakPositions.length; r++) {
        const run = runs[r];
        // Skip non-text runs (e.g., math runs)
        if (run.runType === 'math' || !run.text) {
            continue;
        }

        const runStart = cumOffset;
        const runEnd = cumOffset + run.text.length;

        // Collect all break positions that fall within this run
        const localBreaks = [];
        while (
            bpIdx < breakPositions.length &&
            breakPositions[bpIdx] < runEnd
        ) {
            const localPos = breakPositions[bpIdx] - runStart;
            if (localPos >= 0 && localPos <= run.text.length) {
                localBreaks.push(localPos);
            }
            bpIdx++;
        }

        if (localBreaks.length > 0) {
            // Apply breaks from end to start so positions stay valid
            let newText = run.text;
            for (let i = localBreaks.length - 1; i >= 0; i--) {
                let pos = localBreaks[i];
                // If the break position lands on a space, replace it
                if (pos > 0 && newText[pos - 1] === ' ') {
                    newText =
                        newText.slice(0, pos - 1) + '\n' + newText.slice(pos);
                } else if (pos < newText.length && newText[pos] === ' ') {
                    newText =
                        newText.slice(0, pos) + '\n' + newText.slice(pos + 1);
                } else {
                    // Insert \n at the position (no space to replace)
                    newText =
                        newText.slice(0, pos) + '\n' + newText.slice(pos);
                }
            }
            run.text = newText;
        }

        cumOffset = runEnd;
    }
}
