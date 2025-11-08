/*
 * RxMen Discovery Call Form - Validation Logic
 * Handle form validation and error display
 */

// ==================== VALIDATION RULES ====================

const validationRules = {
    // Age validation (11-99, RED FLAG for <18 and >80)
    age: (value) => {
        const age = parseInt(value);
        if (isNaN(age)) return 'Please enter a valid age';
        if (age < 11) return 'Age must be at least 11';
        if (age > 99) return 'Age must be less than 100';

        // Red flags (handled separately in main.js)
        if (age < 18) return 'RED_FLAG_MINOR';
        if (age > 80) return 'RED_FLAG_ELDERLY';

        return null;
    },

    // Height validation (cm: 140-220)
    height_cm: (value) => {
        const height = parseFloat(value);
        if (height < 140 || height > 220) {
            return 'Height must be between 140-220 cm';
        }
        return null;
    },

    // Height validation (feet: 4-7)
    height_feet: (value) => {
        const feet = parseInt(value);
        if (feet < 4 || feet > 7) {
            return 'Height must be between 4-7 feet';
        }
        return null;
    },

    // Height validation (inches: 0-11)
    height_inches: (value) => {
        const inches = parseInt(value);
        if (inches < 0 || inches > 11) {
            return 'Inches must be between 0-11';
        }
        return null;
    },

    // Weight validation (40-200 kg)
    weight_kg: (value) => {
        const weight = parseFloat(value);
        if (weight < 40 || weight > 200) {
            return 'Weight must be between 40-200 kg';
        }
        return null;
    },

    // Required field validation
    required: (value, fieldName) => {
        if (!value || value.trim() === '') {
            return `This field is required`;
        }
        return null;
    }
};

// ==================== FIELD VALIDATION ====================

/**
 * Validate a single field
 */
function validateField(field) {
    const { $ } = window.utils;
    const fieldName = field.name;
    const value = field.value;

    // Check if required
    if (field.hasAttribute('required') && (!value || value.trim() === '')) {
        return 'This field is required';
    }

    // Run specific validation rule if exists
    if (validationRules[fieldName]) {
        const error = validationRules[fieldName](value);
        if (error) return error;
    }

    return null;
}

/**
 * Validate a radio group
 */
function validateRadioGroup(fieldName) {
    const { $ } = window.utils;
    const checked = $(`[name="${fieldName}"]:checked`);

    if (!checked) {
        // Check if any radio in the group is required
        const anyRequired = $(`[name="${fieldName}"][required]`);
        if (anyRequired) {
            return 'Please select an option';
        }
    }

    return null;
}

/**
 * Validate a checkbox group
 */
function validateCheckboxGroup(fieldName) {
    const { $, $$ } = window.utils;
    const checked = $$(`[name="${fieldName}"]:checked`);

    if (checked.length === 0) {
        // Check if any checkbox in the group is required
        const anyRequired = $(`[name="${fieldName}"][required]`);
        if (anyRequired) {
            return 'Please select at least one option';
        }
    }

    return null;
}

// ==================== ERROR DISPLAY ====================

/**
 * Show error message for a field
 */
function showError(field, message) {
    // Add error class to field
    field.classList.add('error');

    // Find and show error message span
    const errorId = `${field.id || field.name}-error`;
    const errorSpan = $(`#${errorId}`);

    if (errorSpan) {
        errorSpan.textContent = message;
        errorSpan.classList.add('visible');
    }

    // Mark parent question as incomplete
    const question = field.closest('.form-question');
    if (question) {
        question.classList.add('incomplete');
    }
}

/**
 * Hide error message for a field
 */
function hideError(field) {
    // Remove error class from field
    field.classList.remove('error');

    // Find and hide error message span
    const errorId = `${field.id || field.name}-error`;
    const errorSpan = $(`#${errorId}`);

    if (errorSpan) {
        errorSpan.textContent = '';
        errorSpan.classList.remove('visible');
    }

    // Remove incomplete class from parent question
    const question = field.closest('.form-question');
    if (question) {
        question.classList.remove('incomplete');
    }
}

// ==================== SECTION VALIDATION ====================

/**
 * Validate entire section
 */
function validateSection(sectionNumber) {
    const { $ } = window.utils;
    const section = $(`#section-${sectionNumber}`);
    if (!section) return { isValid: true, errors: [] };

    // Skip validation if section is hidden (display: none)
    if (section.style.display === 'none' || !window.utils.isVisible(section)) {
        return { isValid: true, errors: [] };
    }

    let isValid = true;
    const errors = [];

    // Get all visible questions
    const questions = section.querySelectorAll('.form-question:not(.hidden)');

    questions.forEach(question => {
        // Skip if question is in a hidden conditional branch
        const branch = question.closest('.conditional-branch');
        if (branch && branch.classList.contains('hidden')) return;

        // Get field name from first input
        const firstInput = question.querySelector('input, textarea, select');
        if (!firstInput) return;

        const fieldName = firstInput.name;
        const fieldType = firstInput.type;

        let error = null;

        if (fieldType === 'radio') {
            error = validateRadioGroup(fieldName);
            if (error) {
                showError(firstInput, error);
                errors.push({ field: firstInput, message: error });
                isValid = false;
            }
        } else if (fieldType === 'checkbox') {
            error = validateCheckboxGroup(fieldName);
            if (error) {
                showError(firstInput, error);
                errors.push({ field: firstInput, message: error });
                isValid = false;
            }
        } else {
            error = validateField(firstInput);
            if (error && !error.startsWith('RED_FLAG')) {
                showError(firstInput, error);
                errors.push({ field: firstInput, message: error });
                isValid = false;
            }
        }
    });

    return { isValid, errors };
}

/**
 * Validate entire form
 */
function validateForm() {
    let allValid = true;
    let firstInvalidSection = null;
    const allErrors = [];

    for (let i = 1; i <= 7; i++) {
        const result = validateSection(i);

        if (!result.isValid) {
            allValid = false;
            if (!firstInvalidSection) {
                firstInvalidSection = i;
            }
            allErrors.push(...result.errors);
        }
    }

    return {
        isValid: allValid,
        firstInvalidSection,
        errors: allErrors
    };
}

// ==================== REAL-TIME VALIDATION ====================

/**
 * Set up real-time validation for all fields
 */
function setupRealTimeValidation() {
    const { $$ } = window.utils;
    // Validate text inputs on blur
    $$('input[type="text"], input[type="number"], textarea').forEach(field => {
        field.addEventListener('blur', function() {
            const error = validateField(this);
            if (error && !error.startsWith('RED_FLAG')) {
                showError(this, error);
            } else if (!error) {
                hideError(this);
            }
        });

        // Clear error on input
        field.addEventListener('input', function() {
            if (this.classList.contains('error')) {
                hideError(this);
            }
            // Update section status count
            const section = this.closest('.form-section');
            if (section && typeof updateSectionStatus === 'function') {
                const sectionNum = parseInt(section.dataset.section);
                if (sectionNum) updateSectionStatus(sectionNum);
            }
        });
    });

    // Validate radio buttons on change
    $$('input[type="radio"]').forEach(radio => {
        radio.addEventListener('change', function() {
            const error = validateRadioGroup(this.name);
            if (!error) {
                hideError(this);
            }
            // Update section status count
            const section = this.closest('.form-section');
            if (section && typeof updateSectionStatus === 'function') {
                const sectionNum = parseInt(section.dataset.section);
                if (sectionNum) updateSectionStatus(sectionNum);
            }
        });
    });

    // Validate checkboxes on change
    $$('input[type="checkbox"]').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const error = validateCheckboxGroup(this.name);
            if (!error) {
                hideError(this);
            }
            // Update section status count
            const section = this.closest('.form-section');
            if (section && typeof updateSectionStatus === 'function') {
                const sectionNum = parseInt(section.dataset.section);
                if (sectionNum) updateSectionStatus(sectionNum);
            }
        });
    });

    console.log(' Real-time validation enabled');
}

// ==================== ERROR BANNER ====================

/**
 * Show error banner with list of incomplete fields
 */
function showErrorBanner(errors) {
    const { $ } = window.utils;
    const banner = $('#error-banner');
    const message = $('#error-banner-message');
    const fieldList = $('#error-field-list');

    if (!banner || !message) return;

    // Set message
    message.textContent = `${errors.length} required fields missing`;

    // Create clickable field links
    fieldList.innerHTML = '';
    errors.forEach(({ field }) => {
        const link = document.createElement('a');
        link.href = '#';
        link.className = 'error-field-link';
        link.textContent = field.closest('.form-question')?.dataset.question || field.name;

        link.addEventListener('click', (e) => {
            e.preventDefault();
            window.utils.scrollTo(field);
            field.focus();
        });

        fieldList.appendChild(link);
    });

    // Show banner
    banner.style.display = 'block';
}

/**
 * Hide error banner
 */
function hideErrorBanner() {
    const { $ } = window.utils;
    const banner = $('#error-banner');
    if (banner) {
        banner.style.display = 'none';
    }
}

// ==================== EXPORT ====================

window.validation = {
    validateField,
    validateRadioGroup,
    validateCheckboxGroup,
    validateSection,
    validateForm,
    showError,
    hideError,
    setupRealTimeValidation,
    showErrorBanner,
    hideErrorBanner
};

console.log(' Validation loaded');
