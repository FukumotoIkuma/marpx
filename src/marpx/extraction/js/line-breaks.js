/**
 * Visual line break detection using the Range/getClientRects API.
 *
 * When CSS causes text to wrap (e.g., large headings), the DOM still reports
 * a single text string.  This module detects where visual line breaks occur
 * by walking text nodes word-by-word and checking for y-coordinate changes.
 *
 * Returns the text content of each visual line so that callers can insert
 * line breaks in normalized (whitespace-collapsed) run text without offset
 * mismatch issues.
 */

const Y_THRESHOLD = 2; // px – accounts for sub-pixel rendering

/**
 * Detect visual line breaks inside an element's text content.
 *
 * Returns the text content of each visual line as an array of strings.
 * The text for each line is obtained by reading the Range contents,
 * so it reflects the raw DOM text (callers must normalize afterwards).
 *
 * @param {Element} element - The element whose text may wrap visually.
 * @returns {string[]} An array of line texts.  Empty array if no wrapping
 *   occurred (single line or empty).
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

    // Collect all words with their y-coordinates
    const words = []; // { text: string, top: number }
    let lastTop = null;

    while (treeWalker.nextNode()) {
        const textNode = treeWalker.currentNode;
        const text = textNode.textContent;
        if (!text || text.length === 0) continue;

        let i = 0;
        while (i < text.length) {
            // Skip leading whitespace
            const wsMatch = text.substring(i).match(/^\s+/);
            if (wsMatch) {
                // Include whitespace as part of the word sequence
                // (it will be normalized later)
                i += wsMatch[0].length;
            }
            if (i >= text.length) break;

            // Find end of current word (use regex for Unicode whitespace)
            const remaining = text.substring(i);
            const wbMatch = remaining.match(/\s/);
            let wordEnd = wbMatch ? i + wbMatch.index : text.length;

            // Measure the word's bounding rect
            const wordRange = document.createRange();
            wordRange.setStart(textNode, i);
            wordRange.setEnd(textNode, wordEnd);
            const wordRect = wordRange.getBoundingClientRect();

            if (wordRect.height > 0) {
                const wordText = text.substring(i, wordEnd);
                const isNewLine =
                    lastTop !== null &&
                    wordRect.top - lastTop > Y_THRESHOLD;
                words.push({ text: wordText, newLine: isNewLine });
                lastTop = wordRect.top;
            }

            i = wordEnd;
        }
    }

    if (words.length === 0) return [];

    // Check if any wrapping actually occurred
    const hasWrapping = words.some((w) => w.newLine);
    if (!hasWrapping) return [];

    // Build line texts
    const lines = [];
    let currentLine = '';
    for (const word of words) {
        if (word.newLine && currentLine.length > 0) {
            lines.push(currentLine);
            currentLine = word.text;
        } else {
            if (currentLine.length > 0) {
                currentLine += ' ' + word.text;
            } else {
                currentLine = word.text;
            }
        }
    }
    if (currentLine.length > 0) {
        lines.push(currentLine);
    }

    return lines.length > 1 ? lines : [];
}

/**
 * Insert `\n` into the collected runs at visual line boundaries.
 *
 * Uses the line texts returned by `detectVisualLineBreaks` to find where
 * to insert `\n` in the normalized run text.  This avoids the raw-DOM vs
 * normalized-text offset mismatch.
 *
 * @param {Array<{text: string}>} runs - The text runs (mutated in place).
 * @param {string[]} lineTexts - Array of visual line texts from
 *   `detectVisualLineBreaks`.
 */
export function insertLineBreaksIntoRuns(runs, lineTexts) {
    if (!lineTexts || lineTexts.length <= 1) return;

    // Concatenate all run texts (skipping math runs) to get full normalized text
    const textRuns = [];
    for (let i = 0; i < runs.length; i++) {
        if (runs[i].runType === 'math' || !runs[i].text) continue;
        textRuns.push({ index: i, run: runs[i] });
    }

    if (textRuns.length === 0) return;

    const fullText = textRuns.map((tr) => tr.run.text).join('');

    // Normalize the line texts (collapse whitespace) and join with \n
    const normalizedLines = lineTexts.map((l) => l.replace(/\s+/g, ' ').trim());
    const joinedLines = normalizedLines.join('\n');

    // Now we need to match the joined lines against fullText.
    // The fullText may have spaces where line breaks should be inserted.
    // Strategy: walk through fullText and joinedLines simultaneously.
    // Build a new full text with \n inserted at the right positions.
    let newFullText = '';
    let fi = 0; // index into fullText
    let ji = 0; // index into joinedLines

    while (fi < fullText.length && ji < joinedLines.length) {
        if (joinedLines[ji] === '\n') {
            // Line break in joined lines – skip any space in fullText
            if (fi > 0 && fullText[fi] === ' ') {
                fi++; // consume the space that becomes a line break
            }
            newFullText += '\n';
            ji++;
        } else if (fullText[fi] === joinedLines[ji]) {
            newFullText += fullText[fi];
            fi++;
            ji++;
        } else if (fullText[fi] === ' ' && joinedLines[ji] !== ' ') {
            // Extra space in fullText not in joinedLines – might be at a
            // boundary; keep it
            newFullText += fullText[fi];
            fi++;
        } else {
            // Mismatch – just keep the original character
            newFullText += fullText[fi];
            fi++;
            ji++;
        }
    }
    // Append any remaining text from fullText
    while (fi < fullText.length) {
        newFullText += fullText[fi];
        fi++;
    }

    // If nothing changed, bail out
    if (newFullText === fullText) return;

    // Distribute newFullText back into the runs, preserving run boundaries
    let pos = 0;
    for (const tr of textRuns) {
        const runLen = tr.run.text.length;
        // Count how many chars from newFullText correspond to this run.
        // We need to figure out the new length: the original run length plus
        // any \n inserted minus any spaces consumed.
        // Simpler: walk newFullText consuming characters that match the
        // original run text.
        let newRunText = '';
        let origConsumed = 0;
        while (origConsumed < runLen && pos < newFullText.length) {
            const ch = newFullText[pos];
            if (ch === '\n') {
                // Check if this \n replaces a space in the original
                if (
                    origConsumed < runLen &&
                    tr.run.text[origConsumed] === ' '
                ) {
                    // Replace the space with \n
                    newRunText += '\n';
                    origConsumed++;
                    pos++;
                } else if (origConsumed < runLen) {
                    // Insert \n without consuming original chars
                    newRunText += '\n';
                    pos++;
                } else {
                    break;
                }
            } else {
                newRunText += ch;
                origConsumed++;
                pos++;
            }
        }
        tr.run.text = newRunText;
    }
}
