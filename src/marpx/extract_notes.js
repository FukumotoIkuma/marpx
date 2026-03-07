() => {
            const noteDivs = document.querySelectorAll('.bespoke-marp-note');
            const notes = {};
            for (const noteDiv of noteDivs) {
                const index = parseInt(noteDiv.getAttribute('data-index'));
                if (!isNaN(index)) {
                    notes[index] = noteDiv.textContent.trim();
                }
            }
            return notes;
        }
