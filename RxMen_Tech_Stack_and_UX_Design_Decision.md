# RxMen Discovery Call Copilot
## Tech Stack & UX Design Decision Document

**Version:** 1.0  
**Date:** November 6, 2025  
**Status:** Final Recommendation  
**Purpose:** Technical implementation guidance for frontend development

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [UX Design Principles](#ux-design-principles)
3. [Tech Stack Recommendation](#tech-stack-recommendation)
4. [Implementation Architecture](#implementation-architecture)
5. [Development Roadmap](#development-roadmap)
6. [Deployment Strategy](#deployment-strategy)
7. [Testing & Quality Assurance](#testing--quality-assurance)
8. [Potential Issues & Solutions](#potential-issues--solutions)

---

## Executive Summary

### Decision: Plain HTML + CSS + JavaScript

**Rationale:** For a 15-day MVP with a non-technical Chief of Staff managing a form-based tool used by agents during live video calls, plain HTML/CSS/JS is the optimal choice.

### Key Factors:
- ✅ **Speed:** No build process - instant preview in browser
- ✅ **Simplicity:** Any developer can understand and modify
- ✅ **Iteration:** Make changes and refresh browser (5 seconds vs 30 seconds with React)
- ✅ **Deployment:** Drag-and-drop to Netlify (no CI/CD setup needed)
- ✅ **Learning Curve:** Zero - standard web technologies
- ✅ **Performance:** Loads in <500ms (critical for agent experience)
- ✅ **Debugging:** Browser DevTools - no source maps or transpilation issues
- ✅ **Timeline:** Fits perfectly in 15-day MVP schedule

### Why NOT React/Vue/Angular:
- ❌ Build process adds complexity (webpack/vite setup, dependencies)
- ❌ Slower iteration (npm install, build step, hot reload issues)
- ❌ Overkill for a data collection form (using a sledgehammer for a nail)
- ❌ Steeper learning curve if you need to modify later
- ❌ More things that can break (node_modules, build configs)
- ❌ Longer initial setup time (wastes MVP timeline)

**Bottom Line:** React is for complex web applications with state management, routing, and component reusability. You have a single-page form with conditional logic. Plain JavaScript is perfect.

---

## UX Design Principles

### Context: High Cognitive Load Environment

**Primary Use Case:**
- Agents fill form during **live video calls** with patients
- Agent is **listening, typing, and thinking** simultaneously
- Form must be **effortless** to use - zero friction
- Desktop/Laptop environment (not mobile optimization needed for MVP)

### Core UX Principles:

#### 1. **Minimize Cognitive Load**
- One question visible at a time (progressive disclosure)
- Clear visual hierarchy (large text, obvious buttons)
- No clutter or unnecessary UI elements
- Auto-focus next field on selection

#### 2. **Forgiving & Flexible**
- Allow editing previous sections anytime
- Show validation errors clearly but not intrusively
- Auto-save form state (restore if browser refreshes)
- Clear error messages with actionable fixes

#### 3. **Speed Over Aesthetics**
- Fast page load (<500ms)
- Instant response to clicks (no loading spinners for conditional logic)
- Keyboard navigation works perfectly (Tab, Enter, Arrow keys)
- Minimal animations (only when helpful, never decorative)

#### 4. **Progressive Disclosure**
- Sections collapse after completion (reduces overwhelm)
- Conditional questions appear smoothly (no jarring jumps)
- Progress indicator always visible (agents know where they are)
- Clear visual distinction between active/completed/upcoming sections

#### 5. **Error Prevention**
- Mandatory fields marked with asterisk (*)
- Real-time validation for format errors (age, height, weight)
- Mutually exclusive checkboxes enforced ("None" disables others)
- Submit button validates completeness before sending

---

## Tech Stack Recommendation

### Frontend: Plain HTML + CSS + JavaScript

**File Structure:**
```
rxmen-discovery-form/
├── index.html          (Main form structure)
├── styles.css          (All styling)
├── script.js           (Form logic, validation, conditional display)
├── api.js              (Claude API integration - Phase 2)
└── README.md           (Setup instructions)
```

**Why This Structure:**
- **Single HTML file:** Entire form in one place, easy to understand
- **Single CSS file:** All styles together, easy to find and modify
- **Single JS file:** All logic in one place for MVP (can split later if needed)
- **Separation of concerns:** Structure (HTML) + Style (CSS) + Behavior (JS)

---

### Detailed Tech Decisions:

#### 1. HTML Structure

**Decision:** Semantic HTML5 with proper form elements

**Why:**
- Native form validation (required, min, max, pattern)
- Accessibility built-in (screen readers work automatically)
- Keyboard navigation works out-of-the-box
- Browser auto-fill works (for name, age, etc.)

**Key Elements:**
```html
<form id="discovery-form" novalidate> <!-- novalidate = custom validation -->
  <section class="form-section" id="section-1">
    <h2>Section 1: Client Information</h2>
    
    <div class="form-question">
      <label for="full-name">Full Name <span class="required">*</span></label>
      <input type="text" id="full-name" name="full_name" required minlength="2">
      <span class="error-message" id="full-name-error"></span>
    </div>
    
    <!-- More questions... -->
  </section>
  
  <!-- More sections... -->
  
  <button type="submit" id="submit-btn">Submit Form</button>
</form>
```

**Best Practices:**
- Use `<fieldset>` for radio button groups
- Use `<legend>` for question text in radio groups
- Every input has a `<label>` (accessibility + clickable area)
- Error messages in `<span>` below each field (announced by screen readers)

---

#### 2. CSS Styling

**Decision:** Custom CSS with design tokens from UI Kit

**Why NOT Bootstrap/Tailwind:**
- ❌ Bootstrap: Too heavy (100KB+ for minimal form styling)
- ❌ Tailwind: Requires build process (defeats our "plain HTML" goal)
- ✅ Custom CSS: Lightweight (<10KB), exactly what you need, full control

**Design System (from RxMen_UI_Kit.pdf):**

```css
/* Design Tokens */
:root {
  /* Colors */
  --brand-blue: #1C5BD9;
  --brand-dark-blue: #072178;
  --brand-neutral: #EFF5FF;
  --black: #121212;
  --gray-1: #40434A;
  --gray-2: #707070;
  --gray-3: #CBCDD0;
  --error-red: #FF0000;
  --success-green: #28A745;
  
  /* Typography - Geist Font */
  --font-family: 'Geist', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-size-h1: 36px;
  --font-size-h2: 32px;
  --font-size-body: 20px;
  --font-size-small: 16px;
  
  /* Spacing */
  --spacing-xs: 8px;
  --spacing-sm: 16px;
  --spacing-md: 32px;
  --spacing-lg: 40px;
  
  /* Layout */
  --form-max-width: 800px;
  --input-height: 48px;
}

/* Base Styles */
body {
  font-family: var(--font-family);
  color: var(--black);
  background: var(--brand-neutral);
  margin: 0;
  padding: 0;
}

.form-container {
  max-width: var(--form-max-width);
  margin: 0 auto;
  padding: var(--spacing-lg);
  background: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* Question Styles */
.form-question {
  margin-bottom: var(--spacing-md);
}

label {
  display: block;
  font-size: var(--font-size-body);
  font-weight: 500;
  margin-bottom: var(--spacing-xs);
  color: var(--black);
}

.required {
  color: var(--error-red);
}

/* Input Styles */
input[type="text"],
input[type="number"],
textarea {
  width: 100%;
  height: var(--input-height);
  padding: 0 var(--spacing-sm);
  border: 1px solid var(--gray-3);
  border-radius: 4px;
  font-size: var(--font-size-small);
  font-family: var(--font-family);
  transition: border-color 0.2s;
}

input:focus,
textarea:focus {
  outline: none;
  border-color: var(--brand-blue);
}

input.error {
  border-color: var(--error-red);
}

/* Radio Button Styles */
.radio-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.radio-option {
  display: flex;
  align-items: center;
  padding: var(--spacing-sm);
  border: 1px solid var(--gray-3);
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s, border-color 0.2s;
}

.radio-option:hover {
  background-color: var(--brand-neutral);
}

.radio-option input[type="radio"] {
  margin-right: var(--spacing-sm);
  width: 20px;
  height: 20px;
  cursor: pointer;
}

.radio-option.selected {
  border-color: var(--brand-blue);
  background-color: var(--brand-neutral);
}

/* Error Messages */
.error-message {
  display: none;
  color: var(--error-red);
  font-size: 14px;
  margin-top: var(--spacing-xs);
}

.error-message.visible {
  display: block;
}

/* Submit Button */
#submit-btn {
  width: 200px;
  height: 56px;
  background-color: var(--brand-blue);
  color: white;
  border: none;
  border-radius: 4px;
  font-size: var(--font-size-small);
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
  display: block;
  margin: var(--spacing-lg) auto 0;
}

#submit-btn:hover {
  background-color: var(--brand-dark-blue);
}

#submit-btn:disabled {
  background-color: var(--gray-3);
  cursor: not-allowed;
}

/* Progress Indicator */
.progress-indicator {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: white;
  padding: var(--spacing-sm);
  border-bottom: 1px solid var(--gray-3);
  z-index: 1000;
}

.progress-bar {
  height: 8px;
  background: var(--gray-3);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--brand-blue);
  transition: width 0.3s ease;
}

/* Section Collapse */
.form-section {
  border: 1px solid var(--gray-3);
  border-radius: 8px;
  padding: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.form-section.collapsed {
  padding: var(--spacing-sm);
  background: var(--brand-neutral);
}

.form-section.collapsed .form-question {
  display: none;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
}

.section-header.completed::after {
  content: '✓';
  color: var(--success-green);
  font-size: 24px;
}
```

**CSS Organization:**
1. Design tokens (CSS variables)
2. Base styles (body, containers)
3. Component styles (questions, inputs, buttons)
4. State styles (hover, focus, error, disabled)
5. Layout styles (sections, progress, collapse)

---

#### 3. JavaScript Logic

**Decision:** Vanilla JavaScript ES6+ (no jQuery, no frameworks)

**Why:**
- Modern browsers support ES6+ (arrow functions, template literals, destructuring)
- No dependencies to manage
- Smaller file size (<20KB for all logic)
- Easier to debug (no framework abstractions)

**Core JavaScript Modules:**

**1. Form State Management**
```javascript
// formState.js - Embedded in script.js

const formState = {
  section1: {
    full_name: '',
    age: null,
    height_cm: null,
    // ... all fields
  },
  section2: { /* ... */ },
  // ... all sections
  
  currentSection: 1,
  completedSections: [],
  
  // Methods
  updateField(section, field, value) {
    this[section][field] = value;
    this.saveToLocalStorage();
  },
  
  saveToLocalStorage() {
    localStorage.setItem('rxmen-form-state', JSON.stringify(this));
  },
  
  loadFromLocalStorage() {
    const saved = localStorage.getItem('rxmen-form-state');
    if (saved) {
      Object.assign(this, JSON.parse(saved));
    }
  },
  
  clearState() {
    localStorage.removeItem('rxmen-form-state');
  }
};
```

**2. Validation Engine**
```javascript
// validation.js - Embedded in script.js

const validators = {
  age: (value) => {
    const age = parseInt(value);
    if (isNaN(age)) return 'Please enter a valid age';
    if (age < 11) return 'Age must be at least 11';
    if (age > 99) return 'Age must be less than 100';
    return null; // No error
  },
  
  height_cm: (value) => {
    const height = parseInt(value);
    if (height < 140 || height > 220) {
      return 'Height must be between 140-220 cm';
    }
    return null;
  },
  
  weight_kg: (value) => {
    const weight = parseFloat(value);
    if (weight < 40 || weight > 200) {
      return 'Weight must be between 40-200 kg';
    }
    return null;
  },
  
  required: (value) => {
    if (!value || value.trim() === '') {
      return 'This field is required';
    }
    return null;
  }
};

function validateField(fieldName, value) {
  const validator = validators[fieldName];
  if (validator) {
    return validator(value);
  }
  return null;
}

function validateSection(sectionNumber) {
  const section = document.querySelector(`#section-${sectionNumber}`);
  const requiredFields = section.querySelectorAll('[required]');
  
  let isValid = true;
  let firstErrorField = null;
  
  requiredFields.forEach(field => {
    const error = validateField(field.name, field.value);
    
    if (error) {
      isValid = false;
      showError(field, error);
      
      if (!firstErrorField) {
        firstErrorField = field;
      }
    } else {
      hideError(field);
    }
  });
  
  if (firstErrorField) {
    scrollToField(firstErrorField);
  }
  
  return isValid;
}

function showError(field, message) {
  field.classList.add('error');
  const errorSpan = document.querySelector(`#${field.id}-error`);
  if (errorSpan) {
    errorSpan.textContent = message;
    errorSpan.classList.add('visible');
  }
}

function hideError(field) {
  field.classList.remove('error');
  const errorSpan = document.querySelector(`#${field.id}-error`);
  if (errorSpan) {
    errorSpan.classList.remove('visible');
  }
}

function scrollToField(field) {
  field.scrollIntoView({ 
    behavior: 'smooth', 
    block: 'center' 
  });
  field.focus();
}
```

**3. Conditional Logic Engine**
```javascript
// conditionalLogic.js - Embedded in script.js

function handleConditionalDisplay() {
  // Section 5: Only show if user has partner
  const relationshipStatus = formState.section1.relationship_status;
  const section5 = document.querySelector('#section-5');
  
  if (relationshipStatus === 'married' || relationshipStatus === 'in_relationship') {
    section5.style.display = 'block';
  } else {
    section5.style.display = 'none';
    formState.section5.partner_response = 'N/A';
  }
  
  // Section 6A: Show if ED selected
  const mainIssue = formState.section2.main_issue;
  const section6A = document.querySelector('#section-6a');
  
  if (mainIssue === 'ed' || mainIssue === 'both') {
    section6A.style.display = 'block';
  } else {
    section6A.style.display = 'none';
  }
  
  // Section 6B: Show if PE selected
  const section6B = document.querySelector('#section-6b');
  
  if (mainIssue === 'pe' || mainIssue === 'both') {
    section6B.style.display = 'block';
  } else {
    section6B.style.display = 'none';
  }
  
  // Q4.2 & Q4.3: Show only if masturbation method != "none"
  const masturbationMethod = formState.section4.masturbation_method;
  const q42 = document.querySelector('#question-4-2');
  const q43 = document.querySelector('#question-4-3');
  
  if (masturbationMethod === 'none') {
    q42.style.display = 'none';
    q43.style.display = 'none';
    formState.section4.masturbation_grip = 'N/A';
    formState.section4.masturbation_frequency = 'N/A';
  } else {
    q42.style.display = 'block';
    q43.style.display = 'block';
    
    // Set default grip to "normal" if not already set
    if (!formState.section4.masturbation_grip) {
      formState.section4.masturbation_grip = 'normal';
      document.querySelector('#grip-normal').checked = true;
    }
  }
  
  // ED Branch: Partner vs Solo pathways
  const edSexualActivity = formState.section6a.ed_sexual_activity_status;
  const partnerPathway = document.querySelector('#ed-partner-pathway');
  const soloPathway = document.querySelector('#ed-solo-pathway');
  
  if (edSexualActivity === 'yes_active' || edSexualActivity === 'avoiding_due_to_fear') {
    partnerPathway.style.display = 'block';
    soloPathway.style.display = 'none';
  } else if (edSexualActivity === 'no_partner') {
    partnerPathway.style.display = 'none';
    soloPathway.style.display = 'block';
  }
  
  // PE Branch: Partner vs Solo pathways
  const peSexualActivity = formState.section6b.pe_sexual_activity_status;
  const pePartnerPathway = document.querySelector('#pe-partner-pathway');
  const peSoloPathway = document.querySelector('#pe-solo-pathway');
  
  if (peSexualActivity === 'yes_active' || peSexualActivity === 'avoiding_due_to_fear') {
    pePartnerPathway.style.display = 'block';
    peSoloPathway.style.display = 'none';
  } else if (peSexualActivity === 'no_partner') {
    pePartnerPathway.style.display = 'none';
    peSoloPathway.style.display = 'block';
  }
  
  // ED Gateway: If "No erections at all", hide all other ED questions
  const edGetsErections = formState.section6a.ed_gets_erections;
  const edQuestions = document.querySelector('#ed-questions-wrapper');
  
  if (edGetsErections === false) {
    edQuestions.style.display = 'none';
    // Set routing flag
    formState.section6a.routing_flags = { andrologist: true, complete_ed: true };
  } else {
    edQuestions.style.display = 'block';
  }
}

// Call this function whenever a relevant field changes
document.addEventListener('change', (e) => {
  handleConditionalDisplay();
});
```

**4. Section Collapse/Expand**
```javascript
// sectionCollapse.js - Embedded in script.js

function initializeSectionCollapse() {
  const sections = document.querySelectorAll('.form-section');
  
  sections.forEach((section, index) => {
    const header = section.querySelector('.section-header');
    
    header.addEventListener('click', () => {
      toggleSection(section, index + 1);
    });
  });
}

function toggleSection(section, sectionNumber) {
  const isCollapsed = section.classList.contains('collapsed');
  
  if (isCollapsed) {
    // Expand
    section.classList.remove('collapsed');
  } else {
    // Collapse
    section.classList.add('collapsed');
  }
}

function markSectionComplete(sectionNumber) {
  const section = document.querySelector(`#section-${sectionNumber}`);
  const header = section.querySelector('.section-header');
  
  header.classList.add('completed');
  formState.completedSections.push(sectionNumber);
  
  // Auto-collapse completed section
  section.classList.add('collapsed');
  
  // Move to next section
  const nextSection = sectionNumber + 1;
  if (nextSection <= 7) {
    scrollToSection(nextSection);
  }
}

function scrollToSection(sectionNumber) {
  const section = document.querySelector(`#section-${sectionNumber}`);
  section.scrollIntoView({ behavior: 'smooth', block: 'start' });
  
  // Expand if collapsed
  section.classList.remove('collapsed');
}
```

**5. Progress Indicator**
```javascript
// progressIndicator.js - Embedded in script.js

function updateProgressIndicator() {
  const totalSections = 7;
  const completedCount = formState.completedSections.length;
  const percentage = Math.round((completedCount / totalSections) * 100);
  
  // Update progress bar
  const progressFill = document.querySelector('.progress-fill');
  progressFill.style.width = `${percentage}%`;
  
  // Update text
  const progressText = document.querySelector('.progress-text');
  progressText.textContent = `Section ${formState.currentSection} of ${totalSections} • ${percentage}% Complete`;
  
  // Update section indicators
  for (let i = 1; i <= totalSections; i++) {
    const indicator = document.querySelector(`#section-indicator-${i}`);
    
    if (formState.completedSections.includes(i)) {
      indicator.classList.add('completed');
      indicator.textContent = '✓';
    } else if (i === formState.currentSection) {
      indicator.classList.add('active');
      indicator.textContent = '▶';
    } else {
      indicator.classList.remove('completed', 'active');
      indicator.textContent = '-';
    }
  }
}

// Call this after each section is completed
document.addEventListener('sectionComplete', (e) => {
  updateProgressIndicator();
});
```

**6. Form Submission**
```javascript
// formSubmission.js - Embedded in script.js

document.querySelector('#submit-btn').addEventListener('click', async (e) => {
  e.preventDefault();
  
  // Validate all sections
  let allValid = true;
  let firstInvalidSection = null;
  
  for (let i = 1; i <= 7; i++) {
    const isValid = validateSection(i);
    
    if (!isValid && !firstInvalidSection) {
      firstInvalidSection = i;
      allValid = false;
    }
  }
  
  if (!allValid) {
    // Scroll to first invalid section
    scrollToSection(firstInvalidSection);
    
    // Show error banner
    showErrorBanner(`Please complete all required fields. Missing: Section ${firstInvalidSection}`);
    return;
  }
  
  // All valid - submit form
  const formData = generateFormJSON();
  
  // Show loading state
  const submitBtn = document.querySelector('#submit-btn');
  submitBtn.disabled = true;
  submitBtn.textContent = 'Submitting...';
  
  try {
    // For MVP: Log to Google Sheets
    await submitToGoogleSheets(formData);
    
    // Show success message
    showSuccessMessage('Form submitted successfully!');
    
    // Clear form state
    formState.clearState();
    
    // Redirect or show next steps
    // window.location.href = '/success';
    
  } catch (error) {
    console.error('Submission error:', error);
    showErrorBanner('Submission failed. Please try again.');
    
    submitBtn.disabled = false;
    submitBtn.textContent = 'Submit Form';
  }
});

function generateFormJSON() {
  return {
    section1_client_info: {
      full_name: formState.section1.full_name,
      age: formState.section1.age,
      height_cm: formState.section1.height_cm,
      weight_kg: formState.section1.weight_kg,
      city: formState.section1.city,
      // ... all section 1 fields
    },
    section2_main_concern: {
      main_issue: formState.section2.main_issue,
      issue_duration: formState.section2.issue_duration,
      issue_context: formState.section2.issue_context,
    },
    // ... all sections
    metadata: {
      form_version: '1.0',
      submission_timestamp: new Date().toISOString(),
      agent_id: 'agent_placeholder', // Will be filled dynamically
    }
  };
}

async function submitToGoogleSheets(formData) {
  // For MVP: Use Google Apps Script Web App or Sheets API
  const GOOGLE_SCRIPT_URL = 'YOUR_GOOGLE_APPS_SCRIPT_URL';
  
  const response = await fetch(GOOGLE_SCRIPT_URL, {
    method: 'POST',
    mode: 'no-cors', // For Google Apps Script
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(formData)
  });
  
  // Since we use no-cors, we can't read the response
  // Assume success if no error thrown
  return true;
}
```

**7. Keyboard Navigation**
```javascript
// keyboardNavigation.js - Embedded in script.js

function initializeKeyboardNavigation() {
  // Enter key: Move to next field
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && e.target.tagName !== 'TEXTAREA') {
      e.preventDefault();
      
      // Find next focusable element
      const focusableElements = Array.from(
        document.querySelectorAll('input:not([disabled]), select:not([disabled]), textarea:not([disabled]), button:not([disabled])')
      );
      
      const currentIndex = focusableElements.indexOf(e.target);
      const nextElement = focusableElements[currentIndex + 1];
      
      if (nextElement) {
        nextElement.focus();
      }
    }
  });
  
  // Arrow keys for radio buttons
  document.querySelectorAll('.radio-group').forEach(group => {
    const radios = group.querySelectorAll('input[type="radio"]');
    
    radios.forEach((radio, index) => {
      radio.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowDown' || e.key === 'ArrowRight') {
          e.preventDefault();
          const nextRadio = radios[(index + 1) % radios.length];
          nextRadio.focus();
          nextRadio.checked = true;
          nextRadio.dispatchEvent(new Event('change', { bubbles: true }));
        }
        
        if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') {
          e.preventDefault();
          const prevRadio = radios[(index - 1 + radios.length) % radios.length];
          prevRadio.focus();
          prevRadio.checked = true;
          prevRadio.dispatchEvent(new Event('change', { bubbles: true }));
        }
      });
    });
  });
}
```

**8. Auto-save**
```javascript
// autoSave.js - Embedded in script.js

let autoSaveTimer;

function setupAutoSave() {
  // Auto-save every 30 seconds
  autoSaveTimer = setInterval(() => {
    formState.saveToLocalStorage();
    showAutoSaveIndicator();
  }, 30000);
  
  // Also save on every input change (debounced)
  document.addEventListener('input', debounce(() => {
    formState.saveToLocalStorage();
  }, 1000));
}

function showAutoSaveIndicator() {
  const indicator = document.querySelector('#autosave-indicator');
  indicator.textContent = 'Saved';
  indicator.style.opacity = '1';
  
  setTimeout(() => {
    indicator.style.opacity = '0';
  }, 2000);
}

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

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
  formState.loadFromLocalStorage();
  setupAutoSave();
});
```

**JavaScript File Size Estimate:**
- Entire `script.js` file: ~15-20KB (minified)
- Loads in <100ms on average connection

---

#### 4. API Integration (Phase 2 - Not MVP)

**Decision:** Separate `api.js` file for Claude API integration

**Phase 2 Implementation:**
```javascript
// api.js - Add this in Phase 2

const CLAUDE_API_URL = 'https://api.anthropic.com/v1/messages';
const CLAUDE_API_KEY = 'YOUR_API_KEY'; // Store securely

async function analyzeFormWithClaude(formData) {
  // 1. Retrieve relevant medical documents from vector DB
  const relevantContext = await searchVectorDB(formData);
  
  // 2. Construct prompt with form data + medical context
  const prompt = constructPrompt(formData, relevantContext);
  
  // 3. Call Claude API
  const response = await fetch(CLAUDE_API_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': CLAUDE_API_KEY,
      'anthropic-version': '2023-06-01'
    },
    body: JSON.stringify({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 2000,
      messages: [
        {
          role: 'user',
          content: prompt
        }
      ]
    })
  });
  
  const data = await response.json();
  
  // 4. Parse AI response (root cause + explanation)
  return parseAIResponse(data.content[0].text);
}

function constructPrompt(formData, medicalContext) {
  return `You are an expert sexual health diagnostician. Analyze the following patient data and provide:
1. Primary root cause
2. Secondary root cause (if applicable)
3. Simple explanation in Hinglish

MEDICAL CONTEXT:
${medicalContext}

PATIENT DATA:
${JSON.stringify(formData, null, 2)}

Provide your analysis in this format:
PRIMARY: [Root cause name]
SECONDARY: [Root cause name or "None"]
EXPLANATION: [Simple Hinglish explanation for agent to read to patient]
DOCTOR: [Sexologist/Andrologist/Venerologist]`;
}
```

---

### Hosting & Deployment

**Decision:** Netlify (Free Tier)

**Why Netlify:**
- ✅ Free for MVP (generous free tier)
- ✅ Drag-and-drop deployment (literally drag folder to browser)
- ✅ Instant HTTPS (automatic SSL certificate)
- ✅ Custom domain support (rxmen.app or similar)
- ✅ Form submissions (can use Netlify Forms API for MVP logging)
- ✅ Instant rollback (if something breaks, revert in 1 click)
- ✅ Fast CDN (global edge network)

**Deployment Process:**
1. Create Netlify account (free)
2. Drag `rxmen-discovery-form` folder to Netlify dashboard
3. Get instant URL: `https://rxmen-discovery-form.netlify.app`
4. Share with agents immediately

**Alternative (if needed):** GitHub Pages, Vercel, or any static hosting

---

### Development Tools

**Recommended:**
- **Code Editor:** VS Code (free)
- **VS Code Extensions:**
  - Live Server (instant preview)
  - Prettier (code formatting)
  - ESLint (JavaScript linting)
- **Browser:** Chrome/Firefox with DevTools
- **Testing:** Manual testing initially, automated tests in Phase 2

**No Build Tools Needed:**
- No npm, webpack, babel, or any build process
- Just edit files and refresh browser
- Instant feedback loop

---

## Implementation Architecture

### File Organization

```
rxmen-discovery-form/
│
├── index.html              (3,000-5,000 lines - entire form structure)
│   ├── Header (logo, progress)
│   ├── Section 1: Client Information
│   ├── Section 2: Main Concern
│   ├── Section 3: Medical & Lifestyle
│   ├── Section 4: Masturbation History
│   ├── Section 5: Relationship Dynamics
│   ├── Section 6A: ED Branch
│   ├── Section 6B: PE Branch
│   ├── Section 7: Other Information
│   └── Submit Button
│
├── styles.css              (1,000-1,500 lines - all styling)
│   ├── Design Tokens
│   ├── Base Styles
│   ├── Component Styles
│   ├── State Styles
│   └── Responsive Styles (future)
│
├── script.js               (1,500-2,000 lines - all logic)
│   ├── Form State Management
│   ├── Validation Engine
│   ├── Conditional Logic
│   ├── Section Collapse
│   ├── Progress Indicator
│   ├── Form Submission
│   ├── Keyboard Navigation
│   └── Auto-save
│
├── api.js                  (Phase 2 - Claude integration)
│
├── README.md               (Setup instructions)
│
└── assets/
    └── logo.svg            (RxMen logo)
```

**Total Code Size:** ~6,000-8,500 lines (very manageable for MVP)

---

### Data Flow

```
User Input
    â†"
HTML Form Element
    â†"
JavaScript Event Listener (change/input)
    â†"
Update formState Object
    â†"
├─→ Save to localStorage (auto-save)
├─→ Run Validation (real-time)
├─→ Update Conditional Display (show/hide sections)
└─→ Update Progress Indicator
    â†"
Submit Button Clicked
    â†"
Validate All Sections
    â†"
├─ Invalid → Scroll to Error, Show Message
└─ Valid → Generate JSON → Submit to Google Sheets
           â†"
       Success/Error Feedback
```

---

## Development Roadmap

### Day 1: HTML Structure (6-8 hours)

**Goal:** Complete HTML form with all 7 sections

**Tasks:**
1. Create `index.html` skeleton
2. Add header with logo and progress indicator
3. Build Section 1: Client Information (9 questions)
4. Build Section 2: Main Concern (3 questions)
5. Build Section 3: Medical & Lifestyle (7 questions)
6. Build Section 4: Masturbation History (4 questions)
7. Build Section 5: Relationship Dynamics (1 question)
8. Build Section 6A: ED Branch (10 questions with pathways)
9. Build Section 6B: PE Branch (9 questions with pathways)
10. Build Section 7: Other Information (1 textarea)
11. Add Submit Button

**Deliverable:** Complete HTML form (no styling, no logic - just structure)

**Testing:** Open in browser, verify all questions visible

---

### Day 2: CSS Styling (6-8 hours)

**Goal:** Style form to match RxMen UI Kit

**Tasks:**
1. Add design tokens (CSS variables)
2. Style base elements (body, containers, typography)
3. Style form questions (labels, inputs, radio buttons, checkboxes)
4. Style error states (red borders, error messages)
5. Style progress indicator (fixed header, progress bar)
6. Style section collapse (collapsible sections, checkmarks)
7. Style submit button (primary button, hover states)
8. Add responsive padding and spacing
9. Test cross-browser compatibility

**Deliverable:** Fully styled form matching RxMen brand

**Testing:** Visual review, compare with UI Kit PDF

---

### Day 3: JavaScript - Validation (4-6 hours)

**Goal:** Implement real-time validation for all fields

**Tasks:**
1. Create validation engine (validators object)
2. Add real-time validation (input/change events)
3. Add submit validation (validate all sections)
4. Implement error display (showError/hideError functions)
5. Implement scroll-to-error (scrollToField function)
6. Add age validation (11-99 range)
7. Add height validation (140-220 cm range)
8. Add weight validation (40-200 kg range)
9. Add required field validation
10. Test all validation rules

**Deliverable:** Working validation system

**Testing:** Try invalid inputs, verify error messages

---

### Day 4: JavaScript - Conditional Logic (4-6 hours)

**Goal:** Implement show/hide logic for all conditional questions

**Tasks:**
1. Section 5 conditional display (show if has partner)
2. Section 6A conditional display (show if ED selected)
3. Section 6B conditional display (show if PE selected)
4. Q4.2/Q4.3 conditional display (show if masturbation method != none)
5. ED Partner/Solo pathway logic
6. PE Partner/Solo pathway logic
7. ED gateway question logic (if no erections, hide all other ED questions)
8. Test all conditional paths

**Deliverable:** Working conditional logic

**Testing:** Change answers, verify correct sections show/hide

---

### Day 5: JavaScript - UI Enhancements (4-6 hours)

**Goal:** Add section collapse, progress indicator, keyboard navigation

**Tasks:**
1. Implement section collapse/expand (click header to toggle)
2. Mark sections as complete (green checkmark)
3. Build progress indicator (update on section complete)
4. Add keyboard navigation (Tab, Enter, Arrow keys)
5. Add auto-save to localStorage
6. Add restore form state on page load
7. Test all UI interactions

**Deliverable:** Polished user experience

**Testing:** Fill form partially, refresh page, verify state restored

---

### Day 6: JavaScript - Form Submission (3-4 hours)

**Goal:** Implement form submission to Google Sheets

**Tasks:**
1. Create formState to JSON conversion
2. Set up Google Apps Script for Sheets API
3. Implement submitToGoogleSheets function
4. Add loading state (disable button, show spinner)
5. Add success message
6. Add error handling
7. Test submission flow

**Deliverable:** Working form submission

**Testing:** Submit form, verify data appears in Google Sheets

---

### Day 7: Testing & Deployment (4-6 hours)

**Goal:** Test all functionality and deploy to production

**Tasks:**
1. Test all 7 sections individually
2. Test conditional logic (all pathways)
3. Test validation (all error cases)
4. Test form submission (success/error)
5. Test keyboard navigation
6. Test auto-save/restore
7. Bug fixes
8. Deploy to Netlify
9. Share URL with stakeholders

**Deliverable:** Live production form

**Testing:** End-to-end testing with real scenarios

---

## Deployment Strategy

### Step-by-Step Deployment

**1. Prepare Files**
```
rxmen-discovery-form/
├── index.html
├── styles.css
├── script.js
└── assets/
    └── logo.svg
```

**2. Deploy to Netlify**
- Go to https://www.netlify.com
- Sign up (free)
- Click "Add new site" → "Deploy manually"
- Drag `rxmen-discovery-form` folder to browser
- Wait 30 seconds
- Get URL: `https://your-site-name.netlify.app`

**3. Configure Custom Domain (Optional)**
- Buy domain: `rxmen-form.com` (optional)
- In Netlify: Settings → Domain management → Add custom domain
- Update DNS records (Netlify provides instructions)
- Automatic HTTPS enabled

**4. Share with Agents**
- Send URL to agents
- Provide brief training (5-minute walkthrough)
- Monitor submissions in Google Sheets

---

### Monitoring & Analytics

**For MVP:**
- Google Sheets logs all submissions (timestamp, agent ID, form data)
- Manual review of submission data
- Agent feedback collection

**Phase 2:**
- Add Google Analytics (track form abandonment, time per section)
- Add error logging (Sentry or similar)
- Add performance monitoring

---

## Testing & Quality Assurance

### Manual Testing Checklist

**Section 1: Client Information**
- [ ] Name accepts 2+ characters
- [ ] Age validates 11-99 range
- [ ] Age < 11 shows error "Age must be at least 11"
- [ ] Age > 99 shows error "Age must be less than 100"
- [ ] Age < 18 triggers red flag (form should not proceed)
- [ ] Height cm validates 140-220 range
- [ ] Height ft-in validates feet 4-7, inches 0-11
- [ ] Weight validates 40-200 kg range
- [ ] City accepts 3+ characters
- [ ] Occupation radio buttons work
- [ ] Relationship status radio buttons work
- [ ] First consultation question works
- [ ] Previous treatments checkboxes work (only if "No" selected)
- [ ] Red flags question works

**Section 2: Main Concern**
- [ ] Main issue radio buttons work
- [ ] Main issue selection determines Section 6 display
- [ ] Duration radio buttons work
- [ ] Context radio buttons work

**Section 3: Medical & Lifestyle**
- [ ] Medical conditions checkboxes work
- [ ] "None" is mutually exclusive with other options
- [ ] "Other" text field appears when "Other" checked
- [ ] Current medications checkboxes work
- [ ] "None" is mutually exclusive with other options
- [ ] Blood thinners triggers red flag warning
- [ ] Surgery question works
- [ ] Alcohol frequency radio buttons work
- [ ] Smoking frequency radio buttons work
- [ ] Sleep quality radio buttons work
- [ ] Physical activity radio buttons work

**Section 4: Masturbation History**
- [ ] Masturbation method radio buttons work
- [ ] Q4.2 & Q4.3 hidden if "No masturbation" selected
- [ ] Q4.2 & Q4.3 visible if any other option selected
- [ ] Grip type defaults to "Normal" when shown
- [ ] Masturbation frequency radio buttons work
- [ ] Porn frequency always visible

**Section 5: Relationship Dynamics**
- [ ] Only shows if relationship status = Married or In a relationship
- [ ] Hidden if Single or Divorced/Widowed
- [ ] Partner response radio buttons work

**Section 6A: ED Branch**
- [ ] Only shows if main issue = ED or Both
- [ ] Hidden if main issue = PE only
- [ ] Gateway question works
- [ ] If "No" selected, all other ED questions hidden
- [ ] If "No" selected, andrologist routing flag set
- [ ] If "Yes" selected, Q6A.2 shows
- [ ] Q6A.2 determines Partner vs Solo pathway
- [ ] Partner pathway questions (Q6A.3-Q6A.7) work
- [ ] Solo pathway questions (Q6A.8-Q6A.10) work
- [ ] All radio buttons in branch work

**Section 6B: PE Branch**
- [ ] Only shows if main issue = PE or Both
- [ ] Hidden if main issue = ED only
- [ ] Q6B.1 determines Partner vs Solo pathway
- [ ] Partner pathway questions (Q6B.2-Q6B.5) work
- [ ] Solo pathway questions (Q6B.6-Q6B.9) work
- [ ] All radio buttons in branch work

**Section 7: Other Information**
- [ ] Textarea accepts up to 1000 characters
- [ ] Character counter works
- [ ] Field is optional (can be empty)

**Validation & Error Handling**
- [ ] All required fields marked with red asterisk (*)
- [ ] Real-time validation shows errors as user types
- [ ] Submit validation checks all sections
- [ ] Submit scrolls to first incomplete question
- [ ] Error messages clear when field becomes valid
- [ ] Submit button disabled during submission
- [ ] Submit button shows "Submitting..." text

**UI/UX**
- [ ] Progress indicator updates correctly
- [ ] Progress bar fills as sections completed
- [ ] Sections collapse after completion
- [ ] Collapsed sections show green checkmark
- [ ] Sections expand when clicked
- [ ] Keyboard navigation works (Tab, Enter, Arrows)
- [ ] Auto-save works (refresh page, state restored)

**Form Submission**
- [ ] Form submits to Google Sheets
- [ ] Success message shows after submission
- [ ] Form clears after successful submission
- [ ] Error handling works if submission fails

---

### Browser Compatibility

**Must Work In:**
- ✅ Chrome 90+ (primary)
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

**Desktop Only (for MVP):**
- No mobile optimization needed initially
- Desktop/Laptop agents only

---

## Potential Issues & Solutions

### Issue 1: Form Too Long (Overwhelming)

**Problem:** 60+ questions, agent might feel overwhelmed

**Solutions:**
- ✅ Section collapse after completion (reduces visual clutter)
- ✅ Progress indicator (shows clear progress)
- ✅ Auto-save (agent can take breaks)
- ✅ Keyboard shortcuts (faster navigation)

---

### Issue 2: Conditional Logic Bugs

**Problem:** Wrong questions showing/hiding

**Solutions:**
- ✅ Thorough testing of all conditional paths
- ✅ Clear console logging (for debugging)
- ✅ Manual testing checklist (test every scenario)
- ✅ Agent feedback loop (report bugs immediately)

---

### Issue 3: Form Submission Failures

**Problem:** Network errors, API failures

**Solutions:**
- ✅ Retry logic (try 3 times before failing)
- ✅ Save form data locally before submission
- ✅ Show clear error message with "Try Again" button
- ✅ Manual submission option (copy JSON, send via email)

---

### Issue 4: Agent Forgets to Fill Fields

**Problem:** Required fields missed

**Solutions:**
- ✅ Red asterisk on all required fields
- ✅ Submit validation (catches missing fields)
- ✅ Scroll to first error (agent sees what's missing)
- ✅ Error message lists missing section

---

### Issue 5: Performance Issues

**Problem:** Form loads slowly or lags

**Solutions:**
- ✅ Minimize JavaScript file size (keep under 20KB)
- ✅ Minimize CSS file size (keep under 10KB)
- ✅ Lazy load conditional sections (only render when needed)
- ✅ Debounce validation (don't validate on every keystroke)

---

### Issue 6: Agent Accidentally Closes Browser

**Problem:** Loses all progress

**Solutions:**
- ✅ Auto-save to localStorage every 30 seconds
- ✅ Auto-restore on page reload
- ✅ Warning before closing (if form has data)

```javascript
window.addEventListener('beforeunload', (e) => {
  if (formHasData()) {
    e.preventDefault();
    e.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
  }
});
```

---

### Issue 7: Red Flag Ignored

**Problem:** Agent proceeds despite red flag

**Solutions:**
- ✅ Red flag questions prominently styled (orange background)
- ✅ Red flag warning in AI output (not inline)
- ✅ Training for agents on red flag protocol
- ✅ Supervisor review of red flag cases

---

### Issue 8: Google Sheets Rate Limits

**Problem:** Too many submissions overwhelm Sheets API

**Solutions:**
- ✅ Use Google Apps Script (higher rate limits)
- ✅ Queue submissions if rate limit hit
- ✅ Phase 2: Move to proper database (PostgreSQL)

---

### Issue 9: Agent Confusion on Conditional Questions

**Problem:** Agent doesn't understand why questions appear/disappear

**Solutions:**
- ✅ Agent training (explain conditional logic)
- ✅ Smooth animations (not jarring show/hide)
- ✅ Visual indication (gray out hidden sections)
- ✅ Help tooltips (optional, if needed)

---

### Issue 10: Form Data Privacy

**Problem:** Sensitive medical data in browser localStorage

**Solutions:**
- ✅ Clear localStorage after submission
- ✅ Warn agent not to use shared computers
- ✅ Phase 2: Server-side encryption
- ✅ Phase 2: Session-based storage (not localStorage)

---

## Summary & Next Steps

### Tech Stack Decision: ✅ **Plain HTML + CSS + JavaScript**

**Why:**
- Fastest to build (15-day MVP timeline)
- Easiest to iterate (no build process)
- Lightest weight (fast page load)
- Most maintainable (anyone can modify)
- Perfect for simple form with conditional logic

**Not:**
- React (overkill, slower to iterate)
- jQuery (unnecessary, adds bloat)
- Bootstrap/Tailwind (requires build process)

---

### Immediate Next Steps:

**Day 1 (Today):**
1. ✅ Read this document thoroughly
2. ✅ Set up project folder structure
3. ✅ Create `index.html` skeleton
4. ✅ Build Section 1 HTML (9 questions)
5. ✅ Build Section 2 HTML (3 questions)

**Day 2:**
1. Complete remaining sections (3-7)
2. Add CSS styling (match UI Kit)
3. Test visual appearance

**Day 3-5:**
1. Add JavaScript validation
2. Add conditional logic
3. Add UI enhancements

**Day 6-7:**
1. Add form submission
2. Deploy to Netlify
3. Test end-to-end
4. Share with agents

---

### Resources for Development

**Reference Documents:**
1. `RxMen_Discovery_Call_Form_Complete_Specification.md` - Detailed form requirements
2. `RxMen_UI_Kit.pdf` - Design system (colors, fonts, spacing)
3. This document - Technical implementation guidance

**External Resources:**
- MDN Web Docs: https://developer.mozilla.org (HTML/CSS/JS reference)
- Can I Use: https://caniuse.com (browser compatibility)
- Netlify Docs: https://docs.netlify.com (deployment)

---

### Questions to Answer Before Starting:

1. **Google Sheets Setup:** Do you have a Google Sheet ready for form submissions?
2. **Logo:** Do you have the RxMen logo file (SVG or PNG)?
3. **Domain:** Do you want a custom domain or use Netlify subdomain?
4. **Agent IDs:** How will agents identify themselves (login system or manual entry)?

---

**END OF DOCUMENT**

---

**Document Version:** 1.0  
**Last Updated:** November 6, 2025  
**Status:** Ready for Development  
**Next Steps:** Begin Day 1 - HTML Structure Development

---

## Quick Start Command

```bash
# Create project folder
mkdir rxmen-discovery-form
cd rxmen-discovery-form

# Create files
touch index.html styles.css script.js README.md

# Create assets folder
mkdir assets

# Open in VS Code
code .

# Install Live Server extension in VS Code
# Right-click index.html → Open with Live Server
# Start building!
```

**You're ready to start frontend development! 🚀**
