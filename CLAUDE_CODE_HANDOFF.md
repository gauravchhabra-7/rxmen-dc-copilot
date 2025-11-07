# RxMen Discovery Call Form - Claude Code Handoff Document

**Date:** November 6, 2025  
**Project:** RxMen Discovery Call Copilot  
**Status:** Ready for full implementation  
**Tool:** Claude Code (Web)

---

## 🎯 PROJECT OVERVIEW

### What We're Building
An AI-powered web form that agents use during live video discovery calls to collect patient information for ED/PE root cause analysis. The form feeds into Claude API with RAG (medical textbooks) to generate accurate, simple explanations.

### Critical Context
- **Users:** RxMen agents (described as "not very smart" - need EXTREME simplicity)
- **Usage:** During LIVE video calls (high cognitive load, multitasking)
- **Volume:** 6,000+ monthly discovery calls
- **Medical:** Wrong diagnosis harms patients AND conversion rates
- **Speed:** Must be fast (<500ms load, <3s AI response)

---

## 📚 REFERENCE DOCUMENTS

### Available in Project
1. **RxMen_Discovery_Call_Form_Complete_Specification.md** (2,293 lines)
   - Complete form structure, all questions, validation rules
   - 7 sections with conditional logic
   - Red flag protocols
   
2. **RxMen_Tech_Stack_and_UX_Design_Decision.md**
   - Tech stack rationale (plain HTML/CSS/JS)
   - Initial UI design patterns
   
3. **section1-client-information.html** (prototype)
   - First section implementation
   - Needs refinement per new decisions

---

## ✅ FINALIZED DECISIONS

### 1. Form Display Strategy
**APPROVED: Single-page flowing form with accordion sections**

**Structure:**
```
[Sticky Progress Header]
▼ Section 1: Client Information ✓ (9/9 completed)
   [Collapsed - click to edit]

▼ Section 2: Main Concern ⏵ (2/3 completed)
   Question 2.1: [Visible]
   Question 2.2: [Visible]
   Question 2.3: [Empty - needs answer]

▶ Section 3: Medical & Lifestyle
   [Not started - click to expand]

[Continue for all sections...]

[Single Submit Button at end]
```

**Behavior:**
- All sections on one page
- Completed sections auto-collapse (show summary)
- Click section header to expand/edit
- Smooth scroll between sections
- One submit button at the very end

---

### 2. Output Display Strategy
**APPROVED: Side Panel (60/40 split)**

**Layout:**
```
┌─────────────────────────┬───────────────────────┐
│  FORM (60%)             │  AI OUTPUT (40%)      │
│  ─────────────          │  ───────────          │
│  [All sections scroll]  │  PRIMARY CAUSE:       │
│                         │  [Medical term]       │
│                         │                       │
│                         │  EXPLANATION:         │
│                         │  [Simple Hindi/Eng]   │
│                         │                       │
│  [Submit Button]        │  [Copy] [Download]    │
│                         │  [Re-submit]          │
└─────────────────────────┴───────────────────────┘
```

**Features:**
- Side-by-side layout (desktop)
- Form stays editable after submission
- Output panel is sticky/scrollable
- Re-submit button for instant re-analysis
- Both visible simultaneously

**Responsive:**
- Desktop (>1200px): 60/40 split
- Tablet (768-1200px): 50/50 split
- Mobile (<768px): Stack vertically (not MVP priority)

---

### 3. Validation & Error Handling
**APPROVED: Auto-scroll + Summary Banner**

**When Submit Clicked with Incomplete Fields:**

```
┌─────────────────────────────────────────────┐
│ ⚠️ 4 REQUIRED FIELDS MISSING                │ ← Sticky banner
│ Click to jump: Age | Height | Occupation    │ ← Clickable links
│              | First Consultation           │
│                                    [×Close] │
├─────────────────────────────────────────────┤
│ [Auto-scrolls to FIRST incomplete field]   │
│                                             │
│ ┌─────────────────────────┐                │
│ │ Age *     ← Pulsing red border          │
│ │ ┌─────────────────────┐ │                │
│ │ │ [empty]             │ │                │
│ │ └─────────────────────┘ │                │
│ │ ⚠️ This field is required│                │
│ └─────────────────────────┘                │
```

**Logic:**
1. Validate entire form on submit
2. Collect all incomplete/invalid fields
3. Show sticky banner with ALL incomplete fields (clickable)
4. Auto-scroll to FIRST incomplete field (smooth animation)
5. Add pulsing red border to ALL incomplete fields
6. Banner stays until ALL fields complete
7. Click field name in banner → jumps to that field

---

### 4. UI Improvements Required

#### A. Toggle Border Fix
**Issue:** Border extends full width  
**Fix:** Make border wrap content only
```css
.toggle-switch {
    display: inline-flex;
    width: auto;  /* Not 100% */
}
```

#### B. Smart Field Grouping
**Side-by-side on desktop (>768px):**
- Height + Weight (same row)
- Name + Age (same row)
- Feet + Inches inputs (same row)

**Full width:**
- City (needs space for long names)
- All radio/checkbox groups
- Text areas

#### C. Field Focus Animation
**On focus:**
- Smooth border color change to brand blue
- Subtle shadow glow (0 0 0 3px rgba(28, 91, 217, 0.1))
- Smooth transition (300ms)

**On incomplete after submit:**
- Pulsing red border animation (2s loop)
- Error message fades in below field

#### D. Progress Indicator (Sticky Header)
```
┌──────────────────────────────────────────────┐
│ RxMen Discovery Form          Section 2/7    │
│ ●●○○○○○ 25% Complete                        │
└──────────────────────────────────────────────┘
```
- Always visible at top (position: sticky)
- Updates as sections complete
- Shows current section number

#### E. Section State Indicators
```
✓ Section 1: Client Information (9/9) ← Green check, collapsible
⏵ Section 2: Main Concern (2/3)       ← Blue arrow, expanded
  Section 3: Medical & Lifestyle      ← Gray, not started
```

---

## 🏗️ TECHNICAL SPECIFICATIONS

### Tech Stack
- **Frontend:** Plain HTML5 + CSS3 + Vanilla JavaScript
- **No frameworks** (React, Vue, etc.) - keep it simple
- **No build tools** - runs directly in browser
- **Font:** Geist (or fallback to system fonts)

### File Structure
```
rxmen-discovery-form/
├── index.html              ← Main form (all 7 sections)
├── assets/
│   ├── css/
│   │   ├── styles.css      ← Global styles
│   │   ├── form.css        ← Form components
│   │   ├── output.css      ← Side panel
│   │   └── animations.css  ← Transitions/animations
│   ├── js/
│   │   ├── main.js         ← Initialization
│   │   ├── validation.js   ← Form validation logic
│   │   ├── sections.js     ← Accordion behavior
│   │   ├── submit.js       ← Form submission
│   │   └── utils.js        ← Helper functions
│   └── images/
│       └── rxmen-logo.png
├── docs/
│   ├── specification.md
│   └── decisions.md
└── README.md
```

### Color Palette (Free Hand - Suggestions)
**Primary:**
- Brand Blue: #1C5BD9 (use for CTAs, focus states)
- Dark Blue: #072178 (headers, important text)

**Neutrals:**
- Black: #121212 (body text)
- Gray 1: #40434A (secondary text)
- Gray 2: #707070 (helper text)
- Gray 3: #CBCDD0 (borders, disabled)

**Status:**
- Error Red: #FF0000 (errors, required indicators)
- Success Green: #28A745 (completed sections)
- Warning Orange: #FF9800 (red flags section)

**Backgrounds:**
- White: #FFFFFF (main background)
- Light Blue: #EFF5FF (hover states, selected options)
- Warning BG: #FFF4E6 (red flags section background)

---

## 📋 FORM STRUCTURE (All 7 Sections)

### Section 1: Client Information (9 questions)
1. Full Name (text, 2-100 chars)
2. Age (number, 11-99, RED FLAG: <18 stops call)
3. Height (toggle: cm OR ft-in, with conversion)
4. Weight (number, 40-200 kg)
5. City (text, 3-50 chars)
6. Occupation (6 radio options)
7. Relationship Status (4 radio options)
8. First Consultation (radio: Yes/No, conditional: previous treatments)
9. Safety Screening (4 radio options, RED FLAG: certain answers stop call)

### Section 2: Main Concern (3 questions)
1. Main issue: ED | PE | Both (determines Section 6 display)
2. Duration: options from <1 month to >2 years
3. Context: when issue occurs (options provided)

### Section 3: Medical & Lifestyle (7 questions)
1. Chronic conditions (multi-select checkboxes)
2. Current medications (multi-select checkboxes)
3. Smoking status (radio buttons)
4. Alcohol consumption (radio buttons)
5. Exercise frequency (radio buttons)
6. Sleep hours (number input)
7. Stress level (1-10 scale)

### Section 4: Masturbation & Behavioral History (4 questions)
1. Frequency (radio buttons)
2. Porn usage (radio buttons)
3. Porn frequency (conditional, appears if porn = yes)
4. Death grip concern (radio buttons)

### Section 5: Relationship Dynamics (1 question - CONDITIONAL)
**ONLY shows if Section 1.7 = "Married" OR "In a relationship"**
1. Relationship satisfaction (1-10 scale with labels)

### Section 6A: ED Branch (CONDITIONAL)
**Shows if Section 2.1 = "ED" OR "Both"**
- Questions about erection quality, timing, situational factors
- See specification doc for complete list

### Section 6B: PE Branch (CONDITIONAL)
**Shows if Section 2.1 = "PE" OR "Both"**
- Questions about ejaculation timing, control, patterns
- See specification doc for complete list

---

## 🔄 CONDITIONAL LOGIC SUMMARY

### Key Conditional Rules:
1. **Section 5** shows ONLY if relationship_status = "married" OR "in_relationship"
2. **Section 6A** shows ONLY if main_issue = "ED" OR "Both"
3. **Section 6B** shows ONLY if main_issue = "PE" OR "Both"
4. **Previous treatments** checkboxes show ONLY if first_consultation = "No"
5. **Porn frequency** shows ONLY if porn_usage = "Yes"

---

## ⚠️ RED FLAG PROTOCOLS

### Critical Actions Required:

**Age < 18:**
- **STOP FORM IMMEDIATELY**
- Show alert: "Cannot proceed - patient is a minor. Decline and document."
- Disable submit button
- Form cannot be submitted

**Age > 80:**
- **FLAG (warning, not stop)**
- Show message: "In-person consultation required"
- Allow form to continue
- Flag in output for doctor review

**Red Flags Section (Question 1.9):**
- **Severe pain:** Escalate - possible torsion/infection
- **Blood in urine/semen:** STOP CALL - immediate urologist referral
- **Priapism (4+ hours):** EMERGENCY - send to hospital immediately

These actions should appear in the **AI output panel**, not as inline form alerts.

---

## 🎨 UI/UX DESIGN PRINCIPLES

### Agent-Centric Design:
1. **Minimize cognitive load** - clear hierarchy, no clutter
2. **Speed over aesthetics** - fast interactions, instant feedback
3. **Forgiving UX** - easy to go back and edit
4. **Obvious next steps** - clear visual cues for what to do
5. **Error prevention** - validate early, guide corrections

### Specific Considerations:
- Agents are multitasking (video call + typing)
- May be in noisy environment
- Need to read explanations to patients in real-time
- High pressure - 6,000+ calls per month
- Mistakes are costly (medical + business impact)

### Do NOT Include:
- Complex animations (distracting)
- Too many colors (overwhelming)
- Small fonts (<14px for body text)
- Hidden features (no hamburger menus)
- Multi-step modals (keep it flat)

---

## 🚀 DEVELOPMENT PRIORITIES

### Phase 1: MVP Structure (Week 1)
- [ ] Create complete HTML with all 7 sections
- [ ] Build accordion section logic
- [ ] Implement side panel layout (empty for now)
- [ ] Add basic styling (professional, clean)
- [ ] Test in browser (Chrome, Firefox)

### Phase 2: Validation & UX (Week 1)
- [ ] Add real-time validation (as user types)
- [ ] Implement auto-scroll to incomplete fields
- [ ] Build summary banner (clickable field jumps)
- [ ] Add pulsing animation on incomplete fields
- [ ] Test with sample data

### Phase 3: Conditional Logic (Week 2)
- [ ] Show/hide Section 5 based on relationship status
- [ ] Show/hide Section 6A/6B based on main issue
- [ ] Test all conditional paths

### Phase 4: Polish & Testing (Week 2)
- [ ] Add field focus animations
- [ ] Implement progress indicator
- [ ] Test keyboard navigation
- [ ] Performance optimization
- [ ] Cross-browser testing

### Future (Post-MVP):
- Claude API integration
- Google Sheets logging
- PDF download functionality
- Multi-language support (Hinglish, Hindi, English)

---

## 📊 SUCCESS METRICS

### Technical Performance:
- Form loads in <500ms
- Submit processes in <3s (including validation)
- No JavaScript errors in console
- Works on Chrome, Firefox, Safari (desktop)

### User Experience:
- Agent can complete form in <10 minutes
- <5 clicks to find/fix incomplete fields
- Clear visual feedback on every action
- Zero confusion on what to do next

### Medical Accuracy:
- All required fields enforced
- Red flags properly handled
- Data validation prevents nonsense inputs
- Clear data structure for AI processing

---

## 💻 STARTING POINTS FOR CLAUDE CODE

### Immediate Tasks:

1. **Review uploaded Section 1 HTML**
   - Check structure, styling, interactions
   - Identify what to keep vs. rebuild

2. **Create project file structure**
   - Set up folders: assets/css, assets/js, docs
   - Create empty files: index.html, styles.css, main.js, etc.

3. **Build main HTML skeleton**
   - Header with progress indicator
   - Form container (left 60%)
   - Output panel (right 40%)
   - All 7 sections as collapsible accordions

4. **Implement core CSS**
   - Layout (60/40 split, sticky header)
   - Form components (inputs, radios, checkboxes)
   - Accordion styling
   - Side panel styling

5. **Add basic JavaScript**
   - Accordion open/close
   - Form field interactions
   - Validation on submit
   - Auto-scroll to first incomplete

### Questions to Ask Me:
- Design specifics (spacing, font sizes, etc.)
- Edge case handling
- Validation rule clarifications
- Any ambiguity in specification

---

## 📞 CONTACT & SUPPORT

**Project Owner:** Chief of Staff, RxMen  
**Medical Context:** ED/PE Discovery Calls  
**Timeline:** 15-day MVP (started November 6, 2025)

**Critical Reminders:**
- This is MEDICAL software - accuracy is non-negotiable
- Agents need extreme simplicity
- Fast performance is required (live calls)
- Wrong diagnosis harms patients + business

---

## ✅ CHECKLIST FOR CLAUDE CODE SESSION 1

```
[ ] Upload specification documents
[ ] Upload Section 1 HTML prototype
[ ] Create project folder structure
[ ] Build main index.html skeleton (all sections)
[ ] Create styles.css with layout (60/40 split)
[ ] Add basic accordion JavaScript
[ ] Test in browser - does it load?
[ ] Review with me before proceeding to validation
```

---

**Ready to build! 🚀**

Let me know if you need clarification on any decisions or specifications.
