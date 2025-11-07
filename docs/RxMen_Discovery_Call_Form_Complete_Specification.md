# RxMen Discovery Call Form - Complete Specification

**Version:** 1.0  
**Date:** November 6, 2025  
**Status:** Finalized for Development  
**Purpose:** AI-powered root cause analysis form for ED/PE discovery calls

---

## Table of Contents

1. [Document Overview](#document-overview)
2. [Form Architecture](#form-architecture)
3. [Validation & Error Handling](#validation--error-handling)
4. [UI/UX Interaction Patterns](#uiux-interaction-patterns)
5. [Section 1: Client Information](#section-1-client-information)
6. [Section 2: Main Concern](#section-2-main-concern)
7. [Section 3: Medical & Lifestyle](#section-3-medical--lifestyle)
8. [Section 4: Masturbation & Behavioral History](#section-4-masturbation--behavioral-history)
9. [Section 5: Relationship Dynamics](#section-5-relationship-dynamics)
10. [Section 6A: ED Branch](#section-6a-ed-branch)
11. [Section 6B: PE Branch](#section-6b-pe-branch)
12. [Section 7: Other Information](#section-7-other-information-open-box)
13. [Data Structure Reference](#data-structure-reference)
14. [Red Flag Logic](#red-flag-logic)
15. [Agent Training Notes](#agent-training-notes)

---

## Document Overview

### Purpose
This document specifies the complete structure, logic, and implementation details for the RxMen Discovery Call Form - a web-based tool that agents use during live video calls to collect patient information for AI-powered root cause analysis of erectile dysfunction (ED) and premature ejaculation (PE).

### Key Principles
- **Simplicity First:** Questions designed for agents to fill during live video calls (high cognitive load context)
- **Elimination Logic:** Questions ordered to quickly narrow down root causes
- **Medical Accuracy:** All questions validated against ED/PE training modules
- **Conditional Display:** Questions adapt based on previous answers
- **No Repetition:** Each diagnostic element asked only once

### Technical Stack
- **Frontend:** HTML + CSS + JavaScript (simple, fast, browser-based)
- **UI Components:** Radio buttons, checkboxes, text inputs, number inputs
- **Validation:** Client-side validation for all required fields
- **Data Output:** JSON structure for AI processing

---

## Form Architecture

### Overall Flow

```
Section 1: Client Information (9 questions)
    â†“
Section 2: Main Concern (3 questions)
    â†’ Determines: ED only | PE only | Both
    â†“
Section 3: Medical & Lifestyle (7 questions)
    â†“
Section 4: Masturbation History (4 questions)
    â†“
Section 5: Relationship Dynamics (1 question - conditional)
    â†“
Section 6: Branch Logic
    â”œâ”€ If ED selected â†’ Section 6A: ED Branch
    â”œâ”€ If PE selected â†’ Section 6B: PE Branch
    â””â”€ If Both â†’ Section 6A + Section 6B
    â†“
[Section 7: Open Box - Not in MVP]
```

### Conditional Display Rules
1. Section 5 (Relationship question) only shows if Section 1.7 = "Married" or "In a relationship"
2. Section 6A (ED Branch) shows if Section 2.1 = "ED" or "Both"
3. Section 6B (PE Branch) shows if Section 2.1 = "PE" or "Both"
4. Within branches, questions adapt based on sexual activity status

---

## Validation & Error Handling

### Mandatory Field System

**Visual Indicator:**
- All required questions have a red asterisk (*) next to the question text
- Example: "Age *" or "What is the main issue? *"
- Asterisk color: Red (#FF0000)
- Placement: Immediately after question text, before any helper text

**Validation Timing:**
- **Real-time validation:** As user fills/selects (for format errors)
- **Submit validation:** When user clicks "Submit" button (for completeness)

---

### Error States & Messages

**Invalid Input Errors (Real-time):**

1. **Age Field:**
   - If value < 11 or > 99: Show error below field
   - Error message: "âš ï¸ Age must be between 11 and 99"
   - Border color changes to red
   - Value is NOT accepted (cannot proceed)
   - Error clears when valid value entered

2. **Height Field:**
   - If cm < 140 or > 220: "âš ï¸ Height must be between 140-220 cm"
   - If feet < 4 or > 7: "âš ï¸ Feet must be between 4-7"
   - If inches < 0 or > 11: "âš ï¸ Inches must be between 0-11"

3. **Weight Field:**
   - If value < 40 or > 200: "âš ï¸ Weight must be between 40-200 kg"

4. **Text Fields (Name, City):**
   - If length < minimum: "âš ï¸ Please enter at least [X] characters"
   - Example: Name < 2 chars: "âš ï¸ Please enter at least 2 characters"

5. **Text Field with "Other" Option:**
   - If "Other" checkbox selected but text field empty: "âš ï¸ Please specify"
   - Border turns red until filled

**Error Visual Design:**
```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ Age *                               â”‚
â”‚ â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â” â”‚
â”‚ â”‚ 10                              â”‚ â”‚ â† Red border
â”‚ â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜ â”‚
â”‚ âš ï¸ Age must be between 11 and 99   â”‚ â† Red text, warning icon
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

### Submit Button Behavior

**Normal State:**
- Text: "Submit Form"
- Color: Brand Blue (#1C5BD9)
- Position: Bottom of form, centered
- Width: 200px
- Font: Bold, 16px

**On Click - Validation Check:**

1. **If form is complete and valid:**
   - Button shows loading state: "Submitting..."
   - Spinner icon appears
   - Form data sent to backend
   - Success message shown (or redirect to results page)

2. **If form is incomplete:**
   - Form does NOT submit
   - Scroll to FIRST incomplete/invalid question
   - Highlight the incomplete section with yellow background
   - Show error message at top of screen:
     ```
     âš ï¸ Please complete all required fields
     Missing: [Section Name] - [Question]
     ```
   - Example: "âš ï¸ Please complete all required fields. Missing: Client Information - Age"

3. **If form has validation errors:**
   - Scroll to FIRST question with validation error
   - Show error message below that question
   - Highlight field with red border
   - Top banner: "âš ï¸ Please fix errors before submitting"

**Scroll Behavior:**
- Smooth scroll animation (300ms)
- Scroll to position 100px above the question (so it's clearly visible)
- Question section expands if collapsed
- Focus automatically placed on the error field

**Error Summary (Optional Enhancement):**
- Small banner at top listing all incomplete sections
- Clickable links to jump to each error
- Example:
  ```
  âš ï¸ 3 fields need attention:
  â†’ Section 1: Age (invalid)
  â†’ Section 3: Current Medications (required)
  â†’ Section 6: Erection quality (required)
  ```

---

### Field-Specific Validation Rules

**Radio Buttons:**
- Must select exactly one option
- If not selected on submit: Red border around entire option group
- Error: "âš ï¸ Please select an option"

**Checkboxes:**
- Must select at least one (if required)
- If "None" is selected, all others disabled (mutually exclusive)
- If any other selected, "None" disabled
- Error: "âš ï¸ Please select at least one option"

**Text Input:**
- Trim whitespace before validation
- Check minimum/maximum character count
- For "Other" fields: Check if parent checkbox selected

**Number Input:**
- Only accept numeric values (0-9)
- Decimal allowed for Weight (1 decimal place max)
- No negative numbers
- Check min/max range in real-time

**Conditional Fields:**
- If parent answer changes and makes child fields invalid, clear child fields
- Example: Change Q4.1 from "Using hands" to "No masturbation" â†’ Clear Q4.2 and Q4.3

---

### Save/Progress Behavior

**Auto-save (Optional for MVP):**
- Save form state to localStorage every 30 seconds
- Restore form if agent refreshes page
- Show small "Saved" indicator when auto-save completes

**Manual Save (Not in MVP):**
- "Save Draft" button separate from "Submit"
- Allows partial completion

---

## UI/UX Interaction Patterns

### Overall Form Layout

**Desktop/Laptop Design (Primary):**
- Single column layout
- Maximum width: 800px (centered on screen)
- White background with subtle shadow
- Padding: 40px on all sides
- Sections clearly separated with horizontal dividers

**Visual Hierarchy:**
```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  RxMen Logo            Discovery Call   â”‚ â† Header (fixed)
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  Progress: Section 2 of 7              â”‚ â† Progress indicator
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                                        â”‚
â”‚  [Section Title]                       â”‚ â† Large, bold
â”‚                                        â”‚
â”‚  Question 1 *                          â”‚ â† Medium, semibold
â”‚  â—‹ Option 1                            â”‚
â”‚  â—‹ Option 2                            â”‚
â”‚                                        â”‚
â”‚  Question 2 *                          â”‚
â”‚  [Text input field]                    â”‚
â”‚                                        â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  [Next Section]                        â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

### Section Collapse Behavior

**Completed Sections:**
- After agent completes a section and moves to next, previous section collapses
- Shows only section title + green checkmark
- Click to expand and edit if needed
- Collapsed state shows summary: "Section 1: Client Information âœ“ (9 answers)"

**Current Section:**
- Expanded, with blue left border highlight
- All questions visible
- Active state

**Future Sections:**
- Collapsed by default
- Gray text
- Not clickable until current section complete (unless allowing navigation)

**Visual Example:**
```
âœ“ Section 1: Client Information (9 answers)     [Click to edit]
âœ“ Section 2: Main Concern (3 answers)            [Click to edit]
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
â–¶ Section 3: Medical & Lifestyle                 [Current]
  
  Question 3.1: Do you have any chronic medical conditions? *
  â˜ None
  â˜ Diabetes
  ...
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
  Section 4: Masturbation History                [Locked]
  Section 5: Relationship Dynamics               [Locked]
```

---

### Progress Indicator

**Position:** Fixed at top of page, always visible

**Design:**
- Visual progress bar (colored sections)
- Text: "Section [X] of 7: [Section Name]"
- Percentage: "[X]% Complete"

**Visual:**
```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ Section 3 of 7: Medical & Lifestyle  â€¢  43% Complete â”‚
â”‚ â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘   â”‚
â”‚ âœ“  âœ“  â–¶  -  -  -  -                              â”‚
â”‚ S1 S2 S3 S4 S5 S6 S7                              â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

### Question Display Patterns

**Radio Buttons:**
- Vertical list (one option per line)
- Adequate spacing between options (16px)
- Full-width clickable area (not just circle)
- Hover state: Light blue background (#EFF5FF)
- Selected state: Blue circle, blue text, blue border

**Checkboxes:**
- Vertical list
- "None" option always first (if present)
- Mutually exclusive behavior clearly communicated
- Gray out disabled options (when "None" selected)

**Text Input:**
- Full width (within 800px container)
- Height: 48px (single line)
- Border: 1px solid #CBCDD0 (Gray 3)
- Focus: Blue border (#1C5BD9)
- Placeholder text in gray

**Textarea (Section 7):**
- Full width
- Height: 120px (multi-line)
- Character counter bottom-right: "0/1000"
- Placeholder: "Type here..."

**Number Input:**
- Width: 200px (not full width)
- Shows number keyboard on mobile
- Up/down arrows visible
- Min/max enforced

**Toggle (Height cm/ft-in):**
- Two buttons side by side
- Active: Blue background, white text
- Inactive: White background, gray text
- Smooth transition animation

---

### Conditional Display Animations

**Show Question:**
- Fade in + slide down animation (200ms)
- Smooth, not jarring

**Hide Question:**
- Fade out + slide up animation (200ms)
- Removed from DOM after animation

**Expand Dropdown (e.g., Q4.2, Q4.3):**
- Click parent question to expand
- Arrow icon rotates down
- Child questions slide in below
- Indented slightly (20px) to show hierarchy

---

### Keyboard Navigation

**Tab Order:**
- Logical top-to-bottom flow
- Skip hidden/collapsed sections
- Focus visible (blue outline)

**Enter Key:**
- In text field: Move to next question
- On radio/checkbox: Select option and move next
- On submit button: Submit form

**Escape Key:**
- Clear current field
- Or collapse expanded section (if supported)

---

### Loading States

**Form Loading (Initial):**
- Skeleton screen with gray placeholder boxes
- "Loading form..." text
- Fast (should load in <500ms)

**Submit Loading:**
- Button text changes to "Submitting..."
- Spinner icon
- Disable all form fields (prevent edits)
- Full-screen overlay with "Processing..." message
- Takes 2-3 seconds for AI processing

---

### Mobile Responsiveness (Future, Not MVP)

**Considerations for later:**
- Stack fields vertically
- Larger touch targets (56px minimum)
- Simplified progress indicator
- Sticky header with progress
- One question visible at a time

---

### Accessibility (Basic MVP Requirements)

**Must Have:**
- All fields have proper `<label>` tags
- Required fields marked with aria-required="true"
- Error messages associated with fields (aria-describedby)
- Focus states visible
- Color contrast ratios meet WCAG AA (4.5:1 minimum)
- Keyboard navigable

**Screen Reader Support:**
- Announce errors when validation fails
- Progress updates announced
- Section changes announced

---

### Visual Design Tokens (From UI Kit)

**Colors:**
- Brand Blue: #1C5BD9
- Brand Dark Blue: #072178
- Brand Neutral: #EFF5FF
- Black: #121212
- Gray 1: #40434A
- Gray 2: #707070
- Gray 3: #CBCDD0
- Error Red: #FF0000
- Success Green: #28A745
- Warning Orange: #FF9800

**Typography (Geist Font):**
- Section Titles: H1 (36px, SemiBold)
- Question Text: H2 (20px, Medium)
- Options/Body: B1 (16px, Regular)
- Helper Text: B2 (14px, Regular)
- Error Text: C1 (14px, Medium, Red)

**Spacing:**
- Section padding: 40px
- Question spacing: 32px
- Option spacing: 16px
- Button padding: 16px 32px

---

## Conditional Display Rules
1. Section 5 (Relationship question) only shows if Section 1.7 = "Married" or "In a relationship"
2. Section 6A (ED Branch) shows if Section 2.1 = "ED" or "Both"
3. Section 6B (PE Branch) shows if Section 2.1 = "PE" or "Both"
4. Within branches, questions adapt based on sexual activity status

---

## Section 1: Client Information

**Purpose:** Capture demographic and basic health screening data

---

### Question 1.1: Full Name

**Question Text:** Full Name

**UI Component:** Text input (single line)

**Validation:**
- Required: Yes
- Minimum length: 2 characters
- Maximum length: 100 characters

**Backend Field:** `full_name`

**Data Type:** String

---

### Question 1.2: Age

**Question Text:** Age

**UI Component:** Number input

**Validation:**
- Required: Yes
- Minimum: 11
- Maximum: 99
- Type: Integer only

**Backend Field:** `age`

**Data Type:** Integer

**Red Flag Logic:**
- If age < 18: **STOP CALL** - Display: "Cannot proceed - patient is a minor. Decline and document."
- If age > 80: **FLAG** - Display: "In-person consultation required"

---

### Question 1.3: Height

**Question Text:** Height

**UI Component:** Toggle switch (cm / ft-in) + Number inputs

**Options:**
- **Metric:** Single input (cm)
  - Range: 140-220 cm
- **Imperial:** Two inputs (feet + inches)
  - Feet range: 4-7
  - Inches range: 0-11

**Validation:**
- Required: Yes
- Must select measurement system
- Must be within valid ranges

**Backend Fields:**
- `height_cm` (Integer) - Always store in cm regardless of input method
- `height_input_method` (String: "metric" | "imperial")
- `height_original_value` (String) - Store original input for reference

**Conversion Logic:**
- If imperial input: Convert to cm using: `cm = (feet Ã— 30.48) + (inches Ã— 2.54)`

---

### Question 1.4: Weight

**Question Text:** Weight (kg)

**UI Component:** Number input

**Validation:**
- Required: Yes
- Minimum: 40 kg
- Maximum: 200 kg
- Type: Integer or decimal (1 decimal place)

**Backend Field:** `weight_kg`

**Data Type:** Float

**Calculated Field:** BMI = weight_kg / (height_cm/100)Â²

---

### Question 1.5: City

**Question Text:** City

**UI Component:** Text input (single line)

**Validation:**
- Required: Yes
- Minimum length: 3 characters
- Maximum length: 50 characters

**Backend Field:** `city`

**Data Type:** String

**Future Enhancement:** Type-ahead dropdown with Indian cities

---

### Question 1.6: Occupation

**Question Text:** User's occupation

**UI Component:** Radio buttons (vertical list)

**Options:**
1. â—‹ Corporate Employee
2. â—‹ Business Owner / Self-employed
3. â—‹ Freelancer
4. â—‹ Student
5. â—‹ Retired
6. â—‹ Unemployed

**Validation:**
- Required: Yes
- Single selection only

**Backend Field:** `occupation`

**Data Type:** String (enum)

**Possible Values:** `"corporate"` | `"business_owner"` | `"freelancer"` | `"student"` | `"retired"` | `"unemployed"`

**Design Note:** No "Other" option - 6 categories are comprehensive for male population

---

### Question 1.7: Relationship Status

**Question Text:** User's relationship status

**UI Component:** Radio buttons (vertical list)

**Options:**
1. â—‹ Married
2. â—‹ In a relationship
3. â—‹ Single
4. â—‹ Divorced / Widowed

**Validation:**
- Required: Yes
- Single selection only

**Backend Field:** `relationship_status`

**Data Type:** String (enum)

**Possible Values:** `"married"` | `"in_relationship"` | `"single"` | `"divorced_widowed"`

**Conditional Logic:** This answer determines if Section 5 (Relationship Dynamics) is shown

**Design Note:** Sexual activity status will be asked later in Section 6 branches where clinically relevant

---

### Question 1.8: First Consultation

**Question Text:** First consultation for this issue?

**UI Component:** Radio buttons (vertical)

**Options:**
- â—‹ Yes *(first time seeking treatment)*
- â—‹ No *(has tried treatment before)*

**Validation:**
- Required: Yes
- Single selection only

**Backend Field:** `first_consultation`

**Data Type:** Boolean

---

**Conditional Sub-question:** If "No" is selected, show:

**Sub-question Text:** What was tried earlier?

**UI Component:** Checkboxes (multi-select, vertical)

**Options:**
- â˜ Tablets *(oral medication)*
- â˜ Gels / Sprays *(topical)*
- â˜ Ayurvedic / Homeopathy
- â˜ Therapy / Counseling

**Validation:**
- Required: Yes (if parent answer is "No")
- Must select at least one option

**Backend Field:** `previous_treatments`

**Data Type:** Array of strings

**Possible Values:** `["tablets", "gels_sprays", "ayurvedic_homeopathy", "therapy"]`

**Logic:** "None" option not needed - checkboxes allow multi-select

---

### Question 1.9: Safety Screening (Red Flags)

**Question Text:** âš ï¸ Does user have any of these RIGHT NOW?

**UI Component:** Radio buttons (vertical list, special warning styling)

**Visual Styling:**
- Background: Light orange/yellow (#FFF4E6)
- Border: Orange left border (#FF9800)
- Icon: âš ï¸ warning triangle

**Options:**
1. â—‹ Severe pain in penis/testicles *(unbearable, can't touch)*
2. â—‹ Blood in urine or semen
3. â—‹ Erection lasting more than 4 hours *(priapism)*
4. â—‹ None of these symptoms

**Validation:**
- Required: Yes
- Single selection only

**Backend Field:** `emergency_red_flags`

**Data Type:** String (enum)

**Possible Values:** `"severe_pain"` | `"blood"` | `"priapism"` | `"none"`

---

**Red Flag Actions (Displayed in AI Output, NOT inline alert):**

- **Option 1 (Severe pain):**
  - Action: Escalate - Possible torsion/infection
  - Message: "âš ï¸ IMMEDIATE ESCALATION: Advise emergency in-person consultation. Possible testicular torsion or infection."

- **Option 2 (Blood):**
  - Action: STOP DISCOVERY CALL
  - Message: "âš ï¸ STOP CALL: Immediate urologist/andrologist referral required. Head to nearest physician."

- **Option 3 (Priapism):**
  - Action: EMERGENCY
  - Message: "âš ï¸ EMERGENCY: Tell patient to go to nearest hospital immediately. Priapism requires urgent treatment."

- **Option 4 (None):**
  - Action: Continue normally

**Design Note:** Using "hybrid approach" - emergency symptoms screened here, other red flags (heart attack, cancer, medications) already captured in Section 3 Medical History

---

## Section 2: Main Concern

**Purpose:** Identify primary complaint and determine which branch(es) to show

---

### Question 2.1: Main Issue

**Question Text:** What is the main issue?

**UI Component:** Radio buttons (vertical list)

**Options:**
1. â—‹ Erectile Dysfunction (ED)
2. â—‹ Early Ejaculation (PE)
3. â—‹ Both ED and PE

**Validation:**
- Required: Yes
- Single selection only

**Backend Field:** `main_issue`

**Data Type:** String (enum)

**Possible Values:** `"ed"` | `"pe"` | `"both"`

---

**Conditional Logic - CRITICAL:**

This answer determines the entire Section 6 flow:

- **If "Erectile Dysfunction (ED)":**
  - Show Section 6A (ED Branch) only
  - Hide Section 6B (PE Branch)

- **If "Early Ejaculation (PE)":**
  - Hide Section 6A (ED Branch)
  - Show Section 6B (PE Branch) only

- **If "Both ED and PE":**
  - Show Section 6A (ED Branch)
  - Show Section 6B (PE Branch)
  - User must complete both branches

---

### Question 2.2: Duration

**Question Text:** Since when are you facing this?

**UI Component:** Radio buttons (vertical list)

**Options:**
1. â—‹ Since my first sexual experience *(Lifelong)*
2. â—‹ Less than 1 month ago
3. â—‹ 1-6 months ago
4. â—‹ 6-12 months ago
5. â—‹ 1-3 years ago
6. â—‹ More than 3 years ago

**Validation:**
- Required: Yes
- Single selection only

**Backend Field:** `issue_duration`

**Data Type:** String (enum)

**Possible Values:** `"lifelong"` | `"less_1_month"` | `"1_to_6_months"` | `"6_to_12_months"` | `"1_to_3_years"` | `"more_3_years"`

**Clinical Significance:**
- **Lifelong:** Primary dysfunction (psychological/anatomical)
- **<6 months:** Transient issue (does not meet DSM-5 criteria)
- **â‰¥6 months:** Chronic ED/PE (meets DSM-5 diagnostic criteria)
- **>3 years:** Long-standing chronic condition

---

### Question 2.3: Context

**Question Text:** When is the problem faced?

**UI Component:** Radio buttons (vertical list)

**Options:**
1. â—‹ During sex with partner
2. â—‹ During masturbation
3. â—‹ Both *(during sex and masturbation)*

**Validation:**
- Required: Yes
- Single selection only

**Backend Field:** `issue_context`

**Data Type:** String (enum)

**Possible Values:** `"sex_with_partner"` | `"masturbation"` | `"both"`

**Clinical Significance:**
- **Only during sex:** Strong indicator of psychological/performance anxiety
- **Only during masturbation:** Rare, needs investigation (habit, guilt, porn-induced)
- **Both:** Suggests biological cause (hormonal, vascular, neurological)

---

## Section 3: Medical & Lifestyle

**Purpose:** Capture comorbidities, medications, and lifestyle factors that influence ED/PE

---

### Question 3.1: Chronic Medical Conditions

**Question Text:** Do you have any chronic medical conditions?

**UI Component:** Checkboxes (multi-select, vertical list)

**Options:**
- â˜ None
- â˜ Diabetes
- â˜ High Blood Pressure
- â˜ Thyroid disorder
- â˜ Heart disease
- â˜ Depression
- â˜ Other *(please specify):* ___________

**Validation:**
- Required: Yes (must select at least one)
- If "None" selected, disable all other options
- If any other option selected, disable "None"
- If "Other" checked, text input becomes required

**Backend Fields:**
- `medical_conditions` (Array of strings)
- `medical_conditions_other` (String, only if "Other" selected)

**Possible Values:** `["none", "diabetes", "hypertension", "thyroid", "heart_disease", "depression", "other"]`

**UI Logic:**
```javascript
// Mutually exclusive "None" checkbox
if (noneCheckbox.checked) {
  disableAllOtherCheckboxes();
} else {
  disableNoneCheckbox();
}
```

---

### Question 3.2: Current Medications

**Question Text:** Are you currently taking any medications?

**UI Component:** Checkboxes (multi-select, vertical list)

**Options:**
- â˜ None
- â˜ Psychiatric medications
- â˜ Blood pressure medications
- â˜ Diabetes medications
- â˜ Blood thinners
- â˜ Other *(please specify):* ___________

**Validation:**
- Required: Yes (must select at least one)
- If "None" selected, disable all other options
- If any other option selected, disable "None"
- If "Other" checked, text input becomes required

**Backend Fields:**
- `current_medications` (Array of strings)
- `current_medications_other` (String, only if "Other" selected)

**Possible Values:** `["none", "psychiatric", "blood_pressure", "diabetes", "blood_thinners", "other"]`

---

**Red Flag Logic:**

**If "Blood thinners" is checked:**
- Action: DO NOT OFFER TREATMENT PLAN
- Message (in AI output): "âš ï¸ BLOOD THINNERS CONTRAINDICATION: Do not offer online treatment. Refer patient to appropriate specialist for in-person consultation."

---

### Question 3.3: Surgeries or Injuries

**Question Text:** Any surgeries or injuries in the spinal or genital area?

**UI Component:** Radio buttons (vertical)

**Options:**
- â—‹ Yes
- â—‹ No

**Validation:**
- Required: Yes
- Single selection only

**Backend Field:** `spinal_genital_surgery`

**Data Type:** Boolean

**Doctor Routing:** If "Yes" â†’ Flag for Andrologist routing (in-person evaluation needed)

---

### Question 3.4: Alcohol Consumption

**Question Text:** How often do you drink alcohol?

**UI Component:** Radio buttons (vertical list)

**Options:**
1. â—‹ No alcohol
2. â—‹ Once a month or less
3. â—‹ Once every 2 weeks
4. â—‹ Once a week
5. â—‹ 2-3 times per week
6. â—‹ Daily

**Validation:**
- Required: Yes
- Single selection only

**Backend Field:** `alcohol_frequency`

**Data Type:** String (enum)

**Possible Values:** `"none"` | `"monthly"` | `"biweekly"` | `"weekly"` | `"2_3_per_week"` | `"daily"`

**Options Ordered By:** Frequency (least to most)

---

### Question 3.5: Smoking

**Question Text:** Do you smoke?

**UI Component:** Radio buttons (vertical list)

**Options:**
1. â—‹ No smoking
2. â—‹ Occasionally *(only while drinking or social events)*
3. â—‹ Few times per week
4. â—‹ Daily

**Validation:**
- Required: Yes
- Single selection only

**Backend Field:** `smoking_frequency`

**Data Type:** String (enum)

**Possible Values:** `"none"` | `"occasional"` | `"few_per_week"` | `"daily"`

---

### Question 3.6: Sleep Quality

**Question Text:** How is your sleep quality?

**UI Component:** Radio buttons (vertical list)

**Options:**
1. â—‹ Good
2. â—‹ Average
3. â—‹ Poor

**Validation:**
- Required: Yes
- Single selection only

**Backend Field:** `sleep_quality`

**Data Type:** String (enum)

**Possible Values:** `"good"` | `"average"` | `"poor"`

**Note:** Subjective self-assessment (like "How do you feel?")

---

### Question 3.7: Physical Activity

**Question Text:** How physically active are you?

**UI Component:** Radio buttons (vertical list)

**Options:**
1. â—‹ Active
2. â—‹ Somewhat active
3. â—‹ Not active

**Validation:**
- Required: Yes
- Single selection only

**Backend Field:** `physical_activity`

**Data Type:** String (enum)

**Possible Values:** `"active"` | `"somewhat_active"` | `"not_active"`

**Note:** Self-reported activity level

---

## Section 4: Masturbation & Behavioral History

**Purpose:** Capture masturbation habits and porn usage patterns (critical for PE/ED root cause analysis)

---

### Question 4.1: Masturbation Method

**Question Text:** How do you usually masturbate?

**UI Component:** Radio buttons (vertical list)

**Options:**
1. â—‹ No masturbation
2. â—‹ Using hands
3. â—‹ Rubbing against surface *(prone)*
4. â—‹ Both hands and rubbing surface

**Validation:**
- Required: Yes
- Single selection only

**Backend Field:** `masturbation_method`

**Data Type:** String (enum)

**Possible Values:** `"none"` | `"hands"` | `"prone"` | `"both"`

---

**Conditional Logic:**

**If Option 1 ("No masturbation") is selected:**
- Skip Questions 4.2 and 4.3
- Mark them as "N/A" in backend
- Question 4.4 (porn usage) still shows (separate behavior)

**If Option 2, 3, or 4 is selected:**
- Show Questions 4.2 and 4.3 in an expanded dropdown/section

---

### Question 4.2: Grip Type (Conditional)

**Display Condition:** Only shown if Q4.1 â‰  "No masturbation"

**Question Text:** Is your grip during masturbation normal or tight?

**UI Component:** Radio buttons (vertical list)

**Options:**
1. â¦¿ Normal **(DEFAULT - pre-selected)**
2. â—‹ Tight

**Validation:**
- Required: Yes (if shown)
- Single selection only
- Normal is pre-selected by default

**Backend Field:** `masturbation_grip`

**Data Type:** String (enum)

**Possible Values:** `"normal"` | `"tight"` | `"N/A"`

**Default Value:** `"normal"` (if Q4.1 â‰  "No masturbation")

**Clinical Significance:** Tight grip can desensitize penis, contributing to ED during partnered sex

---

### Question 4.3: Masturbation Frequency (Conditional)

**Display Condition:** Only shown if Q4.1 â‰  "No masturbation"

**Question Text:** How often do you masturbate per week?

**UI Component:** Radio buttons (vertical list)

**Options:**
1. â—‹ None
2. â—‹ Less than 3 times per week
3. â—‹ 3-7 times per week
4. â—‹ 8 or more times per week

**Validation:**
- Required: Yes (if shown)
- Single selection only

**Backend Field:** `masturbation_frequency`

**Data Type:** String (enum)

**Possible Values:** `"none"` | `"less_than_3"` | `"3_to_7"` | `"8_plus"` | `"N/A"`

---

### Question 4.4: Porn Usage

**Display Condition:** Always visible (not in conditional dropdown)

**Question Text:** How often do you watch porn?

**UI Component:** Radio buttons (vertical list)

**Options:**
1. â—‹ None
2. â—‹ Less than 2 times per week
3. â—‹ 3-5 times per week
4. â—‹ Daily or more

**Validation:**
- Required: Yes
- Single selection only

**Backend Field:** `porn_frequency`

**Data Type:** String (enum)

**Possible Values:** `"none"` | `"less_than_2"` | `"3_to_5"` | `"daily_or_more"`

**Clinical Significance:** Porn-induced ED is real - daily use = high risk factor. Excessive porn can shift arousal patterns and cause ED/PE.

---

## Section 5: Relationship Dynamics

**Purpose:** Assess partner support/awareness (impacts psychological factors in ED/PE)

---

### Question 5.1: Partner Response

**Display Condition:** Only shown if Section 1.7 (Relationship Status) = "Married" OR "In a relationship"

**If user selected "Single" or "Divorced/Widowed" in Q1.7, this entire section is hidden.**

**Question Text:** How would you describe your partner's response to this issue?

**UI Component:** Radio buttons (vertical list)

**Options:**
1. â—‹ Supportive
2. â—‹ Neutral
3. â—‹ Non-supportive
4. â—‹ Unaware *(haven't told them)*

**Validation:**
- Required: Yes (if shown)
- Single selection only

**Backend Field:** `partner_response`

**Data Type:** String (enum)

**Possible Values:** `"supportive"` | `"neutral"` | `"non_supportive"` | `"unaware"` | `"N/A"`

**Default Value:** `"N/A"` (if user is single/divorced/widowed)

**Clinical Significance:**
- Non-supportive or unaware â†’ Relationship stress factor
- Supportive â†’ Better treatment outcomes

---

## Section 6A: ED Branch

**Display Condition:** Only shown if Section 2.1 = "Erectile Dysfunction (ED)" OR "Both ED and PE"

**Purpose:** Detailed erectile dysfunction assessment with elimination logic to determine situational vs generalized ED

---

### Question 6A.1: Gateway Question

**Question Text:** Do you get erections at all?

**UI Component:** Radio buttons (vertical)

**Options:**
1. â—‹ Yes
2. â—‹ No

**Validation:**
- Required: Yes
- Single selection only

**Backend Field:** `ed_gets_erections`

**Data Type:** Boolean

---

**Conditional Logic - CRITICAL:**

**If "No" is selected:**
1. Hide/collapse ALL remaining ED questions (Q6A.2 through Q6A.10)
2. Mark Q6A.2-Q6A.10 as `"N/A - No erections in any situation"` in backend
3. Set routing flag: `andrologist_complete_ed: true`
4. Display in **final AI output only**: "âš ï¸ Route to Andrologist - Complete erectile failure"
5. If user also has PE (Section 2.1 = "Both"), proceed to Section 6B
6. If user only has ED, proceed to form completion

**If "Yes" is selected:**
- Continue to Q6A.2

---

### Question 6A.2: Context Establishment

**Display Condition:** Only shown if Q6A.1 = "Yes"

**Question Text:** Do you currently have sex with a partner?

**UI Component:** Radio buttons (vertical list)

**Options:**
1. â—‹ Yes, I have sex with a partner
2. â—‹ I have a partner but avoid sex due to worry/fear
3. â—‹ No, I don't have a partner

**Validation:**
- Required: Yes
- Single selection only

**Backend Field:** `ed_sexual_activity_status`

**Data Type:** String (enum)

**Possible Values:** `"yes_active"` | `"avoiding_due_to_fear"` | `"no_partner"`

---

**Conditional Logic - Pathway Selection:**

**If Option 1 or 2 (Has Partner):**
- Show **Partner Performance Pathway:** Q6A.3 through Q6A.7
- Hide Solo Pathway questions (Q6A.8-Q6A.10)

**If Option 3 (No Partner):**
- Hide Partner Performance Pathway (Q6A.3-Q6A.7)
- Show **Solo Function Pathway:** Q6A.8 through Q6A.10

**Medical Significance:**
- Option 2 (avoiding sex due to fear) = Strong performance anxiety indicator

---

## PARTNER PERFORMANCE PATHWAY

**Display Condition:** Only if Q6A.2 = Option 1 or 2 (has partner)

---

### Question 6A.3: Arousal Speed (With Partner)

**Question Text:** Does it take a long time to get erections?

**UI Component:** Radio buttons (vertical list)

**Options:**
1. â—‹ Always
2. â—‹ Sometimes
3. â—‹ Rarely

**Validation:**
- Required: Yes
- Single selection only

**Backend Field:** `ed_partner_arousal_speed`

**Data Type:** String (enum)

**Possible Values:** `"always"` | `"sometimes"` | `"rarely"`

**Medical Significance:**
- Always slow â†’ Vascular insufficiency, low testosterone, severe anxiety
- Sometimes â†’ Situational factors, moderate anxiety
- Rarely â†’ Minimal arousal issues

---

### Question 6A.4: Erectile Maintenance (With Partner)

**Question Text:** Does it stay hard till penetration or completion?

**UI Component:** Radio buttons (vertical list)

**Options:**
1. â—‹ Loses hardness before penetration
2. â—‹ Stays hard till penetration, then loses it
3. â—‹ Stays hard till completion

**Validation:**
- Required: Yes
- Single selection only

**Backend Field:** `ed_partner_maintenance`

**Data Type:** String (enum)

**Possible Values:** `"loses_before_penetration"` | `"loses_during_sex"` | `"stays_till_completion"`

**Medical Significance:**
- Loses before penetration â†’ Severe performance anxiety or vascular issue
- Loses during sex â†’ Venous leak, moderate anxiety, distraction
- Stays throughout â†’ Maintenance not the issue (focus on other factors)

---

### Question 6A.5: Erection Quality (With Partner)

**Question Text:** Is the erection hard enough for penetration?

**UI Component:** Radio buttons (vertical list)

**Options:**
1. â—‹ Yes, always hard enough
2. â—‹ Sometimes hard enough
3. â—‹ Rarely hard enough
4. â—‹ Never hard enough

**Validation:**
- Required: Yes
- Single selection only

**Backend Field:** `ed_partner_hardness`

**Data Type:** String (enum)

**Possible Values:** `"always_hard"` | `"sometimes_hard"` | `"rarely_hard"` | `"never_hard"`

**Medical Significance (Erection Hardness Score mapping):**
- Always hard â†’ EHS 3-4 (good quality)
- Sometimes â†’ EHS 2-3 (moderate ED)
- Rarely â†’ EHS 1-2 (severe ED)
- Never â†’ EHS 1 (complete erectile failure during sex)

---

### Question 6A.6: Morning Erections - Comparison Point

**Question Text:** Are morning erections regular, occasional, or absent?

**UI Component:** Radio buttons (vertical list)

**Options:**
1. â—‹ Regular *(most mornings)*
2. â—‹ Occasional *(sometimes)*
3. â—‹ Absent *(rarely or never)*

**Validation:**
- Required: Yes
- Single selection only

**Backend Field:** `ed_morning_erections`

**Data Type:** String (enum)

**Possible Values:** `"regular"` | `"occasional"` | `"absent"`

**Medical Significance - CRITICAL DIAGNOSTIC:**
- **Regular morning erections + ED with partner** = Strong indicator of **Situational/Psychological ED** (performance anxiety)
- **Absent morning erections + ED with partner** = Strong indicator of **Organic/Generalized ED** (vascular, hormonal, neurological)
- **Occasional** = Mixed biological + psychological factors

**Explanation:** Morning erections (nocturnal penile tumescence) occur during REM sleep when parasympathetic nervous system is active. Presence indicates healthy blood flow, nerve function, and testosterone levels. They're non-volitional (not subject to psychological inhibition).

---

### Question 6A.7: Masturbation & Imagination - Comparison Point

**Question Text:** Do you get erections during masturbation or with imagination/fantasies?

**UI Component:** Radio buttons (vertical list, single select)

**Options:**
1. â—‹ Yes, during both masturbation and imagination
2. â—‹ Yes, during masturbation only
3. â—‹ Yes, with imagination/fantasies only
4. â—‹ No, neither works

**Validation:**
- Required: Yes
- Single selection only

**Backend Field:** `ed_masturbation_imagination`

**Data Type:** String (enum)

**Possible Values:** `"both"` | `"masturbation_only"` | `"imagination_only"` | `"neither"`

**Medical Significance - CRITICAL DIAGNOSTIC:**
- **Both work + ED with partner** = Strong **Situational ED** (partner-specific performance anxiety)
- **Masturbation works but not imagination** = Psychogenic pathway affected, reflexogenic intact
- **Imagination works but not masturbation** = Physical stimulation issues, mental arousal intact
- **Neither works** = **Generalized ED** (both pathways affected - severe organic cause)

**Explanation:**
- **Reflexogenic erections (masturbation):** Triggered by physical touch â†’ Spinal reflex pathway â†’ Tests nerve + vascular function
- **Psychogenic erections (imagination):** Triggered by mental stimulation â†’ Brain â†’ spinal pathway â†’ Tests psychological arousal + higher brain function

---

## SOLO FUNCTION PATHWAY

**Display Condition:** Only if Q6A.2 = Option 3 (no partner)

**Purpose:** Assess baseline erectile function in non-partnered contexts

---

### Question 6A.8: Morning Erections - Primary Assessment

**Question Text:** Are morning erections regular, occasional, or absent?

**UI Component:** Radio buttons (vertical list)

**Options:**
1. â—‹ Regular *(most mornings)*
2. â—‹ Occasional *(sometimes)*
3. â—‹ Absent *(rarely or never)*

**Validation:**
- Required: Yes
- Single selection only

**Backend Field:** `ed_solo_morning_erections`

**Data Type:** String (enum)

**Possible Values:** `"regular"` | `"occasional"` | `"absent"`

**Medical Significance:**
- Regular = Healthy nocturnal erectile function (hormonal, vascular, neurological systems intact)
- Occasional = Partial dysfunction
- Absent = Organic dysfunction likely (low testosterone, vascular issues, neurological problems)

---

### Question 6A.9: Masturbation & Imagination - Primary Assessment

**Question Text:** Do you get erections during masturbation or with imagination/fantasies?

**UI Component:** Radio buttons (vertical list, single select)

**Options:**
1. â—‹ Yes, during both masturbation and imagination
2. â—‹ Yes, during masturbation only
3. â—‹ Yes, with imagination/fantasies only
4. â—‹ No, neither works

**Validation:**
- Required: Yes
- Single selection only

**Backend Field:** `ed_solo_masturbation_imagination`

**Data Type:** String (enum)

**Possible Values:** `"both"` | `"masturbation_only"` | `"imagination_only"` | `"neither"`

**Medical Significance:** Same as Q6A.7 but this is PRIMARY assessment (not comparison to partnered sex)

---

### Question 6A.10: Arousal Speed (During Masturbation)

**Question Text:** Does it take a long time to get erections during masturbation?

**UI Component:** Radio buttons (vertical list)

**Options:**
1. â—‹ Always
2. â—‹ Sometimes
3. â—‹ Rarely

**Validation:**
- Required: Yes
- Single selection only

**Backend Field:** `ed_solo_arousal_speed`

**Data Type:** String (enum)

**Possible Values:** `"always"` | `"sometimes"` | `"rarely"`

**Medical Significance:**
Assesses arousal speed in pressure-free context. Slow arousal even during masturbation suggests organic factors (vascular, hormonal) rather than psychological.

---

## ED Branch Summary

### Question Count
- **Partner Pathway:** 7 questions (Q6A.1, Q6A.2, Q6A.3, Q6A.4, Q6A.5, Q6A.6, Q6A.7)
- **Solo Pathway:** 5 questions (Q6A.1, Q6A.2, Q6A.8, Q6A.9, Q6A.10)
- **Complete ED (No erections):** 1 question (Q6A.1 â†’ Andrologist)

### Diagnostic Flow Logic

```
Q6A.1: Get erections at all?
â”œâ”€ NO â†’ Andrologist (STOP ED branch)
â””â”€ YES â†“

Q6A.2: Have sex with partner?
â”œâ”€ YES/AVOIDING (Partner Pathway) â†“
â”‚   Q6A.3: Arousal speed (with partner)
â”‚   Q6A.4: Maintenance (with partner)
â”‚   Q6A.5: Hardness quality (with partner)
â”‚   Q6A.6: Morning erections (COMPARISON)
â”‚   Q6A.7: Masturbation/imagination (COMPARISON)
â”‚   
â”‚   AI Analysis:
â”‚   â€¢ Partner performance issues + Morning/Masturbation works
â”‚     â†’ Situational/Psychological ED (Performance Anxiety)
â”‚   â€¢ Partner issues + Morning/Masturbation also fails
â”‚     â†’ Generalized/Organic ED (Vascular, Hormonal, Neurological)
â”‚
â””â”€ NO PARTNER (Solo Pathway) â†“
    Q6A.8: Morning erections (primary)
    Q6A.9: Masturbation/imagination (primary)
    Q6A.10: Arousal speed (masturbation)
    
    AI Analysis:
    â€¢ Baseline erectile function assessment
    â€¢ No partnered performance data available
    â€¢ Diagnosis based on solo function patterns
```

---

## Section 6B: PE Branch

**Display Condition:** Only shown if Section 2.1 = "Early Ejaculation (PE)" OR "Both ED and PE"

**Purpose:** Detailed premature ejaculation assessment with elimination logic to determine lifelong vs acquired, situational vs biological PE

---

### Question 6B.1: Context Establishment

**Question Text:** Do you currently have sex with a partner?

**UI Component:** Radio buttons (vertical list)

**Options:**
1. â—‹ Yes, I have sex with a partner
2. â—‹ I have a partner but avoid sex due to worry/fear
3. â—‹ No, I don't have a partner

**Validation:**
- Required: Yes
- Single selection only

**Backend Field:** `pe_sexual_activity_status`

**Data Type:** String (enum)

**Possible Values:** `"yes_active"` | `"avoiding_due_to_fear"` | `"no_partner"`

---

**Conditional Logic - Pathway Selection:**

**If Option 1 or 2 (Has Partner):**
- Show **Partner Performance Pathway:** Q6B.2 through Q6B.5
- Hide Solo Pathway questions (Q6B.6-Q6B.9)

**If Option 3 (No Partner):**
- Hide Partner Performance Pathway (Q6B.2-Q6B.5)
- Show **Solo Function Pathway:** Q6B.6 through Q6B.9

**Medical Significance:**
- Option 2 (avoiding sex due to fear) = Strong performance anxiety indicator

---

## PARTNER PERFORMANCE PATHWAY

**Display Condition:** Only if Q6B.1 = Option 1 or 2 (has partner)

---

### Question 6B.2: Ejaculation Time (With Partner)

**Question Text:** What is your ejaculation time during sex?

**UI Component:** Radio buttons (vertical list)

**Options:**
1. â—‹ Before penetration
2. â—‹ Less than 1 minute after penetration
3. â—‹ 1-3 minutes after penetration
4. â—‹ More than 3 minutes

**Validation:**
- Required: Yes
- Single selection only

**Backend Field:** `pe_partner_ejaculation_time`

**Data Type:** String (enum)

**Possible Values:** `"before_penetration"` | `"less_than_1_min"` | `"1_to_3_min"` | `"more_than_3_min"`

**Medical Significance - DSM-5 Diagnostic Criteria:**
- **Options 1-2 (before penetration or <1 min):** Meets **DSM-5 criteria for PE diagnosis**
- **Option 3 (1-3 min):** Borderline PE (subjective concern)
- **Option 4 (>3 min):** Normal ejaculatory latency

**Note:** The ejaculation time considered premature for Indian men is approximately **within 1 minute of vaginal penetration** (as per PE training module).

---

### Question 6B.3: Lifelong vs Acquired

**Question Text:** Has this been since your first sexual encounter or started later?

**UI Component:** Radio buttons (vertical list)

**Options:**
1. â—‹ Since first time *(lifelong)*
2. â—‹ Started later *(acquired)*

**Validation:**
- Required: Yes
- Single selection only

**Backend Field:** `pe_partner_type`

**Data Type:** String (enum)

**Possible Values:** `"lifelong"` | `"acquired"`

**Medical Significance - CRITICAL FOR ROOT CAUSE:**
- **Lifelong:** Primary PE (biological, neurological, possibly genetic - serotonin/dopamine imbalance, hypersensitivity)
- **Acquired:** Secondary PE (psychological trigger, relationship change, medical condition, stress, anxiety)

---

### Question 6B.4: Penile Sensitivity

**Question Text:** Do you feel the penis tip is very sensitive?

**UI Component:** Radio buttons (vertical)

**Options:**
1. â—‹ Yes
2. â—‹ No

**Validation:**
- Required: Yes
- Single selection only

**Backend Field:** `pe_partner_penile_sensitivity`

**Data Type:** Boolean

**Medical Significance:**
- **Yes:** Hypersensitivity of glans penis (biological factor, high nerve receptor density in penile tip)
- Often correlates with **lifelong PE**
- Can benefit from topical desensitizing treatments (lidocaine-prilocaine cream)

---

### Question 6B.5: Control During Masturbation - Comparison Point

**Question Text:** Can you delay or control ejaculation during masturbation?

**UI Component:** Radio buttons (vertical list)

**Options:**
1. â—‹ Always can control
2. â—‹ Sometimes can control
3. â—‹ Rarely can control

**Validation:**
- Required: Yes
- Single selection only

**Backend Field:** `pe_partner_masturbation_control`

**Data Type:** String (enum)

**Possible Values:** `"always"` | `"sometimes"` | `"rarely"`

**Medical Significance - CRITICAL DIAGNOSTIC:**
- **Can control during masturbation BUT NOT during sex** â†’ **Situational/Performance Anxiety PE** (psychological, partner-specific)
- **Cannot control in EITHER context** â†’ **Biological/Generalized PE** (hypersensitivity, neurological, hormonal - serotonin/dopamine imbalance)

**This is the KEY question for differentiating psychological vs biological PE.**

---

## SOLO FUNCTION PATHWAY

**Display Condition:** Only if Q6B.1 = Option 3 (no partner)

**Purpose:** Assess baseline ejaculatory control in non-partnered contexts

---

### Question 6B.6: Ejaculation Time During Masturbation

**Question Text:** How quickly do you ejaculate during masturbation?

**UI Component:** Radio buttons (vertical list)

**Options:**
1. â—‹ Less than 1 minute
2. â—‹ 1-3 minutes
3. â—‹ More than 3 minutes

**Validation:**
- Required: Yes
- Single selection only

**Backend Field:** `pe_solo_ejaculation_time`

**Data Type:** String (enum)

**Possible Values:** `"less_than_1_min"` | `"1_to_3_min"` | `"more_than_3_min"`

**Medical Significance:**
Establishes baseline ejaculatory latency in pressure-free context. Quick ejaculation even during solo masturbation suggests biological PE rather than performance anxiety.

---

### Question 6B.7: Lifelong vs Acquired

**Question Text:** Has this been since you started masturbating or started later?

**UI Component:** Radio buttons (vertical list)

**Options:**
1. â—‹ Since I started *(lifelong)*
2. â—‹ Started later *(acquired)*

**Validation:**
- Required: Yes
- Single selection only

**Backend Field:** `pe_solo_type`

**Data Type:** String (enum)

**Possible Values:** `"lifelong"` | `"acquired"`

**Medical Significance:** Same as Q6B.3 - critical for determining primary vs secondary PE

---

### Question 6B.8: Penile Sensitivity

**Question Text:** Do you feel the penis tip is very sensitive?

**UI Component:** Radio buttons (vertical)

**Options:**
1. â—‹ Yes
2. â—‹ No

**Validation:**
- Required: Yes
- Single selection only

**Backend Field:** `pe_solo_penile_sensitivity`

**Data Type:** Boolean

**Medical Significance:** Same as Q6B.4

---

### Question 6B.9: Control During Masturbation

**Question Text:** Can you delay or control ejaculation during masturbation?

**UI Component:** Radio buttons (vertical list)

**Options:**
1. â—‹ Always can control
2. â—‹ Sometimes can control
3. â—‹ Rarely can control

**Validation:**
- Required: Yes
- Single selection only

**Backend Field:** `pe_solo_masturbation_control`

**Data Type:** String (enum)

**Possible Values:** `"always"` | `"sometimes"` | `"rarely"`

**Medical Significance:**
In solo pathway, this is PRIMARY assessment (not comparison). Lack of control even during masturbation indicates biological PE.

---

## PE Branch Summary

### Question Count
- **Partner Pathway:** 5 questions (Q6B.1, Q6B.2, Q6B.3, Q6B.4, Q6B.5)
- **Solo Pathway:** 5 questions (Q6B.1, Q6B.6, Q6B.7, Q6B.8, Q6B.9)

### Diagnostic Flow Logic

```
Q6B.1: Have sex with partner?
â”œâ”€ YES/AVOIDING (Partner Pathway) â†“
â”‚   Q6B.2: Ejaculation time (with partner) - Severity
â”‚   Q6B.3: Lifelong/Acquired - Primary classification
â”‚   Q6B.4: Penile sensitivity - Biological factor
â”‚   Q6B.5: Control during masturbation - COMPARISON
â”‚   
â”‚   AI Analysis:
â”‚   â€¢ Fast ejaculation during sex + Can control during masturbation
â”‚     â†’ Situational/Performance Anxiety PE
â”‚   â€¢ Fast ejaculation in BOTH contexts + High sensitivity
â”‚     â†’ Biological/Generalized PE (Hypersensitivity, Neurological)
â”‚   â€¢ Lifelong + Biological factors
â”‚     â†’ Primary PE (Serotonin/Dopamine imbalance)
â”‚   â€¢ Acquired + Psychological factors
â”‚     â†’ Secondary PE (Stress, Relationship issues, Anxiety)
â”‚
â””â”€ NO PARTNER (Solo Pathway) â†“
    Q6B.6: Ejaculation time (masturbation)
    Q6B.7: Lifelong/Acquired
    Q6B.8: Penile sensitivity
    Q6B.9: Control during masturbation
    
    AI Analysis:
    â€¢ Baseline ejaculatory control assessment
    â€¢ No partnered performance data available
    â€¢ Diagnosis based on solo function patterns
```

---

## Section 7: Other Information (Open Box)

**Purpose:** Capture any additional information that may not fit into structured questions

---

### Question 7.1: Other Information

**Question Text:** Other Information *(Optional)*

**Helper Text:** Is there anything else the agent or doctor should know? Any symptoms, concerns, or context not covered above.

**UI Component:** Textarea (multi-line text input)

**Validation:**
- Required: No (optional field)
- Maximum length: 1000 characters
- Character counter displayed: "500/1000 characters"

**Backend Field:** `other_information`

**Data Type:** String

**Default Value:** Empty string

**Usage Note:** 
- This field is NOT used for AI root cause analysis in MVP
- Purpose: Capture edge cases or additional context we may have missed in structured questions
- Useful for form improvement and identifying missing question patterns

**Display Logic:**
- Always shown at the end of the form
- Appears after Section 6 (ED/PE branches)
- Shown just before the Submit button

---

## Data Structure Reference

### Complete JSON Output Structure

```json
{
  "section1_client_info": {
    "full_name": "string",
    "age": 25,
    "height_cm": 175,
    "height_input_method": "metric",
    "height_original_value": "175",
    "weight_kg": 70.5,
    "bmi": 23.02,
    "city": "Delhi",
    "occupation": "corporate",
    "relationship_status": "in_relationship",
    "first_consultation": true,
    "previous_treatments": [],
    "emergency_red_flags": "none"
  },
  
  "section2_main_concern": {
    "main_issue": "both",
    "issue_duration": "6_to_12_months",
    "issue_context": "sex_with_partner"
  },
  
  "section3_medical_lifestyle": {
    "medical_conditions": ["none"],
    "medical_conditions_other": null,
    "current_medications": ["none"],
    "current_medications_other": null,
    "spinal_genital_surgery": false,
    "alcohol_frequency": "weekly",
    "smoking_frequency": "occasional",
    "sleep_quality": "average",
    "physical_activity": "somewhat_active"
  },
  
  "section4_masturbation_history": {
    "masturbation_method": "hands",
    "masturbation_grip": "normal",
    "masturbation_frequency": "3_to_7",
    "porn_frequency": "3_to_5"
  },
  
  "section5_relationship": {
    "partner_response": "supportive"
  },
  
  "section6a_ed": {
    "ed_gets_erections": true,
    "ed_sexual_activity_status": "yes_active",
    "ed_partner_arousal_speed": "sometimes",
    "ed_partner_maintenance": "loses_during_sex",
    "ed_partner_hardness": "sometimes_hard",
    "ed_morning_erections": "regular",
    "ed_masturbation_imagination": "both",
    "routing_flags": {
      "andrologist": false,
      "complete_ed": false
    }
  },
  
  "section6b_pe": {
    "pe_sexual_activity_status": "yes_active",
    "pe_partner_ejaculation_time": "less_than_1_min",
    "pe_partner_type": "acquired",
    "pe_partner_penile_sensitivity": false,
    "pe_partner_masturbation_control": "always"
  },
  
  "section7_other_info": {
    "other_information": "Patient mentioned occasional lower back pain. Also concerned about stress from work affecting sleep quality."
  },
  
  "metadata": {
    "form_version": "1.0",
    "submission_timestamp": "2025-11-06T10:30:00Z",
    "agent_id": "agent_123",
    "call_duration_minutes": 15
  }
}
```

### Backend Field Naming Convention

- **Snake_case** for all field names (e.g., `full_name`, `medical_conditions`)
- **Section prefix** for organization (e.g., `section1_`, `ed_`, `pe_`)
- **Boolean fields** for yes/no questions (true/false)
- **Enum strings** for categorical data (lowercase with underscores)
- **Arrays** for multi-select checkboxes
- **Null** for optional fields not filled

---

## Red Flag Logic

### Red Flag Categories

Based on discussions and the Red Flags document, here are the key red flags and their handling:

---

### **Emergency Red Flags (Q1.9 - Section 1)**

Screened at the start of the form:

1. **Severe genital pain**
   - Action: Escalate immediately
   - Message: "âš ï¸ IMMEDIATE ESCALATION: Advise emergency in-person consultation. Possible testicular torsion or infection."

2. **Blood in urine or semen**
   - Action: STOP DISCOVERY CALL
   - Message: "âš ï¸ STOP CALL: Immediate urologist/andrologist referral required. Head to nearest physician."

3. **Priapism (erection >4 hours)**
   - Action: EMERGENCY
   - Message: "âš ï¸ EMERGENCY: Tell patient to go to nearest hospital immediately. Priapism requires urgent treatment."

---

### **Medical History Red Flags (Q3.1 - Section 3)**

**Heart Disease:**
- If user has heart disease AND mentions "recent heart attack" or "stents in last 1 year" in open-ended responses
- Action: Do not proceed with treatment plan
- Message: "Cardiology clearance needed before ED treatment"

**Active Cancer Treatment:**
- If user mentions "chemotherapy" or "cancer treatment ongoing"
- Action: Escalate to doctor review
- Message: "Needs consultation with oncologist before treatment"

---

### **Medication Red Flags (Q3.2 - Section 3)**

**Blood Thinners:**
- If "Blood thinners" checkbox selected
- Action: DO NOT OFFER TREATMENT PLAN
- Message: "âš ï¸ BLOOD THINNERS CONTRAINDICATION: Do not offer online treatment. Refer patient to appropriate specialist for in-person consultation."

**Nitrate Medications:**
- If user mentions nitrates in "Other medications"
- Action: Contraindicated with ED meds
- Message: "Nitrate medications contraindicated with ED treatment. Escalate to doctor, do not prescribe online."

---

### **Age Red Flags (Q1.2 - Section 1)**

**Under 18:**
- Action: STOP CALL - Cannot proceed
- Message: "Cannot proceed - patient is a minor. Decline and document."

**Over 80:**
- Action: Flag for in-person consultation only
- Message: "Patient over 80 years old - in-person consultation required"

---

### **Complete Erectile Failure (Q6A.1 - Section 6A)**

**No erections at all:**
- Action: Route to Andrologist
- Message: "âš ï¸ Route to Andrologist - Complete erectile failure in all contexts"

---

### **Surgery/Injury Red Flag (Q3.3 - Section 3)**

**Spinal or genital surgery:**
- Action: Route to Andrologist
- Message: "Spinal or genital surgery history - Andrologist evaluation needed"

---

### Red Flag Display Logic

**Timing:** Red flag messages are displayed in the **FINAL AI OUTPUT** only, not as inline alerts during form filling.

**Format:**
```
âš ï¸ RED FLAGS DETECTED:

1. BLOOD THINNERS CONTRAINDICATION
   Action: Do not offer online treatment
   Refer to: In-person specialist consultation

2. Route to Andrologist
   Reason: Complete erectile failure
```

---

## Agent Training Notes

### General Form Usage Guidelines

**Context Awareness:**
- Agents fill this form during **live video calls** with patients
- High cognitive load environment - form must be dead simple
- Users are speaking in **Hinglish/Hindi** - agents translate to English selections
- Average call duration: 15-20 minutes

**Filling Best Practices:**

1. **Read questions verbatim** - questions are designed to be asked exactly as written
2. **Don't interpret** - if user says "sometimes," select "Sometimes" option
3. **One question at a time** - don't skip ahead
4. **Use tab key** to navigate quickly between fields
5. **If unclear, ask for clarification** - don't guess
6. **Mark red flags immediately** - don't proceed if emergency symptoms

---

### Section-Specific Agent Notes

**Section 1 (Client Information):**
- **Age verification is critical** - if under 18, stop immediately
- **Height/Weight:** Let user choose cm or ft-in, don't force conversion
- **Occupation:** If user is "doing business," select "Business Owner"
- **Relationship Status:** Don't ask about sexual activity here (asked later)

**Section 2 (Main Concern):**
- **Main Issue:** This determines the entire form flow - confirm with user
- **Duration:** "Since first time" = Lifelong, be clear about this
- **Context:** If user says "everywhere," select "Both"

**Section 3 (Medical & Lifestyle):**
- **Medical Conditions:** Check multiple if user has multiple conditions
- **"None" is exclusive** - can't select "None" + another condition
- **Blood thinners = STOP treatment** - flag this immediately
- **Alcohol/Smoking:** These are about frequency, not judgment

**Section 4 (Masturbation History):**
- **Sensitive topic** - maintain professional tone
- **Grip type:** Most will say "normal" - only ask if they mention "tight grip"
- **Porn frequency:** Be non-judgmental, just record the answer

**Section 5 (Relationship):**
- **Only shows if user has partner** - system handles this automatically
- **Partner unaware:** Common response, not unusual

**Section 6A (ED Branch):**
- **"Do you get erections at all?"** - This is about ANY context (morning, masturbation, sex)
- **Morning erections** - Most men don't pay attention to this, may need clarification
- **Masturbation vs Imagination** - Explain: "Can you get hard just by thinking about sex?"

**Section 6B (PE Branch):**
- **Ejaculation time** - User estimates, don't require exact measurement
- **Lifelong vs Acquired** - "Always had this problem?" = Lifelong, "Started recently?" = Acquired
- **Penis tip sensitivity** - User perception, not medical test

---

### Common User Language Patterns

**ED:**
- "It doesn't get hard" â†’ Select appropriate hardness level
- "It goes soft in the middle" â†’ Loses hardness during sex
- "Takes forever to get up" â†’ Takes long time to get erections
- "Morning time mein hota hai" â†’ Regular morning erections

**PE:**
- "Bahut jaldi ho jaata hai" â†’ Before or <1 minute
- "Control nahi hota" â†’ Rarely can control
- "Pehli baar se hi problem hai" â†’ Lifelong
- "Pehle theek tha, ab problem hai" â†’ Acquired

**Performance Anxiety Indicators:**
- "Partner ke saamne nahi hota" â†’ Works during masturbation, not with partner
- "Dar lagta hai" â†’ Avoiding sex due to fear
- "Tension mein rehta hun" â†’ Anxiety during sex

---

### Technical Troubleshooting

**If form doesn't show expected questions:**
- Check previous answer - conditional logic may have hidden sections
- Use browser back button ONLY if form supports it
- If unsure, start new form

**If user wants to change answer:**
- Forms should allow editing previous sections
- Verify downstream logic updates correctly
- Reconfirm critical answers (age, main issue)

**If technical error occurs:**
- Note where form stopped
- Document answers manually if needed
- Report bug to technical team with specifics

---

### Quality Assurance Checklist

Before submitting form:

- [ ] All red flags properly flagged
- [ ] Age verified (not under 18)
- [ ] Main concern clearly selected (ED/PE/Both)
- [ ] Medical history complete (especially medications)
- [ ] Section 6 branches completed based on main concern
- [ ] No contradictory answers (e.g., "no erections" but "hard enough for penetration")

---

### DO NOT DO

âŒ **Don't skip questions** - every question has diagnostic value  
âŒ **Don't interpret medical terminology** - use exact options provided  
âŒ **Don't make assumptions** - if unsure, ask user for clarification  
âŒ **Don't judge or react** - maintain professional, non-judgmental tone  
âŒ **Don't offer medical advice** - form is for data collection only  
âŒ **Don't proceed if red flags present** - follow escalation protocol  
âŒ **Don't rush** - accuracy more important than speed  

---

### Emergency Protocol

**If ANY of these occur during call:**

1. **Patient mentions chest pain, severe headache, or breathing difficulty**
   - Stop form immediately
   - Advise patient to call emergency services or go to hospital
   - Document in notes

2. **Patient expresses suicidal thoughts**
   - Stop form
   - Provide crisis helpline: Tele Manas 14416
   - Escalate to supervisor immediately

3. **Patient becomes aggressive or abusive**
   - Terminate call professionally
   - Document incident
   - Report to supervisor

---

**END OF DOCUMENT**

---

**Document Version:** 1.0  
**Last Updated:** November 6, 2025  
**Status:** Ready for Development  
**Next Steps:** Begin frontend development (Day 1-2 of MVP timeline)
