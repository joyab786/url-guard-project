const urlForm = document.getElementById('url-form');
const urlInput = document.getElementById('url-input');
const resultContainer = document.getElementById('result-container');
const resultCard = document.getElementById('result-card');
const resultStatus = document.getElementById('result-status');
const riskScore = document.getElementById('risk-score');
const checkButton = document.getElementById('check-button');

urlForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const url = urlInput.value;

    // Show loading state
    checkButton.textContent = 'Checking...';
    checkButton.disabled = true;
    resultContainer.classList.add('hidden');

    try {
        // NOTE: Make sure your FastAPI server is running at http://127.0.0.1:8000
        const response = await fetch('http://127.0.0.1:8000/analyze-url/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url }),
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();

        // Update UI with the result
        resultStatus.textContent = data.status;
        riskScore.textContent = data.risk_score;
        
        // Apply color-coded class
        resultCard.className = ''; // Reset classes
        resultCard.classList.add(data.verdict_class);
        
        resultContainer.classList.remove('hidden');

    } catch (error) {
        console.error('Error:', error);
        resultStatus.textContent = 'Error: Could not analyze URL';
        riskScore.textContent = 'N/A';
        resultCard.className = 'dangerous'; // Show error as dangerous
        resultContainer.classList.remove('hidden');
    } finally {
        // Reset button state
        checkButton.textContent = 'Check URL';
        checkButton.disabled = false;
    }
});