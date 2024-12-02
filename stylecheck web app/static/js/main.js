document.addEventListener('DOMContentLoaded', () => {
    const inputText = document.getElementById('input-text');
    const checkButton = document.getElementById('check-button');
    const outputSection = document.getElementById('output-section');
    const correctedText = document.getElementById('corrected-text');
    const correctionsList = document.getElementById('corrections-list');
    const loadingSpinner = document.createElement('div');
    loadingSpinner.className = 'loading-spinner';
    loadingSpinner.innerHTML = '<div class="spinner"></div><div class="loading-text">Analyzing text...</div>';

    function highlightOriginalText(originalPhrase, correction) {
        const escapedOriginal = correction.original.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        const regex = new RegExp(`(${escapedOriginal})`, 'gi');
        return originalPhrase.replace(regex, '<span class="highlight-error">$1</span>');
    }

    checkButton.addEventListener('click', async () => {
        const text = inputText.value.trim();
        
        if (!text) {
            alert('Please enter some text to check.');
            return;
        }

        try {
            // Show loading spinner
            checkButton.disabled = true;
            document.body.appendChild(loadingSpinner);
            outputSection.style.display = 'none';

            const response = await fetch('/check', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text }),
            });

            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Display corrected text
            correctedText.textContent = data.corrected_phrase;
            
            // Display corrections
            correctionsList.innerHTML = `
                ${data.corrections.map(correction => {
                    const highlightedText = highlightOriginalText(data.original_phrase, correction);
                    return `
                        <div class="correction-item">
                            <div class="original">Original: ${highlightedText}</div>
                            <div class="corrected">Corrected: ${correction.corrected}</div>
                            <div class="explanation">Explanation: ${correction.explanation}</div>
                        </div>
                    `;
                }).join('')}
                <div class="correction-item overall-explanation">
                    <div class="explanation">Overall: ${data.overall_explanation}</div>
                </div>
            `;

            // Show output section
            outputSection.style.display = 'grid';
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while checking the text. Please try again.');
        } finally {
            // Hide loading spinner and re-enable button
            checkButton.disabled = false;
            document.body.removeChild(loadingSpinner);
        }
    });
});
