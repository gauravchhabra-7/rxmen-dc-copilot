/*
 * RxMen Discovery Call Form - Main Application Logic
 * Conditional logic, form submission, and initialization
 */

// ==================== INITIALIZATION ====================

document.addEventListener('DOMContentLoaded', function() {
    console.log('=� RxMen Discovery Form Initializing...');

    // Initialize modules
    window.sections.initializeSections();
    window.sections.initializeSectionIndicators();
    window.validation.setupRealTimeValidation();

    // Set up conditional logic
    setupConditionalLogic();

    // Set up form submission
    setupFormSubmission();

    // Set up auto-save
    setupAutoSave();

    // Set up special interactions
    setupSpecialInteractions();

    // Close error banner button
    const closeBtn = $('#error-banner-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            window.validation.hideErrorBanner();
        });
    }

    console.log(' Form initialized successfully');
});

// ==================== CONDITIONAL LOGIC ====================

/**
 * Set up all conditional display logic
 */
function setupConditionalLogic() {
    const { $, $$, show, hide, getFieldValue, debounce } = window.utils;
    // Watch for changes that trigger conditional display
    document.addEventListener('change', function(e) {
        const target = e.target;

        // Height unit toggle (cm vs ft-in)
        if (target.id === 'height-cm-toggle' || target.id === 'height-ft-toggle') {
            handleHeightUnitToggle(target);
        }

        // Relationship status (triggers Section 5 visibility)
        if (target.name === 'relationship_status') {
            handleRelationshipStatusChange();
        }

        // Main issue (triggers Section 6A/6B visibility)
        if (target.name === 'main_issue') {
            handleMainIssueChange();
        }

        // Masturbation method (triggers Q4.2 & Q4.3 visibility)
        if (target.name === 'masturbation_method') {
            handleMasturbationMethodChange();
        }

        // First consultation (triggers previous treatments)
        if (target.name === 'first_consultation') {
            handleFirstConsultationChange();
        }

        // Medical conditions "Other" checkbox
        if (target.id === 'medical-conditions-other-checkbox') {
            handleOtherCheckbox('medical-conditions-other');
        }

        // Current medications "Other" checkbox
        if (target.id === 'current-medications-other-checkbox') {
            handleOtherCheckbox('current-medications-other');
        }

        // Blood thinners red flag
        if (target.name === 'current_medications' && target.value === 'blood_thinners') {
            handleBloodThinnersWarning();
        }

        // Exclusive checkbox logic (None option)
        if (target.type === 'checkbox' && target.dataset.exclusive) {
            handleExclusiveCheckbox(target);
        }

        // Age red flags
        if (target.name === 'age') {
            handleAgeRedFlags();
        }

        // Auto-save on any change
        debouncedSave();
    });

    // Initialize conditional display on load
    handleRelationshipStatusChange();
    handleMainIssueChange();
    handleMasturbationMethodChange();

    console.log(' Conditional logic set up');
}

/**
 * Handle height unit toggle (cm vs ft-in)
 */
function handleHeightUnitToggle(button) {
    const { $$, show, hide } = window.utils;
    const unit = button.dataset.unit;

    // Update toggle buttons
    $$('.toggle-option').forEach(btn => {
        btn.classList.remove('active');
        btn.setAttribute('aria-pressed', 'false');
    });
    button.classList.add('active');
    button.setAttribute('aria-pressed', 'true');

    // Show/hide appropriate input
    if (unit === 'cm') {
        show('#height-cm-input');
        hide('#height-ft-input');
    } else {
        hide('#height-cm-input');
        show('#height-ft-input');
    }
}

/**
 * Handle relationship status change (Section 5 visibility)
 */
function handleRelationshipStatusChange() {
    const { $, getFieldValue } = window.utils;
    const status = getFieldValue('relationship_status');
    const section5 = $('#section-5');

    if (!section5) return;

    if (status === 'married' || status === 'in_relationship') {
        section5.style.display = 'block';
    } else {
        section5.style.display = 'none';
    }
}

/**
 * Handle main issue change (Section 6A/6B visibility)
 */
function handleMainIssueChange() {
    const { $, show, hide, getFieldValue } = window.utils;
    const mainIssue = getFieldValue('main_issue');
    const edBranch = $('#section-6a-ed-branch');
    const peBranch = $('#section-6b-pe-branch');

    if (!edBranch || !peBranch) return;

    // Show/hide ED branch
    if (mainIssue === 'ed' || mainIssue === 'both') {
        show(edBranch);
    } else {
        hide(edBranch);
    }

    // Show/hide PE branch
    if (mainIssue === 'pe' || mainIssue === 'both') {
        show(peBranch);
    } else {
        hide(peBranch);
    }
}

/**
 * Handle masturbation method change (Q4.2 & Q4.3 visibility)
 */
function handleMasturbationMethodChange() {
    const { $, show, hide, getFieldValue } = window.utils;
    const method = getFieldValue('masturbation_method');
    const detailsGroup = $('#masturbation-details-group');

    if (!detailsGroup) return;

    if (method === 'none') {
        hide(detailsGroup);
    } else {
        show(detailsGroup);
    }
}

/**
 * Handle first consultation change (previous treatments visibility)
 */
function handleFirstConsultationChange() {
    const { $, show, hide, getFieldValue } = window.utils;
    const firstConsult = getFieldValue('first_consultation');
    const treatmentsGroup = $('#previous-treatments-group');

    if (!treatmentsGroup) return;

    if (firstConsult === 'no') {
        show(treatmentsGroup);
    } else {
        hide(treatmentsGroup);
    }
}

/**
 * Handle "Other" checkbox - show/hide text input
 */
function handleOtherCheckbox(fieldPrefix) {
    const { $, show, hide } = window.utils;
    const checkbox = $(`#${fieldPrefix}-checkbox`);
    const textInput = $(`#${fieldPrefix}-text`);

    if (!checkbox || !textInput) return;

    if (checkbox.checked) {
        show(textInput);
        textInput.focus();
    } else {
        hide(textInput);
        textInput.value = '';
    }
}

/**
 * Handle blood thinners warning
 */
function handleBloodThinnersWarning() {
    const { $ } = window.utils;
    const checkbox = $('[name="current_medications"][value="blood_thinners"]');
    const warning = $('#blood-thinners-warning');

    if (!checkbox || !warning) return;

    if (checkbox.checked) {
        warning.style.display = 'block';
    } else {
        warning.style.display = 'none';
    }
}

/**
 * Handle exclusive checkbox (e.g., "None" disables others)
 */
function handleExclusiveCheckbox(exclusiveCheckbox) {
    const { $$ } = window.utils;
    const groupName = exclusiveCheckbox.name;
    const otherCheckboxes = $$(`[name="${groupName}"]:not([data-exclusive])`);

    if (exclusiveCheckbox.checked) {
        // Uncheck all others
        otherCheckboxes.forEach(cb => {
            cb.checked = false;
            cb.disabled = true;
            cb.closest('.checkbox-option')?.classList.add('disabled');
        });
    } else {
        // Enable all others
        otherCheckboxes.forEach(cb => {
            cb.disabled = false;
            cb.closest('.checkbox-option')?.classList.remove('disabled');
        });
    }
}

/**
 * Handle age red flags
 */
function handleAgeRedFlags() {
    const { $, getFieldValue } = window.utils;
    const age = parseInt(getFieldValue('age'));
    const warning = $('#age-warning');

    if (!warning || isNaN(age)) return;

    if (age < 18) {
        warning.textContent = '=� RED FLAG: Patient is a minor. Cannot proceed with online consultation. Decline call and document.';
        warning.style.display = 'block';
        warning.style.background = '#FEE';
        warning.style.padding = '12px';
        warning.style.borderRadius = '4px';
        warning.style.color = '#FF0000';
        warning.style.fontWeight = '600';
    } else if (age > 80) {
        warning.textContent = '� WARNING: In-person consultation required for elderly patients (age 80+). Flag for doctor review.';
        warning.style.display = 'block';
        warning.style.background = '#FFF4E6';
        warning.style.padding = '12px';
        warning.style.borderRadius = '4px';
        warning.style.color = '#FF9800';
        warning.style.fontWeight = '600';
    } else {
        warning.style.display = 'none';
    }
}

// ==================== FORM SUBMISSION ====================

/**
 * Set up form submission handler
 */
function setupFormSubmission() {
    const { $ } = window.utils;
    const form = $('#discovery-form');
    const submitBtn = $('#submit-btn');

    if (!form || !submitBtn) return;

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        console.log('=� Form submitted');

        // Hide previous error banner
        window.validation.hideErrorBanner();

        // Validate entire form
        const result = window.validation.validateForm();

        if (!result.isValid) {
            // Show error banner
            window.validation.showErrorBanner(result.errors);

            // Scroll to first invalid section
            if (result.firstInvalidSection) {
                const section = $(`#section-${result.firstInvalidSection}`);
                if (section) {
                    window.sections.expandSection(section);
                    window.utils.scrollTo(section);
                }
            }

            // Scroll to first error
            if (result.errors.length > 0) {
                setTimeout(() => {
                    window.utils.scrollTo(result.errors[0].field);
                    result.errors[0].field.focus();
                }, 500);
            }

            return;
        }

        // All valid - proceed with submission
        console.log(' Form is valid, submitting...');

        // Disable submit button
        submitBtn.disabled = true;
        submitBtn.textContent = 'Submitting...';
        submitBtn.classList.add('loading');

        // Get form data
        const formData = window.utils.getFormData(form);

        try {
            // TODO: Integrate with Claude API + Google Sheets
            // For now, just log the data
            console.log('Form Data:', formData);

            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 2000));

            // Show success message
            alert('Form submitted successfully!\\n\\nNext step: Integrate with Claude API for AI analysis.');

            // Clear form state
            window.utils.clearFormState();

            // Reset form
            //form.reset();

        } catch (error) {
            console.error('Submission error:', error);
            alert('Submission failed. Please try again.');
        } finally {
            // Re-enable submit button
            submitBtn.disabled = false;
            submitBtn.textContent = 'Submit Form';
            submitBtn.classList.remove('loading');
        }
    });

    console.log(' Form submission handler set up');
}

// ==================== AUTO-SAVE ====================

const debouncedSave = window.utils.debounce(window.utils.saveFormState, 1000);

function setupAutoSave() {
    // Load saved form state on page load
    window.utils.loadFormState();

    // Save on form changes (debounced)
    // Already handled by conditional logic listener

    console.log(' Auto-save enabled');
}

// ==================== SPECIAL INTERACTIONS ====================

/**
 * Set up special interactions (character counter, etc.)
 */
function setupSpecialInteractions() {
    const { $ } = window.utils;
    // Character counter for textarea
    const textarea = $('#additional-info');
    const charCount = $('#char-count');

    if (textarea && charCount) {
        textarea.addEventListener('input', function() {
            const count = this.value.length;
            charCount.textContent = count;

            const counter = this.nextElementSibling;
            if (counter && counter.classList.contains('char-counter')) {
                counter.classList.remove('warning', 'limit');

                if (count > 900) {
                    counter.classList.add('limit');
                } else if (count > 800) {
                    counter.classList.add('warning');
                }
            }
        });
    }

    // Height toggle buttons
    const cmToggle = $('#height-cm-toggle');
    const ftToggle = $('#height-ft-toggle');

    if (cmToggle && ftToggle) {
        cmToggle.addEventListener('click', () => handleHeightUnitToggle(cmToggle));
        ftToggle.addEventListener('click', () => handleHeightUnitToggle(ftToggle));
    }

    console.log(' Special interactions set up');
}

console.log(' Main.js loaded');
