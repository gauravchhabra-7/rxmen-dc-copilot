/* ===================================
   RxMen Discovery Call Copilot - Main JS
   Handles form submission and results display
   =================================== */

// Configuration
const API_BASE_URL = 'http://localhost:8000/api/v1';
const ANALYZE_ENDPOINT = `${API_BASE_URL}/analyze`;

// DOM Elements
const form = document.getElementById('discoveryForm');
const analyzeBtn = document.getElementById('analyzeBtn');
const loadingState = document.getElementById('loadingState');
const emptyState = document.getElementById('emptyState');
const resultsDisplay = document.getElementById('resultsDisplay');
const errorState = document.getElementById('errorState');
const errorMessage = document.getElementById('errorMessage');

// Result elements
const primaryCause = document.getElementById('primaryCause');
const secondaryCause = document.getElementById('secondaryCause');
const agentScript = document.getElementById('agentScript');
const treatmentPlan = document.getElementById('treatmentPlan');

// Action buttons
const copyBtn = document.getElementById('copyBtn');
const resetBtn = document.getElementById('resetBtn');
const retryBtn = document.getElementById('retryBtn');

// Conditional sections
const peSection = document.getElementById('peSection');
const edSection = document.getElementById('edSection');
const mainIssueInputs = document.querySelectorAll('input[name="main_issue"]');

// === CONDITIONAL LOGIC ===
// Show/hide PE and ED sections based on main issue
mainIssueInputs.forEach(input => {
    input.addEventListener('change', (e) => {
        const value = e.target.value;

        if (value === 'pe' || value === 'both') {
            peSection.style.display = 'block';
            // Make PE fields required
            peSection.querySelectorAll('select').forEach(select => {
                select.required = true;
            });
        } else {
            peSection.style.display = 'none';
            peSection.querySelectorAll('select').forEach(select => {
                select.required = false;
            });
        }

        if (value === 'ed' || value === 'both') {
            edSection.style.display = 'block';
            // Make ED fields required
            edSection.querySelectorAll('select').forEach(select => {
                select.required = true;
            });
        } else {
            edSection.style.display = 'none';
            edSection.querySelectorAll('select').forEach(select => {
                select.required = false;
            });
        }
    });
});

// === FORM SUBMISSION ===
form.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Get form data
    const formData = getFormData();

    // Validate
    if (!validateFormData(formData)) {
        showError('Please fill in all required fields');
        return;
    }

    // Show loading state
    showLoading();

    try {
        // Call API
        const response = await fetch(ANALYZE_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const result = await response.json();

        // Display results
        displayResults(result);

    } catch (error) {
        console.error('Analysis error:', error);
        showError(error.message || 'Failed to analyze. Please check if the backend server is running.');
    }
});

// === GET FORM DATA ===
function getFormData() {
    const formData = new FormData(form);
    const data = {};

    // Convert FormData to object
    for (const [key, value] of formData.entries()) {
        // Handle checkboxes (medical_conditions)
        if (key === 'medical_conditions') {
            if (!data[key]) {
                data[key] = [];
            }
            data[key].push(value);
        } else {
            data[key] = value;
        }
    }

    // Convert numeric fields
    if (data.age) data.age = parseInt(data.age);
    if (data.height_cm) data.height_cm = parseFloat(data.height_cm);
    if (data.weight) data.weight = parseFloat(data.weight);

    // Ensure medical_conditions is an array
    if (!data.medical_conditions) {
        data.medical_conditions = ['none'];
    }

    return data;
}

// === VALIDATE FORM DATA ===
function validateFormData(data) {
    // Check required fields
    const required = ['age', 'height_cm', 'weight', 'main_issue', 'emergency_red_flags'];

    for (const field of required) {
        if (!data[field]) {
            return false;
        }
    }

    return true;
}

// === DISPLAY RESULTS ===
function displayResults(result) {
    console.log('Analysis result:', result);

    // Hide loading and error states
    loadingState.style.display = 'none';
    errorState.style.display = 'none';
    emptyState.style.display = 'none';

    // Extract data
    const rootCauses = result.root_causes || [];
    const detailed = result.detailed_analysis || '';

    // PRIMARY ROOT CAUSE
    if (rootCauses.length > 0) {
        const primary = rootCauses[0];
        primaryCause.textContent = primary.category || primary.medical_term || 'Unknown';
    } else {
        primaryCause.textContent = result.primary_diagnosis || 'Unknown';
    }

    // SECONDARY ROOT CAUSE
    if (rootCauses.length > 1) {
        const secondary = rootCauses[1];
        secondaryCause.textContent = secondary.category || secondary.medical_term || 'Unknown';
    } else {
        secondaryCause.textContent = 'Not identified';
    }

    // AGENT SCRIPT (combined from both root causes)
    let scriptText = '';

    if (rootCauses.length > 0) {
        // Primary explanation
        scriptText += rootCauses[0].explanation || '';

        // Add spacing
        if (rootCauses.length > 1 && rootCauses[1].explanation) {
            scriptText += '\n\n';
            // Secondary explanation
            scriptText += rootCauses[1].explanation;
        }
    }

    // If no explanations, use summary
    if (!scriptText) {
        scriptText = result.summary || 'No detailed explanation available.';
    }

    agentScript.textContent = scriptText;

    // TREATMENT PLAN
    if (detailed) {
        treatmentPlan.textContent = detailed;
    } else {
        // Fallback: combine recommended actions
        const actions = result.recommended_actions || [];
        let treatmentText = '';

        actions.forEach((action, index) => {
            if (index > 0) treatmentText += '\n\n';
            treatmentText += `${action.action_type.toUpperCase()}: ${action.description}`;
        });

        treatmentPlan.textContent = treatmentText || 'Treatment recommendations not available.';
    }

    // Show results
    resultsDisplay.style.display = 'block';

    // Scroll to results (optional)
    resultsDisplay.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// === SHOW LOADING ===
function showLoading() {
    emptyState.style.display = 'none';
    resultsDisplay.style.display = 'none';
    errorState.style.display = 'none';
    loadingState.style.display = 'block';
    analyzeBtn.disabled = true;
}

// === SHOW ERROR ===
function showError(message) {
    emptyState.style.display = 'none';
    resultsDisplay.style.display = 'none';
    loadingState.style.display = 'none';
    errorMessage.textContent = message;
    errorState.style.display = 'block';
    analyzeBtn.disabled = false;
}

// === COPY SCRIPT ===
copyBtn.addEventListener('click', () => {
    // Combine agent script and treatment for copying
    const textToCopy = `ROOT CAUSES
${'-'.repeat(50)}
PRIMARY: ${primaryCause.textContent}
SECONDARY: ${secondaryCause.textContent}

AGENT SCRIPT
${'-'.repeat(50)}
${agentScript.textContent}

TREATMENT PLAN
${'-'.repeat(50)}
${treatmentPlan.textContent}`;

    navigator.clipboard.writeText(textToCopy).then(() => {
        // Visual feedback
        const originalText = copyBtn.textContent;
        copyBtn.textContent = 'Copied!';
        copyBtn.style.background = 'var(--success-green)';
        copyBtn.style.color = 'white';
        copyBtn.style.borderColor = 'var(--success-green)';

        setTimeout(() => {
            copyBtn.textContent = originalText;
            copyBtn.style.background = '';
            copyBtn.style.color = '';
            copyBtn.style.borderColor = '';
        }, 2000);
    }).catch(err => {
        console.error('Copy failed:', err);
        alert('Failed to copy. Please select and copy manually.');
    });
});

// === RESET ===
resetBtn.addEventListener('click', () => {
    resultsDisplay.style.display = 'none';
    emptyState.style.display = 'block';
    form.reset();
    analyzeBtn.disabled = false;

    // Reset conditional sections
    peSection.style.display = 'none';
    edSection.style.display = 'none';
});

// === RETRY ===
retryBtn.addEventListener('click', () => {
    errorState.style.display = 'none';
    emptyState.style.display = 'block';
    analyzeBtn.disabled = false;
});

// === INITIAL STATE ===
console.log('RxMen Discovery Call Copilot - Loaded');
console.log('API Endpoint:', ANALYZE_ENDPOINT);
console.log('Make sure backend server is running at:', API_BASE_URL);
