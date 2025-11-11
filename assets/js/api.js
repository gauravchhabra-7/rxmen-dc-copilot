/*
 * RxMen Discovery Call Form - Backend API Integration
 * Handles communication with the backend analyze endpoint
 */

(function() {
    'use strict';

    // ==================== CONFIGURATION ====================

    const API_CONFIG = {
        BASE_URL: 'http://localhost:8000',
        ENDPOINTS: {
            HEALTH: '/api/v1/health',
            ANALYZE: '/api/v1/analyze'
        },
        TIMEOUT: 60000, // 60 seconds
        LANGUAGE: 'hinglish' // default language
    };

    // ==================== API CLIENT ====================

    /**
     * Call backend /analyze endpoint
     * @param {Object} formData - Patient form data
     * @returns {Promise<Object>} Analysis result
     */
    async function analyzePatientCase(formData) {
        const url = `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.ANALYZE}`;

        console.log('=á Calling backend API:', url);
        console.log('=ä Request payload:', formData);

        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.TIMEOUT);

            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(formData),
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            console.log('=å Response status:', response.status);

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new APIError(
                    `API request failed: ${response.status}`,
                    response.status,
                    errorData
                );
            }

            const result = await response.json();
            console.log(' Analysis result:', result);

            return result;

        } catch (error) {
            console.error('L API call failed:', error);

            if (error.name === 'AbortError') {
                throw new APIError('Request timeout - please try again', 408);
            }

            if (error instanceof APIError) {
                throw error;
            }

            if (!navigator.onLine) {
                throw new APIError('No internet connection. Please check your network.', 0);
            }

            throw new APIError(`Failed to connect to backend: ${error.message}`, 0, error);
        }
    }

    /**
     * Check backend health status
     * @returns {Promise<Object>} Health status
     */
    async function checkHealth() {
        const url = `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.HEALTH}`;

        try {
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`Health check failed: ${response.status}`);
            }

            return await response.json();

        } catch (error) {
            console.error('Health check failed:', error);
            throw error;
        }
    }

    // ==================== ERROR HANDLING ====================

    /**
     * Custom API Error class
     */
    class APIError extends Error {
        constructor(message, statusCode, details = null) {
            super(message);
            this.name = 'APIError';
            this.statusCode = statusCode;
            this.details = details;
        }
    }

    /**
     * Get user-friendly error message
     * @param {Error} error - Error object
     * @returns {string} User-friendly message
     */
    function getErrorMessage(error) {
        if (!(error instanceof APIError)) {
            return `Unexpected error: ${error.message}`;
        }

        switch (error.statusCode) {
            case 0:
                return 'Cannot connect to backend server. Please ensure the server is running.';
            case 400:
                return 'Invalid form data. Please check all fields and try again.';
            case 408:
                return 'Request timeout. The server is taking too long to respond. Please try again.';
            case 422:
                return 'Invalid form data. ' + (error.details?.detail || 'Please check all required fields.');
            case 500:
                return 'Server error. Please try again in a moment.';
            case 503:
                return 'Backend service unavailable. Please try again later.';
            default:
                return error.message || 'Analysis failed. Please try again.';
        }
    }

    // ==================== UI HELPERS ====================

    /**
     * Show loading state in output panel
     */
    function showLoadingState() {
        const outputPanel = document.getElementById('output-content');
        const outputStatus = document.getElementById('output-status');
        const submitBtn = document.getElementById('submit-btn');

        if (outputStatus) {
            outputStatus.textContent = 'Analyzing...';
            outputStatus.className = 'output-status loading';
        }

        if (outputPanel) {
            outputPanel.innerHTML = `
                <div class="loading-state">
                    <div class="spinner"></div>
                    <p class="loading-text">Analyzing patient data...</p>
                    <p class="loading-subtext">This may take 2-5 seconds</p>
                    <div class="loading-steps">
                        <div class="loading-step" id="step-1">
                            <span class="step-icon">=</span>
                            <span class="step-text">Retrieving medical knowledge...</span>
                        </div>
                        <div class="loading-step" id="step-2">
                            <span class="step-icon">>à</span>
                            <span class="step-text">AI analysis in progress...</span>
                        </div>
                        <div class="loading-step" id="step-3">
                            <span class="step-icon">=Ë</span>
                            <span class="step-text">Generating diagnosis...</span>
                        </div>
                    </div>
                </div>
            `;

            // Animate loading steps
            setTimeout(() => document.getElementById('step-1')?.classList.add('active'), 500);
            setTimeout(() => document.getElementById('step-2')?.classList.add('active'), 1500);
            setTimeout(() => document.getElementById('step-3')?.classList.add('active'), 2500);
        }

        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Analyzing...';
            submitBtn.classList.add('loading');
        }

        // Scroll to output panel
        outputPanel?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    /**
     * Hide loading state
     */
    function hideLoadingState() {
        const submitBtn = document.getElementById('submit-btn');

        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Submit Form';
            submitBtn.classList.remove('loading');
        }
    }

    /**
     * Display diagnosis result
     * @param {Object} result - Analysis result from backend
     */
    function displayDiagnosis(result) {
        const outputPanel = document.getElementById('output-content');
        const outputStatus = document.getElementById('output-status');
        const outputActions = document.getElementById('output-actions');

        if (outputStatus) {
            outputStatus.textContent = 'Analysis Complete';
            outputStatus.className = 'output-status success';
        }

        // Check for red flags first
        if (result.red_flags && result.red_flags.length > 0) {
            displayRedFlagAlert(result.red_flags[0], outputPanel);
            return;
        }

        // Display normal diagnosis
        const html = `
            <div class="diagnosis-result">
                <div class="diagnosis-header">
                    <h3 class="diagnosis-title"> Diagnosis Complete</h3>
                    <div class="diagnosis-meta">
                        <span class="meta-item">
                            <span class="meta-icon">ñ</span>
                            ${(result.processing_time_ms / 1000).toFixed(2)}s
                        </span>
                        <span class="meta-item">
                            <span class="meta-icon">=Ú</span>
                            ${result.retrieval_chunks_used || 0} knowledge chunks
                        </span>
                    </div>
                </div>

                <div class="root-causes">
                    <!-- Primary Root Cause -->
                    <div class="root-cause primary">
                        <div class="root-cause-header">
                            <h4 class="root-cause-title">
                                <span class="badge badge-primary">PRIMARY</span>
                                Root Cause #1
                            </h4>
                            <span class="confidence-badge high">
                                ${Math.round((result.primary_root_cause.confidence_score || 0) * 100)}% Confidence
                            </span>
                        </div>
                        <p class="medical-term">${escapeHtml(result.primary_root_cause.medical_term)}</p>
                        <p class="simple-explanation">${escapeHtml(result.primary_root_cause.simple_explanation)}</p>
                        ${result.primary_root_cause.analogy ? `
                            <div class="analogy-box">
                                <span class="analogy-icon">=¡</span>
                                <p class="analogy-text">${escapeHtml(result.primary_root_cause.analogy)}</p>
                            </div>
                        ` : ''}
                    </div>

                    <!-- Secondary Root Cause -->
                    <div class="root-cause secondary">
                        <div class="root-cause-header">
                            <h4 class="root-cause-title">
                                <span class="badge badge-secondary">SECONDARY</span>
                                Root Cause #2
                            </h4>
                            <span class="confidence-badge medium">
                                ${Math.round((result.secondary_root_cause.confidence_score || 0) * 100)}% Confidence
                            </span>
                        </div>
                        <p class="medical-term">${escapeHtml(result.secondary_root_cause.medical_term)}</p>
                        <p class="simple-explanation">${escapeHtml(result.secondary_root_cause.simple_explanation)}</p>
                        ${result.secondary_root_cause.analogy ? `
                            <div class="analogy-box">
                                <span class="analogy-icon">=¡</span>
                                <p class="analogy-text">${escapeHtml(result.secondary_root_cause.analogy)}</p>
                            </div>
                        ` : ''}
                    </div>
                </div>

                <!-- Treatment Recommendation -->
                <div class="treatment-section">
                    <h4 class="treatment-title">
                        <span class="treatment-icon">=Š</span>
                        Treatment Recommendation
                    </h4>
                    <p class="treatment-text">${escapeHtml(result.treatment_recommendation)}</p>
                </div>

                <!-- Additional Info -->
                ${result.model_used || result.language ? `
                    <div class="diagnosis-footer">
                        ${result.language ? `<span class="footer-item">Language: ${result.language}</span>` : ''}
                        ${result.model_used ? `<span class="footer-item">Model: ${result.model_used}</span>` : ''}
                    </div>
                ` : ''}
            </div>
        `;

        if (outputPanel) {
            outputPanel.innerHTML = html;
        }

        // Show action buttons
        if (outputActions) {
            outputActions.classList.remove('hidden');
        }

        // Scroll to result
        outputPanel?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    /**
     * Display red flag alert
     * @param {Object} redFlag - Red flag object
     * @param {HTMLElement} container - Container element
     */
    function displayRedFlagAlert(redFlag, container) {
        const html = `
            <div class="red-flag-alert">
                <div class="red-flag-header">
                    <span class="red-flag-icon"> </span>
                    <h3 class="red-flag-title">Red Flag Detected</h3>
                </div>
                <div class="red-flag-content">
                    <p class="red-flag-message">${escapeHtml(redFlag.message)}</p>
                    <div class="red-flag-action">
                        <strong>Required Action:</strong>
                        <p>${escapeHtml(redFlag.action)}</p>
                    </div>
                    ${redFlag.severity ? `
                        <div class="red-flag-severity">
                            <strong>Severity:</strong> <span class="severity-badge ${redFlag.severity.toLowerCase()}">${redFlag.severity}</span>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;

        if (container) {
            container.innerHTML = html;
        }
    }

    /**
     * Display error message
     * @param {string} message - Error message
     */
    function displayError(message) {
        const outputPanel = document.getElementById('output-content');
        const outputStatus = document.getElementById('output-status');

        if (outputStatus) {
            outputStatus.textContent = 'Analysis Failed';
            outputStatus.className = 'output-status error';
        }

        if (outputPanel) {
            outputPanel.innerHTML = `
                <div class="error-state">
                    <div class="error-icon">L</div>
                    <h3 class="error-title">Analysis Failed</h3>
                    <p class="error-message">${escapeHtml(message)}</p>
                    <button type="button" class="btn-retry" onclick="document.getElementById('submit-btn').click()">
                        = Retry Analysis
                    </button>
                    <div class="error-help">
                        <p class="error-help-title">Troubleshooting:</p>
                        <ul class="error-help-list">
                            <li>Ensure the backend server is running at <code>http://localhost:8000</code></li>
                            <li>Check your internet connection</li>
                            <li>Verify all required form fields are filled</li>
                            <li>Try refreshing the page and submitting again</li>
                        </ul>
                    </div>
                </div>
            `;
        }
    }

    /**
     * Escape HTML to prevent XSS
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text || '';
        return div.innerHTML;
    }

    // ==================== PUBLIC API ====================

    window.api = {
        analyzePatientCase,
        checkHealth,
        showLoadingState,
        hideLoadingState,
        displayDiagnosis,
        displayError,
        getErrorMessage,
        APIError,
        API_CONFIG
    };

    console.log(' API module loaded');

})();
