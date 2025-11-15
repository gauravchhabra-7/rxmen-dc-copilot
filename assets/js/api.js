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

    // ==================== DATA TRANSFORMATION ====================

    /**
     * Transform frontend form data to match backend API schema
     * Handles field name mapping, type conversion, and data cleanup
     * @param {Object} formData - Raw form data from frontend
     * @returns {Object} Transformed data matching backend schema
     */
    function transformFormDataForBackend(formData) {
        const transformed = {};

        // Field name mappings (frontend → backend)
        const fieldMappings = {
            'weight_kg': 'weight',
            'height_feet': 'height_ft',
            'height_inches': 'height_in',
            'alcohol_frequency': 'alcohol_consumption',
            'smoking_frequency': 'smoking_status',
            'additional_information': 'additional_info',
            'pe_partner_ejaculation_time': 'pe_partner_time_to_ejaculation'
        };

        // Fields to convert to integers
        const intFields = ['age', 'height_ft', 'height_in'];

        // Fields to convert to floats
        const floatFields = ['weight', 'height_cm'];

        // Fields to ensure are arrays
        const arrayFields = ['medical_conditions', 'current_medications', 'previous_treatments'];

        // Fields to exclude (not in backend schema)
        const excludeFields = [
            'full_name', 'city', 'occupation', 'issue_context', 'issue_duration',
            'pe_partner_type', 'pe_partner_ejaculation_time', 'pe_partner_penile_sensitivity',
            'medical_conditions_other', 'current_medications_other'
        ];

        // Process each field
        for (let [key, value] of Object.entries(formData)) {
            // Skip excluded fields
            if (excludeFields.includes(key)) {
                continue;
            }

            // Map field name if needed
            const mappedKey = fieldMappings[key] || key;

            // SPECIAL HANDLING: Array fields must always be arrays (even for single values)
            if (arrayFields.includes(mappedKey)) {
                // Convert to array if not already
                if (Array.isArray(value)) {
                    transformed[mappedKey] = value;
                } else if (value === '' || value === null || value === undefined) {
                    transformed[mappedKey] = [];
                } else {
                    // Single value -> wrap in array
                    transformed[mappedKey] = [value];
                }
                continue;
            }

            // Handle empty values for non-array fields
            if (value === '' || value === null || value === undefined) {
                // For optional fields, set to null
                transformed[mappedKey] = null;
                continue;
            }

            // Convert to appropriate type
            if (intFields.includes(mappedKey)) {
                transformed[mappedKey] = parseInt(value, 10);
            } else if (floatFields.includes(mappedKey)) {
                transformed[mappedKey] = parseFloat(value);
            } else {
                transformed[mappedKey] = value;
            }
        }

        // Add metadata
        transformed.form_version = '2.2';
        transformed.submitted_at = new Date().toISOString();

        return transformed;
    }

    // ==================== API CLIENT ====================

    /**
     * Call backend /analyze endpoint
     * @param {Object} formData - Patient form data
     * @returns {Promise<Object>} Analysis result
     */
    async function analyzePatientCase(formData) {
        const url = `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.ANALYZE}`;

        console.log('📡 Calling backend API:', url);
        console.log('📦 Raw form data:', formData);

        // Transform data to match backend schema
        const transformedData = transformFormDataForBackend(formData);
        console.log('✨ Transformed payload:', transformedData);

        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.TIMEOUT);

            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(transformedData),
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            console.log('=� Response status:', response.status);

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
                            <span class="step-icon">>�</span>
                            <span class="step-text">AI analysis in progress...</span>
                        </div>
                        <div class="loading-step" id="step-3">
                            <span class="step-icon">=�</span>
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
     * Display diagnosis result - Clean format for agent-optimized output
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

        // Extract data from backend response
        const primaryCause = result.root_causes?.[0];
        const secondaryCause = result.root_causes?.[1];

        // Format root causes: Simple term [Medical Term]
        // Use AI-generated simple_term from backend, fallback to category if not available
        const formatRootCause = (cause) => {
            if (!cause) return 'Unknown';

            const medicalTerm = cause.category || 'Unknown';
            const simpleTerm = cause.simple_term || medicalTerm;

            return `${simpleTerm} [${medicalTerm}]`;
        };

        const primaryDisplay = formatRootCause(primaryCause);
        const secondaryDisplay = formatRootCause(secondaryCause);

        // Agent script: Combine both explanations
        const agentScript = [
            primaryCause?.explanation || '',
            secondaryCause?.explanation || ''
        ].filter(Boolean).join('\n\n');

        // Treatment plan: Use detailed_analysis which contains personalized treatment explanation
        const treatmentPlan = result.detailed_analysis || result.summary || '';

        // Clean display format - no emojis, no badges, no confidence scores
        const html = `
            <div class="clean-diagnosis-result">
                <div class="cause-section">
                    <h4 class="cause-label">PRIMARY ROOT CAUSE</h4>
                    <p class="medical-term">${escapeHtml(primaryDisplay)}</p>
                </div>

                <div class="cause-section">
                    <h4 class="cause-label">SECONDARY ROOT CAUSE</h4>
                    <p class="medical-term">${escapeHtml(secondaryDisplay)}</p>
                </div>

                <div class="divider">═══════════════════════════════════</div>

                <div class="script-section">
                    <h4 class="section-label">AGENT SCRIPT</h4>
                    <p class="script-text">${escapeHtml(agentScript)}</p>
                </div>

                <div class="divider">═══════════════════════════════════</div>

                <div class="treatment-section">
                    <h4 class="section-label">TREATMENT PLAN</h4>
                    <p class="treatment-text">${escapeHtml(treatmentPlan)}</p>
                </div>
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
                    <span class="red-flag-icon">�</span>
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
