/*
 * RxMen Discovery Call Form - Section Management
 * Handle accordion expand/collapse and section state
 */

// ==================== SECTION STATE ====================

const sectionState = {
    currentSection: 1,
    completedSections: [],
    totalSections: 6
};

// ==================== ACCORDION FUNCTIONALITY ====================

/**
 * Initialize section accordion behavior
 */
function initializeSections() {
    const { $, $$ } = window.utils;
    // Add click handlers to all section headers
    $$('.section-header').forEach((header) => {
        header.addEventListener('click', function() {
            const section = this.closest('.form-section');
            toggleSection(section);
        });
    });

    // Expand first section by default
    const firstSection = $('#section-1');
    if (firstSection) {
        expandSection(firstSection);
    }

    console.log(' Sections initialized');
}

/**
 * Toggle section expand/collapse
 */
function toggleSection(section) {
    // Don't toggle sections marked as always-open
    if (section.dataset.alwaysOpen === 'true') {
        return;
    }

    if (section.classList.contains('collapsed')) {
        expandSection(section);
    } else {
        collapseSection(section);
    }
}

/**
 * Expand a section
 */
function expandSection(section) {
    section.classList.remove('collapsed');
    section.classList.add('expanded');

    // Update toggle icon
    const icon = section.querySelector('.toggle-icon');
    if (icon) {
        icon.textContent = '\u25BC'; // ▼ Down arrow
    }

    // Update current section
    const sectionNum = parseInt(section.dataset.section);
    if (sectionNum) {
        sectionState.currentSection = sectionNum;
        updateProgressIndicator();
    }
}

/**
 * Collapse a section
 */
function collapseSection(section) {
    section.classList.remove('expanded');
    section.classList.add('collapsed');

    // Update toggle icon
    const icon = section.querySelector('.toggle-icon');
    if (icon) {
        icon.textContent = '\u25B6'; // ▶ Right arrow
    }
}

/**
 * Mark section as complete
 */
function markSectionComplete(sectionNumber) {
    const { $ } = window.utils;
    const section = $(`#section-${sectionNumber}`);
    if (!section) return;

    // Add completed class
    section.classList.add('completed');

    // Add to completed sections if not already there
    if (!sectionState.completedSections.includes(sectionNumber)) {
        sectionState.completedSections.push(sectionNumber);
    }

    // Update section status text
    updateSectionStatus(sectionNumber);

    // Update progress
    updateProgressIndicator();

    // Auto-collapse completed section
    collapseSection(section);

    // Expand next section
    const nextSection = $(`#section-${sectionNumber + 1}`);
    if (nextSection) {
        setTimeout(() => {
            expandSection(nextSection);
            // Scroll to next section
            window.utils.scrollTo(nextSection);
        }, 300);
    }
}

/**
 * Update section status text (e.g., "3/7 completed")
 */
function updateSectionStatus(sectionNumber) {
    const { $, $$ } = window.utils;
    const statusSpan = $(`#section-${sectionNumber}-status`);
    if (!statusSpan) return;

    // Count completed questions in this section
    const section = $(`#section-${sectionNumber}`);
    const questions = $$('.form-question', section);
    const completed = questions.filter(q => isQuestionComplete(q)).length;

    // Skip if section 6 (optional)
    if (sectionNumber === 6) {
        statusSpan.textContent = 'Optional';
        return;
    }

    statusSpan.textContent = `${completed}/${questions.length} completed`;
}

/**
 * Check if a question is complete
 */
function isQuestionComplete(questionElement) {
    const inputs = questionElement.querySelectorAll('input, textarea, select');

    for (let input of inputs) {
        if (input.hasAttribute('required')) {
            // Radio buttons
            if (input.type === 'radio') {
                const name = input.name;
                const checked = questionElement.querySelector(`[name="${name}"]:checked`);
                if (!checked) return false;
            }
            // Checkboxes
            else if (input.type === 'checkbox') {
                const name = input.name;
                const checked = questionElement.querySelectorAll(`[name="${name}"]:checked`);
                if (checked.length === 0) return false;
            }
            // Other inputs
            else {
                if (!input.value || input.value.trim() === '') return false;
            }
        }
    }

    return true;
}

// ==================== PROGRESS INDICATOR ====================

/**
 * Update progress indicator (bar and percentage)
 */
function updateProgressIndicator() {
    const { $ } = window.utils;
    const current = sectionState.currentSection;
    const total = sectionState.totalSections;

    // Calculate progress based on current section (not completed sections)
    // Section 1 = 0%, Section 2 = 17%, Section 3 = 33%, etc.
    const percentage = Math.round(((current - 1) / total) * 100);

    // Update progress bar
    const progressFill = $('#progress-fill');
    if (progressFill) {
        progressFill.style.width = `${percentage}%`;
    }

    // Update progress text
    const progressText = $('#progress-text');
    if (progressText) {
        progressText.textContent = `Section ${current} of ${total} • ${percentage}% Complete`;
    }

    // Update section indicators
    updateSectionIndicators();
}

/**
 * Update section indicators (numbered circles at top)
 */
function updateSectionIndicators() {
    const { $$ } = window.utils;
    $$('.indicator').forEach((indicator, index) => {
        const sectionNum = index + 1;

        // Remove all state classes
        indicator.classList.remove('active', 'completed');

        // Add appropriate class
        if (sectionState.completedSections.includes(sectionNum)) {
            indicator.classList.add('completed');
        } else if (sectionNum === sectionState.currentSection) {
            indicator.classList.add('active');
        }
    });
}

/**
 * Make section indicators clickable to jump to sections
 */
function initializeSectionIndicators() {
    const { $ , $$ } = window.utils;
    $$('.indicator').forEach((indicator) => {
        indicator.addEventListener('click', function() {
            const sectionNum = parseInt(this.dataset.section);
            const section = $(`#section-${sectionNum}`);

            if (section) {
                // Expand clicked section
                expandSection(section);
                // Scroll to it
                window.utils.scrollTo(section);
            }
        });
    });
}

// ==================== EXPORT ====================

window.sections = {
    initializeSections,
    toggleSection,
    expandSection,
    collapseSection,
    markSectionComplete,
    updateSectionStatus,
    updateProgressIndicator,
    initializeSectionIndicators,
    sectionState
};

console.log(' Sections loaded');
