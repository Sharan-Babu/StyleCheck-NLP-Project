async function checkGrammar() {
    const inputText = document.getElementById('inputText').value.trim();
    const checkButton = document.getElementById('checkButton');
    const resultsSection = document.getElementById('results');
    
    if (!inputText) {
        alert('Please enter some text to check.');
        return;
    }

    try {
        // Show loading state
        checkButton.disabled = true;
        checkButton.classList.add('loading');
        resultsSection.style.display = 'none';

        const response = await fetch('/check', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: inputText })
        });

        if (!response.ok) {
            throw new Error('Server error');
        }

        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }

        displayResults(data, inputText);
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while checking the text. Please try again.');
    } finally {
        // Hide loading state
        checkButton.disabled = false;
        checkButton.classList.remove('loading');
    }
}

function displayResults(data, inputText) {
    const resultsSection = document.getElementById('results');
    const correctedTextDiv = document.getElementById('correctedText');
    const correctionsDiv = document.getElementById('corrections');

    // Display corrected text
    correctedTextDiv.textContent = data.corrected_phrase;

    // Display corrections
    correctionsDiv.innerHTML = data.corrections.map(correction => {
        // Create a copy of the input text and wrap the original error in a span
        const highlightedText = inputText.replace(
            correction.original,
            `<span class="highlight-error">${correction.original}</span>`
        );
        
        return `
        <div class="correction-item">
            <div class="correction-header">
                <div class="correction-number">${correction.id}</div>
                <strong>Correction ${correction.id}</strong>
            </div>
            <div>
                <div><strong>Original:</strong> <span class="original">${highlightedText}</span></div>
                <div><strong>Corrected:</strong> <span class="corrected">${correction.corrected}</span></div>
                <div class="explanation"><strong>Explanation:</strong> ${correction.explanation}</div>
            </div>
        </div>
    `}).join('');

    // Add overall explanation if available
    if (data.overall_explanation) {
        correctionsDiv.innerHTML += `
        <div class="correction-item overall-explanation">
            <div class="correction-header">
                <strong>Overall Analysis</strong>
            </div>
            <div class="explanation">${data.overall_explanation}</div>
        </div>
        `;
    }

    // Show results section
    resultsSection.style.display = 'block';
}
