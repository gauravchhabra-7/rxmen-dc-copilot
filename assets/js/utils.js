/*
 * RxMen Discovery Call Form - Utility Functions
 * Helper functions used across the application
 */

// ==================== DOM UTILITIES ====================

/**
 * Shorthand for document.querySelector
 */
const $ = (selector) => document.querySelector(selector);

/**
 * Shorthand for document.querySelectorAll (returns array)
 */
const $$ = (selector) => Array.from(document.querySelectorAll(selector));

/**
 * Add event listener with delegation support
 */
const on = (element, event, selector, handler) => {
    if (typeof selector === 'function') {
        handler = selector;
        element.addEventListener(event, handler);
    } else {
        element.addEventListener(event, (e) => {
            if (e.target.matches(selector) || e.target.closest(selector)) {
                handler.call(e.target.closest(selector), e);
            }
        });
    }
};

// ==================== FORM DATA UTILITIES ====================

/**
 * Get form data as an object
 */
const getFormData = (form) => {
    const formData = new FormData(form);
    const data = {};

    for (let [key, value] of formData.entries()) {
        // Handle multiple checkboxes with same name
        if (data[key]) {
            if (Array.isArray(data[key])) {
                data[key].push(value);
            } else {
                data[key] = [data[key], value];
            }
        } else {
            data[key] = value;
        }
    }

    return data;
};

/**
 * Get value of a form field by name
 */
const getFieldValue = (fieldName) => {
    const field = $(`[name="${fieldName}"]`);
    if (!field) return null;

    if (field.type === 'radio') {
        const checked = $(`[name="${fieldName}"]:checked`);
        return checked ? checked.value : null;
    }

    if (field.type === 'checkbox') {
        const checked = $$(`[name="${fieldName}"]:checked`);
        return checked.map(cb => cb.value);
    }

    return field.value;
};

/**
 * Set value of a form field by name
 */
const setFieldValue = (fieldName, value) => {
    const fields = $$(`[name="${fieldName}"]`);

    fields.forEach(field => {
        if (field.type === 'radio') {
            field.checked = field.value === value;
        } else if (field.type === 'checkbox') {
            field.checked = Array.isArray(value) ? value.includes(field.value) : field.value === value;
        } else {
            field.value = value;
        }
    });
};

// ==================== VALIDATION UTILITIES ====================

/**
 * Check if a field has a value
 */
const hasValue = (fieldName) => {
    const value = getFieldValue(fieldName);

    if (Array.isArray(value)) {
        return value.length > 0;
    }

    return value !== null && value !== '' && value !== undefined;
};

/**
 * Check if a field is required
 */
const isRequired = (fieldName) => {
    const field = $(`[name="${fieldName}"]`);
    return field && field.hasAttribute('required');
};

// ==================== VISIBILITY UTILITIES ====================

/**
 * Show an element
 */
const show = (element) => {
    if (typeof element === 'string') {
        element = $(element);
    }
    if (element) {
        element.classList.remove('hidden');
    }
};

/**
 * Hide an element
 */
const hide = (element) => {
    if (typeof element === 'string') {
        element = $(element);
    }
    if (element) {
        element.classList.add('hidden');
    }
};

/**
 * Toggle element visibility
 */
const toggle = (element) => {
    if (typeof element === 'string') {
        element = $(element);
    }
    if (element) {
        element.classList.toggle('hidden');
    }
};

/**
 * Check if element is visible
 */
const isVisible = (element) => {
    if (typeof element === 'string') {
        element = $(element);
    }
    return element && !element.classList.contains('hidden');
};

// ==================== SCROLL UTILITIES ====================

/**
 * Smooth scroll to element
 */
const scrollTo = (element, offset = 100) => {
    if (typeof element === 'string') {
        element = $(element);
    }

    if (element) {
        const top = element.getBoundingClientRect().top + window.pageYOffset - offset;
        window.scrollTo({ top, behavior: 'smooth' });
    }
};

/**
 * Scroll to first incomplete field
 */
const scrollToFirstIncomplete = () => {
    const incomplete = $('.form-question.incomplete');
    if (incomplete) {
        scrollTo(incomplete);
        const input = incomplete.querySelector('input, textarea, select');
        if (input) {
            setTimeout(() => input.focus(), 500);
        }
    }
};

// ==================== LOCAL STORAGE UTILITIES ====================

/**
 * Save form state to localStorage
 */
const saveFormState = () => {
    const form = $('#discovery-form');
    if (!form) return;

    const data = getFormData(form);
    localStorage.setItem('rxmen-form-state', JSON.stringify(data));

    // Show auto-save indicator
    showAutoSaveIndicator();
};

/**
 * Load form state from localStorage
 */
const loadFormState = () => {
    const saved = localStorage.getItem('rxmen-form-state');
    if (!saved) return;

    try {
        const data = JSON.parse(saved);

        for (let [fieldName, value] of Object.entries(data)) {
            setFieldValue(fieldName, value);
        }

        console.log('Form state restored from localStorage');
    } catch (error) {
        console.error('Failed to restore form state:', error);
    }
};

/**
 * Clear form state from localStorage
 */
const clearFormState = () => {
    localStorage.removeItem('rxmen-form-state');
};

/**
 * Show auto-save indicator
 */
const showAutoSaveIndicator = () => {
    const indicator = $('#autosave-indicator');
    if (indicator) {
        indicator.style.opacity = '1';
        setTimeout(() => {
            indicator.style.opacity = '0';
        }, 2000);
    }
};

// ==================== DEBOUNCE UTILITY ====================

/**
 * Debounce function execution
 */
const debounce = (func, wait = 300) => {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
};

// ==================== STRING UTILITIES ====================

/**
 * Capitalize first letter of string
 */
const capitalize = (str) => {
    return str.charAt(0).toUpperCase() + str.slice(1);
};

/**
 * Convert snake_case to Title Case
 */
const toTitleCase = (str) => {
    return str
        .split('_')
        .map(word => capitalize(word))
        .join(' ');
};

// ==================== EXPORT UTILITIES ====================

// Make utilities available globally
window.utils = {
    $,
    $$,
    on,
    getFormData,
    getFieldValue,
    setFieldValue,
    hasValue,
    isRequired,
    show,
    hide,
    toggle,
    isVisible,
    scrollTo,
    scrollToFirstIncomplete,
    saveFormState,
    loadFormState,
    clearFormState,
    showAutoSaveIndicator,
    debounce,
    capitalize,
    toTitleCase
};

console.log(' Utils loaded');
