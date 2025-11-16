/*
 * RxMen Discovery Call Form - Main Application Logic
 * Conditional logic, form submission, and initialization
 */

// ==================== INITIALIZATION ====================

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 RxMen Discovery Form Initializing...');

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

    // Prevent Enter key from submitting form
    preventEnterSubmission();

    // Close error banner button
    const closeBtn = $('#error-banner-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            window.validation.hideErrorBanner();
        });
    }

    console.log('✅ Form initialized successfully');
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

        // ED gateway question (triggers Q5A.2-Q5A.7 visibility)
        if (target.name === 'ed_gets_erections') {
            handleEDGatewayChange();
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

        // Surgery/injury red flag
        if (target.name === 'spinal_genital_surgery') {
            handleSurgeryInjuryWarning();
        }

        // Exclusive checkbox logic (None option)
        if (target.type === 'checkbox' && target.dataset.exclusive) {
            handleExclusiveCheckbox(target);
        }

        // Age red flags
        if (target.name === 'age') {
            handleAgeRedFlags();
        }

        // Emergency red flags
        if (target.name === 'emergency_red_flags') {
            handleEmergencyRedFlags();
        }

        // Sync ED and PE sexual activity answers when "both" is selected
        if (target.name === 'ed_sexual_activity_status') {
            handleSexualActivitySync();
        }

        // Auto-save on any change
        debouncedSave();
    });

    // Initialize conditional display on load
    handleRelationshipStatusChange();
    handleMainIssueChange();
    handleMasturbationMethodChange();
    handleEDGatewayChange();

    console.log('✅ Conditional logic set up');
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
 * Handle relationship status change (Q4.5 visibility)
 */
function handleRelationshipStatusChange() {
    const { $, show, hide, getFieldValue } = window.utils;
    const status = getFieldValue('relationship_status');
    const partnerResponseGroup = $('#partner-response-group');

    if (!partnerResponseGroup) return;

    if (status === 'married' || status === 'in_relationship') {
        show(partnerResponseGroup);
    } else {
        hide(partnerResponseGroup);
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

    // Hide duplicate sexual activity question in PE branch when "both" is selected
    // (ED branch Q5A.2 and PE branch Q5B.1 ask the same question)
    const peFirstQuestion = peBranch.querySelector('[data-question="5b.1"]');
    if (peFirstQuestion) {
        if (mainIssue === 'both') {
            hide(peFirstQuestion);
        } else if (mainIssue === 'pe') {
            show(peFirstQuestion);
        }
    }
}

/**
 * Handle masturbation method change (Q4.2 & Q4.3 visibility)
 */
function handleMasturbationMethodChange() {
    const { $, show, hide, getFieldValue } = window.utils;
    const method = getFieldValue('masturbation_method');
    const gripGroup = $('#masturbation-grip-group');      // Q4.2
    const frequencyGroup = $('#masturbation-frequency-group');  // Q4.3

    if (!gripGroup || !frequencyGroup) return;

    // Q4.2 (Grip) logic: show only for "hands" or "both"
    // Hide for "none" and "prone" (grip not applicable without hands)
    if (method === 'hands' || method === 'both') {
        show(gripGroup);
    } else {
        hide(gripGroup);
    }

    // Q4.3 (Frequency) logic: show for all methods except "none"
    // Show for "hands", "prone", and "both"
    if (method === 'none') {
        hide(frequencyGroup);
    } else {
        show(frequencyGroup);
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
 * Handle ED gateway question (Q5A.1)
 */
function handleEDGatewayChange() {
    const { $, show, hide, getFieldValue } = window.utils;
    const getsErections = getFieldValue('ed_gets_erections');
    const followupGroup = $('#ed-followup-questions-group');

    if (!followupGroup) return;

    // Show ED follow-up questions only if user gets erections
    if (getsErections === 'yes') {
        show(followupGroup);
    } else {
        hide(followupGroup);
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
 * Handle surgery/injury warning
 */
function handleSurgeryInjuryWarning() {
    const { $, getFieldValue } = window.utils;
    const value = getFieldValue('spinal_genital_surgery');
    const warning = $('#surgery-injury-warning');

    if (!warning) return;

    if (value === 'yes') {
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
        warning.textContent = '⚠️ RED FLAG: Patient is a minor. Cannot proceed with online consultation. Decline call and document.';
        warning.style.display = 'block';
        warning.style.background = '#FEE';
        warning.style.padding = '12px';
        warning.style.borderRadius = '4px';
        warning.style.color = '#FF0000';
        warning.style.fontWeight = '600';
    } else if (age > 80) {
        warning.textContent = '⚠️ WARNING: In-person consultation required for elderly patients (age 80+). Flag for doctor review.';
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

/**
 * Handle emergency red flags - show inline alert and disable form
 */
function handleEmergencyRedFlags() {
    const { $, $$, getFieldValue } = window.utils;
    const value = getFieldValue('emergency_red_flags');
    const alert = $('#red-flag-alert');
    const message = $('#red-flag-message');
    const form = $('#discovery-form');

    if (!alert || !message || !form) return;

    // Define red flag messages
    const redFlagMessages = {
        'severe_pain': '⚠️ IMMEDIATE ESCALATION REQUIRED: Severe pain in penis/testicles may indicate testicular torsion or infection. Advise patient to seek emergency in-person consultation immediately. Do not proceed with this form.',
        'blood': '⚠️ STOP CONSULTATION: Blood in urine or semen requires immediate urologist/andrologist referral. Instruct patient to see a physician as soon as possible. Do not proceed with this form.',
        'priapism': '⚠️ MEDICAL EMERGENCY: Erection lasting more than 4 hours (priapism) requires urgent medical treatment. Tell patient to go to the nearest hospital IMMEDIATELY. Do not proceed with this form.'
    };

    if (value && value !== 'none' && redFlagMessages[value]) {
        // Show alert
        message.textContent = redFlagMessages[value];
        alert.classList.remove('hidden');
        alert.style.display = 'block';

        // Disable all form sections except Section 1
        $$('.form-section').forEach((section) => {
            const sectionNum = parseInt(section.dataset.section);
            if (sectionNum > 1) {
                // Disable all inputs in this section
                section.querySelectorAll('input, textarea, select, button').forEach(input => {
                    input.disabled = true;
                    input.style.opacity = '0.5';
                    input.style.cursor = 'not-allowed';
                });
            }
        });

        // Disable submit button
        const submitBtn = $('#submit-btn');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.style.opacity = '0.5';
            submitBtn.style.cursor = 'not-allowed';
        }
    } else {
        // Hide alert and re-enable form
        alert.classList.add('hidden');
        alert.style.display = 'none';

        // Re-enable all form elements
        $$('input, textarea, select, button').forEach(input => {
            input.disabled = false;
            input.style.opacity = '';
            input.style.cursor = '';
        });
    }
}

// ==================== FORM SUBMISSION ====================

/**
 * Sync ED and PE sexual activity answers when "both" is selected
 * (Avoids duplicate question by using ED answer for both branches)
 */
function handleSexualActivitySync() {
    const { $, $$, getFieldValue, setFieldValue } = window.utils;
    const mainIssue = getFieldValue('main_issue');

    // Only sync when "both" is selected
    if (mainIssue !== 'both') return;

    const edValue = getFieldValue('ed_sexual_activity_status');
    if (edValue) {
        setFieldValue('pe_sexual_activity_status', edValue);
    }
}

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

        console.log('📋 Form submitted');

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
        console.log('✅ Form is valid, submitting...');

        // Show loading state
        window.api.showLoadingState();

        // Get form data
        const formData = window.utils.getFormData(form);

        try {
            // Call backend API
            console.log('📡 Calling backend API...');
            const result = await window.api.analyzePatientCase(formData);

            // Display diagnosis result
            window.api.displayDiagnosis(result);

            console.log('✅ Analysis complete');

            // Clear form state (auto-save data)
            window.utils.clearFormState();

        } catch (error) {
            console.error('❌ Analysis failed:', error);

            // Get user-friendly error message
            const errorMessage = window.api.getErrorMessage(error);

            // Display error
            window.api.displayError(errorMessage);

        } finally {
            // Hide loading state
            window.api.hideLoadingState();
        }
    });

    console.log('✅ Form submission handler set up');
}

// ==================== AUTO-SAVE ====================

const debouncedSave = window.utils.debounce(window.utils.saveFormState, 1000);

function setupAutoSave() {
    // Load saved form state on page load
    window.utils.loadFormState();

    // Save on form changes (debounced)
    // Already handled by conditional logic listener

    console.log('✅ Auto-save enabled');
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

    console.log('✅ Special interactions set up');
}

console.log('✅ Main.js loaded');

// ==================== PREVENT ENTER KEY SUBMISSION ====================

/**
 * Prevent Enter key from submitting the form
 */
function preventEnterSubmission() {
    const { $ } = window.utils;
    const form = $('#discovery-form');

    if (!form) return;

    form.addEventListener('keydown', function(e) {
        // If Enter key is pressed in an input field (not textarea or submit button)
        if (e.key === 'Enter' && e.target.type !== 'textarea' && e.target.type !== 'submit') {
            e.preventDefault();
            return false;
        }
    });

    console.log('✅ Enter key submission prevented');
}
