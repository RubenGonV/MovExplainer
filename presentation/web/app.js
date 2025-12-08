// ===================================
// Global State
// ===================================
let board = null;
const API_BASE_URL = window.location.origin;

// ===================================
// Initialize Application
// ===================================
document.addEventListener('DOMContentLoaded', function () {
    initializeBoard();
    setupFormHandler();
    setupFenInputHandler();
});

// ===================================
// Chess Board Initialization
// ===================================
function initializeBoard() {
    const config = {
        draggable: false,
        position: 'start',
        pieceTheme: 'https://chessboardjs.com/img/chesspieces/wikipedia/{piece}.png'
    };

    board = Chessboard('board', config);

    // Make board responsive
    $(window).resize(board.resize);
}

// ===================================
// FEN Input Handler
// ===================================
function setupFenInputHandler() {
    const fenInput = document.getElementById('fen');

    fenInput.addEventListener('input', debounce(function (e) {
        const fen = e.target.value.trim();
        if (fen) {
            try {
                board.position(fen);
            } catch (error) {
                console.log('Invalid FEN, waiting for valid input...');
            }
        }
    }, 500));
}

// ===================================
// Form Submission Handler
// ===================================
function setupFormHandler() {
    const form = document.getElementById('analysisForm');

    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        // Get form values
        const fen = document.getElementById('fen').value.trim();
        const movesInput = document.getElementById('moves').value.trim();
        const targetAudience = document.getElementById('targetAudience').value;

        // Parse moves (comma-separated)
        const moves = movesInput
            ? movesInput.split(',').map(m => m.trim()).filter(m => m)
            : [];

        // Prepare request data
        const requestData = {
            fen: fen,
            moves: moves,
            target_audience: targetAudience
        };

        // Submit analysis
        await submitAnalysis(requestData);
    });
}

// ===================================
// API Request Handler
// ===================================
async function submitAnalysis(data) {
    const analyzeBtn = document.getElementById('analyzeBtn');
    const btnText = analyzeBtn.querySelector('.btn-text');
    const btnLoader = analyzeBtn.querySelector('.btn-loader');
    const resultsContainer = document.getElementById('resultsContainer');

    try {
        // Show loading state
        analyzeBtn.disabled = true;
        btnText.style.display = 'none';
        btnLoader.style.display = 'flex';

        // Make API request
        const response = await fetch(`${API_BASE_URL}/explain`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();

        // Display results
        displayResults(result);

    } catch (error) {
        console.error('Error:', error);
        displayError(error.message);
    } finally {
        // Reset button state
        analyzeBtn.disabled = false;
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
    }
}

// ===================================
// Display Results
// ===================================
function displayResults(result) {
    const resultsContainer = document.getElementById('resultsContainer');

    const isSuccess = result.success;
    const statusClass = isSuccess ? 'success' : 'error';

    let html = `
        <div class="result-card ${statusClass}">
            <div class="result-header">
                <span class="status-badge ${statusClass}">
                    ${isSuccess ? '✓ Success' : '✗ Error'}
                </span>
            </div>
            
            <div class="result-content">
    `;

    if (isSuccess) {
        // Display explanation
        if (result.explanation) {
            html += `
                <h3>Explanation</h3>
                <p>${escapeHtml(result.explanation)}</p>
            `;
        }

        // Display metadata
        if (result.best_move || result.score !== null) {
            html += `
                <div class="result-meta">
            `;

            if (result.best_move) {
                html += `
                    <div class="meta-item">
                        <span class="meta-label">Best Move</span>
                        <span class="meta-value">${escapeHtml(result.best_move)}</span>
                    </div>
                `;
            }

            if (result.score !== null && result.score !== undefined) {
                const scoreDisplay = formatScore(result.score);
                html += `
                    <div class="meta-item">
                        <span class="meta-label">Evaluation</span>
                        <span class="meta-value">${scoreDisplay}</span>
                    </div>
                `;
            }

            html += `</div>`;
        }
    } else {
        // Display error
        html += `
            <h3>Error</h3>
            <p style="color: var(--error);">${escapeHtml(result.error || 'Unknown error occurred')}</p>
        `;
    }

    html += `
            </div>
        </div>
        
        <details class="json-display">
            <summary style="cursor: pointer; color: var(--text-secondary); margin-bottom: 1rem;">
                View Raw JSON Response
            </summary>
            <pre>${JSON.stringify(result, null, 2)}</pre>
        </details>
    `;

    resultsContainer.innerHTML = html;
}

// ===================================
// Display Error
// ===================================
function displayError(message) {
    const resultsContainer = document.getElementById('resultsContainer');

    resultsContainer.innerHTML = `
        <div class="result-card error">
            <div class="result-header">
                <span class="status-badge error">✗ Request Failed</span>
            </div>
            <div class="result-content">
                <h3>Error</h3>
                <p style="color: var(--error);">${escapeHtml(message)}</p>
            </div>
        </div>
    `;
}

// ===================================
// Utility Functions
// ===================================

// Debounce function to limit API calls
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Escape HTML to prevent XSS
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

// Format chess engine score
function formatScore(score) {
    if (score === null || score === undefined) return 'N/A';

    // Score is in centipawns
    const pawns = (score / 100).toFixed(2);

    if (score > 0) {
        return `+${pawns}`;
    } else if (score < 0) {
        return pawns;
    } else {
        return '0.00';
    }
}
