document.addEventListener('DOMContentLoaded', function() {
    const queryInput = document.getElementById('query-input');
    const submitBtn = document.getElementById('submit-btn');
    const outputArea = document.getElementById('output-area');
    const statusIndicator = document.getElementById('status-indicator');

    // API endpoint - update this to match your backend
    const API_ENDPOINT = 'http://localhost:5000/query';

    // Event listeners
    submitBtn.addEventListener('click', handleQuery);
    queryInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleQuery();
        }
    });

    /**
     * Handle query submission
     */
    async function handleQuery() {
        const query = queryInput.value.trim();

        // Validation
        if (!query) {
            showStatus('Please enter a query', 'error');
            return;
        }

        // Disable button and show loading state
        submitBtn.disabled = true;
        showStatus('Processing your query...', 'loading');
        clearOutput();

        try {
            // Make API request
            const response = await fetch(API_ENDPOINT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query })
            });

            // Handle response
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            // Display answer
            if (data.answer) {
                displayAnswer(data.answer);
                showStatus('Query processed successfully', 'success');
            } else if (data.error) {
                displayError(data.error);
                showStatus('Error processing query', 'error');
            } else {
                displayError('No answer received from server');
                showStatus('Error processing query', 'error');
            }

        } catch (error) {
            console.error('Error:', error);
            displayError(`Error: ${error.message}<br><br>Make sure your backend is running at ${API_ENDPOINT}`);
            showStatus('Connection error', 'error');
        } finally {
            // Re-enable button
            submitBtn.disabled = false;
        }
    }

    /**
     * Display the answer in the output area
     */
    function displayAnswer(answer) {
        outputArea.innerHTML = `<p>${escapeHtml(answer)}</p>`;
        outputArea.style.opacity = '0';
        setTimeout(() => {
            outputArea.style.transition = 'opacity 0.4s ease';
            outputArea.style.opacity = '1';
        }, 10);
    }

    /**
     * Display error message
     */
    function displayError(error) {
        outputArea.innerHTML = `<p style="color: #8b4513; font-style: italic;">${error}</p>`;
        outputArea.style.opacity = '0';
        setTimeout(() => {
            outputArea.style.transition = 'opacity 0.4s ease';
            outputArea.style.opacity = '1';
        }, 10);
    }

    /**
     * Clear output area
     */
    function clearOutput() {
        outputArea.innerHTML = '';
        outputArea.style.opacity = '1';
    }

    /**
     * Show status message
     */
    function showStatus(message, type) {
        statusIndicator.textContent = message;
        statusIndicator.className = 'status-indicator active';

        if (type === 'loading') {
            statusIndicator.classList.add('loading');
        } else if (type === 'error') {
            statusIndicator.style.color = '#8b4513';
        } else if (type === 'success') {
            statusIndicator.style.color = '#6b8e23';
        }

        // Auto-hide success messages
        if (type === 'success') {
            setTimeout(() => {
                statusIndicator.classList.remove('active');
            }, 3000);
        }
    }

    /**
     * Escape HTML special characters to prevent XSS
     */
    function escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }
});