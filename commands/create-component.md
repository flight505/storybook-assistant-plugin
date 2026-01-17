---
description: Scaffold a new component with story, tests, and optional visual mockup following SOTA patterns
---

# Create Component Command

When the user invokes `/create-component`, guide them through creating a new component with all necessary files: component implementation, Storybook story, tests, and optional visual mockup.

## Workflow Overview

This command provides an interactive workflow for scaffolding production-ready components:

1. **Detect Framework**: Auto-detect project framework (React, Vue, Svelte)
2. **Gather Requirements**: Use AskUserQuestion to collect component details
3. **Generate Component**: Create component file with TypeScript/proper types
4. **Generate Story**: Create story file with variants and tests
5. **Optional Mockup**: Generate visual mockup if OPENROUTER_API_KEY available
6. **Summary**: Display created files and next steps

## Execution Steps

### Step 1: Detect Framework and Project Structure

Run framework detection to understand the project setup:

```bash
bash ${CLAUDE_PLUGIN_ROOT}/scripts/detect-framework.sh
```

This provides:
- Framework: react, vue, svelte
- Version: e.g., "18.2.0"
- TypeScript: yes/no
- Component directory: e.g., "src/components"

### Step 2: Ask User for Component Details

Use AskUserQuestion with serial questions to gather component requirements:

**Round 1: Component Category**

```javascript
AskUserQuestion({
  questions: [
    {
      question: "What category of component are you creating?",
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
  ]
})
```

**Round 2: Specific Component Type (Conditional)**

After receiving the category answer, ask for specific type. The pattern is:
1. Ask category-specific component type question (4 options)
2. Follow with name, testing, and mockup questions (same for all categories)

**Pattern Example (Form Control):**

```javascript
AskUserQuestion({
  questions: [
    // Question 1: Component type (category-specific)
    {
      question: "Which form control component?",
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
    },
    // Question 2: Component name (same for all categories)
    {
      question: "What should the component be named? (Use PascalCase)",
      header: "Name",
      multiSelect: false,
      options: [
        {
          label: "MyButton",
          description: "Example name - you can type your own via 'Other'"
        },
        {
          label: "UserCard",
          description: "Example name - you can type your own via 'Other'"
        }
      ]
    },
    // Question 3: Testing level (same for all categories)
    {
      question: "What level of testing should I include?",
      header: "Test Level",
      multiSelect: false,
      options: [
        {
          label: "Full Testing",
          description: "Recommended: Component + Story + Interaction tests + A11y tests"
        },
        {
          label: "Standard Testing",
          description: "Component + Story + Interaction tests"
        },
        {
          label: "Basic",
          description: "Component + Story only"
        },
        {
          label: "Minimal",
          description: "Component only (no story or tests)"
        }
      ]
    },
    // Question 4: Visual mockup (same for all categories)
    {
      question: "Should I generate a visual mockup for design reference?",
      header: "Mockup",
      multiSelect: false,
      options: [
        {
          label: "Yes",
          description: "Recommended: Creates AI mockup (requires OPENROUTER_API_KEY)"
        },
        {
          label: "No",
          description: "Generate component files only"
        }
      ]
    }
  ]
})
```

**Other Category Options (Question 1 varies by category):**

```javascript
// Layout category options:
{
  question: "Which layout component?",
  header: "Type",
  options: [
    { label: "Card", description: "Content container with optional header and footer" },
    { label: "Modal", description: "Overlay dialog with backdrop and focus management" },
    { label: "Container", description: "Layout wrapper with max-width and padding" },
    { label: "Grid", description: "Responsive grid system for complex layouts" }
  ]
}

// Data Display category options:
{
  question: "Which data display component?",
  header: "Type",
  options: [
    { label: "Table", description: "Data table with sorting, filtering, pagination" },
    { label: "List", description: "Vertical list with optional icons and actions" },
    { label: "DataGrid", description: "Advanced table with inline editing and grouping" },
    { label: "Chart", description: "Data visualization component (requires chart library)" }
  ]
}

// Navigation category options:
{
  question: "Which navigation component?",
  header: "Type",
  options: [
    { label: "Menu", description: "Dropdown or sidebar menu with nested items" },
    { label: "Tabs", description: "Horizontal or vertical tab navigation" },
    { label: "Breadcrumb", description: "Page location breadcrumb trail" },
    { label: "Navbar", description: "Top navigation bar with logo and links" }
  ]
}
```

**Note:** Questions 2-4 (Name, Testing, Mockup) are identical across all categories. Only Question 1 (component type) varies based on the category selected in Round 1.

### Step 3: Process User Input

After receiving answers from both rounds, process and prepare for generation:

```python
import json
import os

# Extract answers from Round 1 (Category)
component_category = answers_round1['What category of component are you creating?']

# Extract answers from Round 2 (Type and preferences)
# Question text varies by category, use the actual question text as key
component_type = answers_round2['Which form control component?']  # Or 'Which layout component?', etc.
component_name_raw = answers_round2['What should the component be named? (Use PascalCase)']
testing_level_raw = answers_round2['What level of testing should I include?']
generate_mockup_raw = answers_round2['Should I generate a visual mockup for design reference?']

# Clean component name (from "Other" text input)
component_name = component_name_raw.strip()

# Validate component name (PascalCase)
if not component_name[0].isupper():
    component_name = component_name[0].upper() + component_name[1:]

# Map testing level
testing_level_map = {
    "Full Testing": "full",
    "Standard Testing": "standard",
    "Basic": "basic",
    "Minimal": "minimal"
}
testing_level = testing_level_map.get(testing_level_raw, "full")

# Determine if mockup should be generated
generate_mockup = "Yes" in generate_mockup_raw and os.getenv('OPENROUTER_API_KEY')

# Get component template based on type
component_template = get_component_template(component_type, framework)
```

### Step 4: Generate Component File

Invoke the component scaffold script:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/component-scaffold/scripts/create_component.py \
  --name "${COMPONENT_NAME}" \
  --type "${COMPONENT_TYPE}" \
  --framework "${FRAMEWORK}" \
  --typescript \
  --output "${COMPONENT_DIR}/${COMPONENT_NAME}.tsx"
```

This creates the component file with:
- Proper TypeScript interfaces
- Framework-specific patterns (React hooks, Vue Composition API, Svelte stores)
- Props with sensible defaults based on component type
- Accessibility attributes
- JSDoc comments

### Step 5: Generate Story File

Use the existing story generation system:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/story-generation/scripts/generate_story.py \
  "${COMPONENT_DIR}/${COMPONENT_NAME}.tsx" \
  --level "${TESTING_LEVEL}" \
  --output "${COMPONENT_DIR}/${COMPONENT_NAME}.stories.tsx"
```

### Step 6: Generate Visual Mockup (Optional)

If user requested mockup and OPENROUTER_API_KEY is available:

```python
# Build context-aware prompt based on component type and project
mockup_prompt = f"""
Modern {component_type} component for {framework} application.
Component name: {component_name}
Style: Clean, professional, follows design system best practices
Include: {get_type_specific_elements(component_type)}
Color scheme: Modern, accessible (WCAG AA compliant)
Layout: Responsive, mobile-friendly
"""

# Generate mockup
python3 ${CLAUDE_PLUGIN_ROOT}/skills/visual-design/scripts/generate_mockup.py \
  "${mockup_prompt}" \
  --model "google/gemini-3.0-pro-image" \
  --output "${COMPONENT_DIR}/mockups/${COMPONENT_NAME}.png"
```

### Step 7: Display Summary

Show the user what was created:

```
═══════════════════════════════════════════════
  Component Created: ${COMPONENT_NAME}
═══════════════════════════════════════════════

Type: ${COMPONENT_TYPE}
Framework: ${FRAMEWORK}

Files Created:
  ✓ ${COMPONENT_DIR}/${COMPONENT_NAME}.tsx
  ✓ ${COMPONENT_DIR}/${COMPONENT_NAME}.stories.tsx
  ${MOCKUP_CREATED ? `✓ ${COMPONENT_DIR}/mockups/${COMPONENT_NAME}.png` : ''}

Component Features:
  ✓ TypeScript interfaces with proper types
  ✓ Accessibility attributes (ARIA labels, roles)
  ✓ ${PROPS_COUNT} props with sensible defaults
  ✓ JSDoc documentation
  ${TESTING_LEVEL === 'full' ? '✓ Interaction tests with play functions' : ''}
  ${TESTING_LEVEL === 'full' ? '✓ Accessibility tests with axe-core' : ''}

Next Steps:
  1. Review component: ${COMPONENT_DIR}/${COMPONENT_NAME}.tsx
  2. Customize props and styling as needed
  3. Run Storybook: npm run storybook
  4. View your component in the browser
  ${TESTING_LEVEL !== 'minimal' ? '5. Run tests: npm run test-storybook' : ''}
```

## Component Templates by Type

### Button Component Template

**Features:**
- Variants: primary, secondary, outline, ghost
- Sizes: small, medium, large
- States: disabled, loading
- Icon support
- Click handler

**Props Generated:**
```typescript
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  loading?: boolean;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  onClick?: () => void;
  children: React.ReactNode;
}
```

### Input Component Template

**Features:**
- Label and placeholder
- Error states and validation
- Helper text
- Required indicator
- Different input types

**Props Generated:**
```typescript
interface InputProps {
  label: string;
  type?: 'text' | 'email' | 'password' | 'number';
  placeholder?: string;
  value?: string;
  error?: string;
  helperText?: string;
  required?: boolean;
  disabled?: boolean;
  onChange?: (value: string) => void;
}
```

### Card Component Template

**Features:**
- Optional header and footer
- Image support
- Variants: elevated, outlined, flat
- Clickable option

**Props Generated:**
```typescript
interface CardProps {
  variant?: 'elevated' | 'outlined' | 'flat';
  image?: string;
  imageAlt?: string;
  header?: React.ReactNode;
  footer?: React.ReactNode;
  onClick?: () => void;
  children: React.ReactNode;
}
```

### Modal Component Template

**Features:**
- Open/close state management
- Focus trap
- Backdrop click to close
- ESC key handling
- Accessibility (aria-modal, role="dialog")

**Props Generated:**
```typescript
interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  size?: 'small' | 'medium' | 'large' | 'fullscreen';
  closeOnBackdropClick?: boolean;
  closeOnEsc?: boolean;
  children: React.ReactNode;
}
```

### Table Component Template

**Features:**
- Column definitions
- Sortable columns
- Row selection
- Pagination
- Loading and empty states

**Props Generated:**
```typescript
interface TableColumn<T> {
  key: keyof T;
  header: string;
  sortable?: boolean;
  render?: (value: T[keyof T], row: T) => React.ReactNode;
}

interface TableProps<T> {
  data: T[];
  columns: TableColumn<T>[];
  sortable?: boolean;
  selectable?: boolean;
  pagination?: boolean;
  pageSize?: number;
  loading?: boolean;
  emptyMessage?: string;
  onRowClick?: (row: T) => void;
}
```

### Custom Component Template

**For "Custom" type, ask follow-up questions:**

```javascript
AskUserQuestion({
  questions: [
    {
      question: "What props does your component need? (comma-separated, e.g., 'title, description, onClick')",
      header: "Component Props",
      multiSelect: false,
      options: [
        {
          label: "Enter prop names",
          description: "List props separated by commas"
        }
      ]
    },
    {
      question: "Should this component accept children?",
      header: "Children Support",
      multiSelect: false,
      options: [
        {
          label: "Yes - Component wraps content",
          description: "Add children prop (React.ReactNode)"
        },
        {
          label: "No - Self-contained component",
          description: "No children prop"
        }
      ]
    }
  ]
})
```

## Framework-Specific Patterns

### React Component Template

```typescript
import React from 'react';
import './{{COMPONENT_NAME}}.css';

export interface {{COMPONENT_NAME}}Props {
  {{PROPS}}
}

/**
 * {{COMPONENT_DESCRIPTION}}
 */
export function {{COMPONENT_NAME}}({
  {{PROP_DESTRUCTURING}}
}: {{COMPONENT_NAME}}Props) {
  {{COMPONENT_LOGIC}}

  return (
    <div className="{{COMPONENT_CLASS}}" {{ATTRIBUTES}}>
      {{COMPONENT_CONTENT}}
    </div>
  );
}

{{COMPONENT_NAME}}.displayName = '{{COMPONENT_NAME}}';
```

### Vue 3 Component Template

```vue
<script setup lang="ts">
interface {{COMPONENT_NAME}}Props {
  {{PROPS}}
}

const props = defineProps<{{COMPONENT_NAME}}Props>();
{{COMPONENT_LOGIC}}
</script>

<template>
  <div class="{{COMPONENT_CLASS}}" {{ATTRIBUTES}}>
    {{COMPONENT_CONTENT}}
  </div>
</template>

<style scoped>
.{{COMPONENT_CLASS}} {
  {{BASE_STYLES}}
}
</style>
```

### Svelte Component Template

```svelte
<script lang="ts">
  export let {{PROPS}};
  {{COMPONENT_LOGIC}}
</script>

<div class="{{COMPONENT_CLASS}}" {{ATTRIBUTES}}>
  {{COMPONENT_CONTENT}}
</div>

<style>
  .{{COMPONENT_CLASS}} {
    {{BASE_STYLES}}
  }
</style>
```

## Component Type Defaults

The script provides sensible defaults based on component type:

| Type | Default Props | Variants | Features |
|------|--------------|----------|----------|
| Button | variant, size, disabled, loading, onClick, children | 4 variants, 3 sizes | Icon support, loading state |
| Input | label, type, value, error, onChange | 4 types | Validation, helper text |
| Card | variant, image, header, footer, children | 3 variants | Clickable, image support |
| Modal | isOpen, onClose, title, size, children | 4 sizes | Focus trap, ESC/backdrop close |
| Table | data, columns, sortable, pagination | - | Sorting, selection, pagination |
| Form | onSubmit, loading, error | - | Validation, error handling |
| Navigation | items, activeItem, onChange | - | Routing support |
| Layout | children, spacing, direction | - | Flex/Grid layout |

## Error Handling

**Component Already Exists:**
```
⚠ Component already exists: src/components/Button.tsx

Options:
  1. Choose a different name
  2. Overwrite existing (use --force flag)
  3. Cancel operation
```

**Invalid Component Name:**
```
✗ Invalid component name: "my-button"

Component names must:
  • Start with uppercase letter (PascalCase)
  • Contain only letters and numbers
  • Not contain spaces or special characters

Examples: MyButton, UserCard, DataTable
```

**Framework Detection Failed:**
```
✗ Could not detect project framework

Please specify framework manually:
  /create-component --framework react
  /create-component --framework vue
  /create-component --framework svelte
```

**No Component Directory:**
```
⚠ Could not find component directory

Suggested directories:
  • src/components
  • src/lib/components
  • components

Create directory? (y/n)
```

## Advanced Usage

### Create Component with Specific Props

```bash
# Custom props
/create-component --name MyButton --type button --props "label:string,onClick:function,disabled:boolean"
```

### Create Component in Specific Directory

```bash
# Specify output directory
/create-component --name UserCard --type card --output src/features/user/components
```

### Create Multiple Variants

```bash
# Generate component with custom variants
/create-component --name StatusBadge --type custom --variants "success,warning,error,info"
```

## Platform-Specific Considerations

### Tauri Components

If project uses Tauri, automatically include IPC mocking in stories:

```typescript
// Auto-generated in story file
export const WithTauriAPI: Story = {
  args: { /* ... */ },
  decorators: [
    (Story) => {
      if (typeof window !== 'undefined') {
        window.__TAURI__ = {
          invoke: async (cmd) => ({ success: true }),
        };
      }
      return <Story />;
    },
  ],
};
```

### Electron Components

If project uses Electron, include IPC mocking:

```typescript
// Auto-generated in story file
export const WithElectronAPI: Story = {
  args: { /* ... */ },
  decorators: [
    (Story) => {
      if (typeof window !== 'undefined') {
        window.api = {
          // Mock electron API
        };
      }
      return <Story />;
    },
  ],
};
```

## Notes

- Always generate TypeScript components (even for JS projects)
- Include accessibility attributes by default (aria-label, role, etc.)
- Follow framework-specific best practices (React hooks, Vue Composition API)
- Generate CSS module or scoped styles by default
- Include JSDoc comments for props
- Use semantic HTML elements
- Ensure keyboard navigation support
- Include loading and error states where applicable
