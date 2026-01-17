# AskUserQuestion Implementation Review

**Project:** storybook-assistant
**Review Date:** 2026-01-17
**Reviewer:** Claude (using askuserquestion skill)
**Scope:** Commands using AskUserQuestion tool

---

## Executive Summary

**Overall Rating:** ⭐⭐⭐⭐ (4/5) - Strong implementation with minor improvements needed

The Storybook Assistant plugin demonstrates **excellent** understanding of AskUserQuestion best practices across most commands. The implementations are context-aware, well-structured, and follow schema requirements. However, there are several opportunities for optimization and consistency improvements.

### Key Strengths ✅
- Context-aware questions (dynamic options based on detected framework/platform)
- Proper schema compliance (headers ≤12 chars, 2-4 options, required fields)
- Good use of multiSelect for non-exclusive choices
- Descriptive option descriptions explaining trade-offs
- Serial questioning patterns for complex workflows

### Areas for Improvement ⚠️
- Some headers could be shorter for better TUI display
- Inconsistent label verbosity (some exceed 1-5 word guideline)
- A few questions use single-option patterns (antipattern)
- Missing explicit multiSelect in some examples
- Could benefit from conditional follow-up patterns

---

## Detailed Analysis by Command

### 1. `/setup-storybook` Command

**File:** `commands/setup-storybook.md`

#### ✅ Strengths

**Context-Aware Questions:**
```javascript
question: `Which testing features do you want for your ${FRAMEWORK} components?`
```
✅ Excellent - Dynamically inserts detected framework name

**Proper MultiSelect Usage:**
```javascript
{
  question: "Which testing features...",
  multiSelect: true,  // ✅ Correct - features are not mutually exclusive
  options: [...]
}
```

**Good Descriptions:**
```javascript
{
  label: "Accessibility Tests (Recommended)",
  description: "WCAG compliance testing with axe-core (catches 57% of issues automatically)"
}
```
✅ Provides context (tool name, percentage) + value proposition

**Schema Compliance:**
- Header: "Testing" (7 chars) ✅ Well under 12 char limit
- Options: 4 items ✅ Within 2-4 range
- Descriptions: All non-empty ✅

#### ⚠️ Areas for Improvement

**Label Verbosity:**
```javascript
// Current
label: "Interaction Tests (Recommended)"

// Better (move "Recommended" to description)
label: "Interaction Tests"
description: "Test user interactions with play functions (Recommended)"
```

**Reasoning:** Labels should be 1-5 words. "(Recommended)" adds noise to the label when it could be in the description.

**Design System Question - Single Option Antipattern:**
```javascript
// Line 98-100 suggests this pattern:
options: [
  {
    label: "Enter custom name",
    description: "Use PascalCase (e.g., MyButton, UserCard, DataTable)"
  }
]
```

❌ **VIOLATION:** Only 1 option (minimum is 2)
**Fix:** Either provide 2+ real options OR use free-text input via "Other" in a different question

#### 📋 Recommendations

1. **Shorten labels with recommendations:**
   ```diff
   - label: "Interaction Tests (Recommended)"
   + label: "Interaction Tests"
   + description: "Recommended: Test user interactions with play functions..."
   ```

2. **Fix single-option questions:**
   ```javascript
   // Instead of asking for component name with 1 option, use:
   {
     question: "What component naming convention do you prefer?",
     header: "Naming",
     multiSelect: false,
     options: [
       { label: "PascalCase", description: "MyButton, UserCard (Recommended)" },
       { label: "kebab-case", description: "my-button, user-card" }
     ]
   }
   // Then user types actual name via "Other"
   ```

---

### 2. `/generate-stories` Command

**File:** `commands/generate-stories.md`

#### ✅ Strengths

**Dynamic Component Options:**
```python
component_options.append({
    "label": f"{name} ({path.split('/')[-1]})",
    "description": f"{props_count} props • {comp_type} • {variant_count} variants detected"
})
```
✅ Excellent - Provides rich metadata to help user decide

**Clear Testing Level Options:**
```javascript
{
  label: "Full Testing (Recommended)",
  description: "Interaction tests, accessibility tests, multiple variants, and edge cases"
}
```
✅ Clear hierarchy and explicit about what's included

**Proper MultiSelect:**
```javascript
{
  question: `I found ${components.length} components. Which should I generate stories for?`,
  multiSelect: true  // ✅ Correct - user can select multiple components
}
```

#### ⚠️ Areas for Improvement

**Header Length:**
```javascript
// Current
header: "Testing Level"  // 13 chars ❌ EXCEEDS 12 char limit

// Better
header: "Test Level"  // 10 chars ✅
```

**Label Structure in Component Options:**
```python
label: f"{name} ({path.split('/')[-1]})"
# Example: "Button (Button.tsx)"

# Could be simplified to:
label: name  # Just "Button"
description: f"{path} • {props_count} props • {variant_count} variants"
```

**Reasoning:** Keep labels concise (component name only), move file path to description for better readability.

#### 📋 Recommendations

1. **Fix header length violation:**
   ```diff
   - header: "Testing Level"
   + header: "Test Level"
   ```

2. **Optimize component option labels:**
   ```python
   component_options.append({
       "label": name,  # Cleaner
       "description": f"{path} • {props_count} props • {comp_type} • {variant_count} variants"
   })
   ```

3. **Consider conditional follow-up:**
   ```javascript
   // If user selects "Full Testing", ask:
   {
     question: "Which accessibility standards should tests enforce?",
     header: "A11y Standard",
     multiSelect: false,
     options: [
       { label: "WCAG 2.1 AA", description: "Standard compliance level" },
       { label: "WCAG 2.2 AA", description: "Latest standard (Recommended)" },
       { label: "WCAG 2.1 AAA", description: "Highest compliance level" }
     ]
   }
   ```

---

### 3. `/create-component` Command

**File:** `commands/create-component.md`

#### ✅ Strengths

**Comprehensive Component Type Options:**
```javascript
options: [
  { label: "Button", description: "Interactive button with variants (primary, secondary, etc.)" },
  { label: "Input", description: "Form input with validation and states" },
  { label: "Card", description: "Content container with optional header, footer, image" },
  // ... 9 total options ❌ WAIT, this is TOO MANY
]
```

**Wait, this is a VIOLATION!** Max 4 options per question.

**Clear Testing Levels:**
```javascript
{
  label: "Full Testing (Recommended)",
  description: "Component + Story + Interaction tests + A11y tests"
}
```
✅ Explicit about deliverables

**Yes/No Pattern for Mockup:**
```javascript
{
  question: "Should I generate a visual mockup for design reference?",
  multiSelect: false,
  options: [
    { label: "Yes - Generate AI mockup (Recommended)", ... },
    { label: "No - Skip mockup", ... }
  ]
}
```
✅ Good use of binary choice

#### ❌ Critical Issues

**SCHEMA VIOLATION - Too Many Options:**
```javascript
// Current: 9 options for component type
options: [
  { label: "Button", ... },
  { label: "Input", ... },
  { label: "Card", ... },
  { label: "Modal / Dialog", ... },  // "/" in label - keep it simple
  { label: "Table / DataGrid", ... },
  { label: "Form", ... },
  { label: "Navigation (Menu/Tabs)", ... },
  { label: "Layout (Container/Grid)", ... },
  { label: "Custom", ... }
]
```

❌ **9 options exceeds max of 4**

**Fix Options:**

**Option A: Serial Questions (Recommended)**
```javascript
// Question 1: Category
{
  question: "What category of component?",
  header: "Category",
  multiSelect: false,
  options: [
    { label: "Interactive", description: "Buttons, inputs, forms, controls" },
    { label: "Layout", description: "Containers, grids, cards, modals" },
    { label: "Navigation", description: "Menus, tabs, breadcrumbs" },
    { label: "Data Display", description: "Tables, lists, data grids" }
  ]
}

// Question 2: Specific Type (based on Q1 answer)
// If "Interactive":
{
  question: "Which interactive component?",
  header: "Type",
  multiSelect: false,
  options: [
    { label: "Button", description: "Clickable action button" },
    { label: "Input", description: "Text input field" },
    { label: "Form", description: "Complete form with validation" }
  ]
}
```

**Option B: Group into Categories**
```javascript
{
  question: "What type of component?",
  header: "Type",
  multiSelect: false,
  options: [
    { label: "Form Component", description: "Button, Input, Checkbox, Select" },
    { label: "Layout Component", description: "Card, Container, Grid, Modal" },
    { label: "Data Component", description: "Table, List, DataGrid" },
    { label: "Navigation", description: "Menu, Tabs, Breadcrumb" }
  ]
}
// Then ask follow-up for specific type within category
```

**Label Issues:**
```javascript
// Current
label: "Modal / Dialog"
label: "Table / DataGrid"
label: "Navigation (Menu/Tabs)"
label: "Layout (Container/Grid)"

// Better - Pick one, move alternative to description
label: "Modal"
description: "Overlay dialog with backdrop and focus management"

label: "Table"
description: "Data table or DataGrid with sorting, filtering, pagination"

label: "Menu"
description: "Navigation menu or tabbed interface"

label: "Container"
description: "Layout container or grid system"
```

#### 📋 Recommendations

1. **CRITICAL: Fix option count violation using serial questions**

2. **Simplify labels:**
   ```diff
   - label: "Modal / Dialog"
   + label: "Modal"

   - label: "Navigation (Menu/Tabs)"
   + label: "Menu"
   ```

3. **Add conditional follow-up for Custom:**
   ```javascript
   // If user selects "Custom", ask:
   {
     question: "What props should the custom component have?",
     header: "Props",
     multiSelect: true,
     options: [
       { label: "Children", description: "Render child elements" },
       { label: "ClassName", description: "CSS class customization" },
       { label: "Variant", description: "Style variants (primary, secondary)" },
       { label: "State", description: "Stateful props (disabled, loading)" }
     ]
   }
   ```

---

## Schema Compliance Summary

| Command | Questions | Options/Q | Headers ≤12 | multiSelect | Labels 1-5 words | Issues |
|---------|-----------|-----------|-------------|-------------|------------------|--------|
| `/setup-storybook` | 2-3 | 4, 3 | ✅ | ✅ | ⚠️ Some verbose | Minor |
| `/generate-stories` | 2 | Dynamic, 4 | ❌ "Testing Level" | ✅ | ⚠️ Some verbose | 1 violation |
| `/create-component` | 4 | **9** ❌, 2, 4, 2 | ✅ | ✅ | ⚠️ Some verbose | **CRITICAL** |

---

## Best Practices Assessment

### ✅ What You're Doing Right

1. **Context-Aware Questions**
   - Dynamic framework/platform detection
   - Customized option labels based on environment
   - Smart defaults based on project analysis

2. **Good Description Quality**
   - Explain trade-offs ("stateless, scalable" vs "simpler, better for web apps")
   - Include metrics ("catches 57% of issues")
   - Provide tool names (axe-core, Vitest, Playwright)

3. **Proper MultiSelect Usage**
   - Testing features: `multiSelect: true` ✅
   - Framework choice: `multiSelect: false` ✅
   - Yes/No decisions: `multiSelect: false` ✅

4. **Serial Questioning Pattern**
   - `/setup-storybook` uses 2-3 rounds based on context
   - Conditional questions based on detected design system

### ⚠️ What Needs Improvement

1. **Label Verbosity**
   ```javascript
   // Too verbose
   label: "Interaction Tests (Recommended)"
   label: "Yes - Generate AI mockup (Recommended)"

   // Better
   label: "Interaction Tests"
   description: "Recommended: Test user interactions..."
   ```

2. **Header Length**
   - "Testing Level" (13 chars) exceeds 12 char limit
   - Should be "Test Level" (10 chars)

3. **Option Count**
   - `/create-component` has 9 options (max is 4)
   - Needs serial questions or categorization

4. **Single-Option Antipattern**
   - Some questions have only 1 option (violates 2-4 constraint)
   - Use "Other" for free text instead

### 🚀 Advanced Patterns to Consider

1. **Conditional Follow-Up Questions**
   ```javascript
   // After user selects "OAuth" for auth:
   {
     question: "Which OAuth providers?",
     header: "Providers",
     multiSelect: true,
     options: [
       { label: "Google", description: "Google OAuth 2.0" },
       { label: "GitHub", description: "GitHub OAuth" },
       { label: "Microsoft", description: "Azure AD / Microsoft" }
     ]
   }
   ```

2. **Spec Confirmation Pattern**
   ```javascript
   // After gathering all requirements, confirm:
   {
     question: "I'll create a Button component with React, TypeScript, and full testing. Proceed?",
     header: "Confirm",
     multiSelect: false,
     options: [
       { label: "Yes", description: "Looks good, proceed" },
       { label: "Modify", description: "I want to change something" }
     ]
   }
   ```

3. **Progressive Disclosure**
   ```javascript
   // Start simple:
   Q1: Component category (4 options)

   // Then get specific:
   Q2: Exact component type within category (3-4 options)

   // Then customize:
   Q3: Features to include (multiSelect, 4 options)

   // Finally confirm:
   Q4: Review and proceed
   ```

---

## Priority Fixes

### 🔴 Critical (Must Fix)

1. **`/create-component`: Reduce component type options from 9 to ≤4**
   - Use serial questions or categorization
   - See Option A or B in detailed analysis above

### 🟡 Important (Should Fix)

2. **`/generate-stories`: Fix "Testing Level" header length**
   ```diff
   - header: "Testing Level"
   + header: "Test Level"
   ```

3. **All commands: Shorten labels with "(Recommended)"**
   ```diff
   - label: "Interaction Tests (Recommended)"
   + label: "Interaction Tests"
   + description: "Recommended: Test user interactions..."
   ```

### 🟢 Nice to Have (Consider)

4. **Add conditional follow-up questions for advanced workflows**
5. **Implement spec confirmation pattern before generation**
6. **Optimize component option labels (just name, not file path)**

---

## Example: Refactored `/create-component` Questions

### Before (VIOLATION - 9 options)
```javascript
{
  question: "What type of component are you creating?",
  header: "Component Type",
  multiSelect: false,
  options: [
    { label: "Button", description: "..." },
    { label: "Input", description: "..." },
    { label: "Card", description: "..." },
    { label: "Modal / Dialog", description: "..." },
    { label: "Table / DataGrid", description: "..." },
    { label: "Form", description: "..." },
    { label: "Navigation (Menu/Tabs)", description: "..." },
    { label: "Layout (Container/Grid)", description: "..." },
    { label: "Custom", description: "..." }
  ]
}
```

### After (COMPLIANT - Serial Questions)
```javascript
// Question 1: Category
{
  question: "What category of component?",
  header: "Category",
  multiSelect: false,
  options: [
    {
      label: "Form Control",
      description: "Interactive elements like buttons, inputs, checkboxes"
    },
    {
      label: "Layout",
      description: "Containers, cards, grids, modals for structuring content"
    },
    {
      label: "Data Display",
      description: "Tables, lists, data grids for showing information"
    },
    {
      label: "Navigation",
      description: "Menus, tabs, breadcrumbs for site navigation"
    }
  ]
}

// Question 2: Specific Type (conditional on Q1 answer)
// If user selected "Form Control":
{
  question: "Which form control?",
  header: "Type",
  multiSelect: false,
  options: [
    {
      label: "Button",
      description: "Action button with variants (primary, secondary, etc.)"
    },
    {
      label: "Input",
      description: "Text input field with validation and states"
    },
    {
      label: "Checkbox",
      description: "Toggle control for boolean options"
    },
    {
      label: "Select",
      description: "Dropdown menu for selecting from options"
    }
  ]
}

// If user selected "Layout":
{
  question: "Which layout component?",
  header: "Type",
  multiSelect: false,
  options: [
    {
      label: "Card",
      description: "Content container with optional header and footer"
    },
    {
      label: "Modal",
      description: "Overlay dialog with backdrop and focus management"
    },
    {
      label: "Container",
      description: "Layout wrapper with max-width and padding"
    },
    {
      label: "Grid",
      description: "Responsive grid system for complex layouts"
    }
  ]
}

// Similar patterns for "Data Display" and "Navigation"
```

---

## Conclusion

The Storybook Assistant plugin demonstrates **strong understanding** of AskUserQuestion best practices with excellent context-awareness and generally good schema compliance. The primary issues are:

1. **One critical violation** (9 options in `/create-component`)
2. **Minor header length issue** ("Testing Level" → "Test Level")
3. **Label verbosity** (easily fixed by moving recommendations to descriptions)

**Recommended Action Plan:**

1. ✅ Refactor `/create-component` to use serial questions (highest priority)
2. ✅ Fix header length in `/generate-stories`
3. ✅ Clean up labels across all commands (remove parentheticals)
4. ✅ Consider implementing conditional follow-up patterns for richer workflows

**Overall Grade:** B+ (would be A with fixes)

---

**Review Completed:** 2026-01-17
**Next Review:** After implementing priority fixes
