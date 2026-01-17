---
description: Generate story files for existing components with interaction tests, accessibility checks, and multiple variants
---

# Generate Stories Command

When the user invokes `/generate-stories`, scan the project for components and generate Storybook stories with SOTA patterns including interaction tests, accessibility checks, and intelligent variant generation.

## Workflow Overview

This command integrates the component parser system with an interactive workflow:

1. **Scan**: Discover all components in the project using `scan_components.py`
2. **Present**: Show discovered components to user via AskUserQuestion
3. **Select**: User selects components and testing preferences
4. **Generate**: Create story files using `generate_story.py` for each selected component
5. **Report**: Display summary of generated files

## Execution Steps

### Step 1: Scan for Components

Run the component discovery workflow:

```bash
bash ${CLAUDE_PLUGIN_ROOT}/commands/scripts/generate-stories-workflow.sh src json
```

This script:
- Scans the project using `scan_components.py`
- Discovers all React, Vue, and Svelte components
- Parses component metadata (props, types, variants)
- Classifies components by type (button, card, modal, etc.)
- Outputs JSON data for Claude to process

### Step 2: Parse Component Data

After receiving the JSON output from the scan, parse it to create options for AskUserQuestion:

```python
import json

# Parse the component scan results
components = json.loads(scan_output)

# Create options for AskUserQuestion
component_options = []
for comp in components:
    name = comp['name']
    path = comp['file_path']
    props_count = len(comp.get('props', []))
    comp_type = comp.get('component_type', 'component')
    variants = comp.get('detected_variants', [])
    variant_count = len(variants)

    component_options.append({
        "label": f"{name} ({path.split('/')[-1]})",
        "description": f"{props_count} props • {comp_type} • {variant_count} variants detected",
        "value": path  # Store full path for later use
    })
```

### Step 3: Present Options to User

Use AskUserQuestion to let the user select components and testing preferences:

```javascript
// Use the parsed component_options from Step 2

AskUserQuestion({
  questions: [
    {
      question: `I found ${components.length} components. Which should I generate stories for?`,
      header: "Components",
      multiSelect: true,
      options: component_options  // From Step 2 parsing
    },
    {
      question: "What level of testing should I include in the stories?",
      header: "Test Level",
      multiSelect: false,
      options: [
        {
          label: "Full Testing",
          description: "Recommended: Interaction tests, accessibility tests, multiple variants, and edge cases"
        },
        {
          label: "Standard Testing",
          description: "Interaction tests and multiple variants (no accessibility tests)"
        },
        {
          label: "Basic Stories",
          description: "Multiple variants with args/controls only (no automated tests)"
        },
        {
          label: "Minimal",
          description: "Single story per component with default props"
        }
      ]
    },
    {
      question: "Should I generate visual mockups for complex components?",
      header: "Mockups",
      multiSelect: false,
      options: [
        {
          label: "Yes",
          description: "Recommended: Generate mockups for Card, Modal, Table (requires OPENROUTER_API_KEY)"
        },
        {
          label: "No",
          description: "Generate stories only"
        }
      ]
    }
  ]
})
```

### Step 4: Process User Selections

After receiving user answers, process the selections and prepare for batch generation:

```python
# Extract user selections from AskUserQuestion response
selected_components = answers['Components']  # List of file paths
testing_level_raw = answers['Testing Level']
generate_mockups_raw = answers['Visual Mockups']

# Map testing level to script parameter
testing_level_map = {
    "Full Testing (Recommended)": "full",
    "Standard Testing": "standard",
    "Basic Stories": "basic",
    "Minimal": "minimal"
}
testing_level = testing_level_map.get(testing_level_raw, "full")

# Map mockup option to boolean
generate_mockups = "Yes" in generate_mockups_raw

# Write selected component paths to temp file for batch script
import tempfile
temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
for path in selected_components:
    temp_file.write(f"{path}\n")
temp_file.close()

# Store temp file path
component_paths_file = temp_file.name
```

### Step 5: Generate Stories

Invoke the batch generation script with user selections:

```bash
bash ${CLAUDE_PLUGIN_ROOT}/commands/scripts/batch-generate-stories.sh \
  "${component_paths_file}" \
  "${testing_level}" \
  "${generate_mockups}"
```

This script will:
- Read the list of selected component paths
- For each component:
  - Parse component metadata using `parse_component.py`
  - Detect variants using `detect_variants.py`
  - Generate story file using `generate_story.py` with appropriate template
  - Optionally queue visual mockup generation for complex components
- Display progress and summary

### Step 6: Report Results

After batch generation completes, the script outputs a summary:

```
═══════════════════════════════════════════════
  Story Generation Summary
═══════════════════════════════════════════════

✓ Successfully generated: 5 stories
ℹ Mockups queued: 2

Generated Files:
  ✓ src/components/Button.stories.tsx
  ✓ src/components/Card.stories.tsx
  ✓ src/components/Modal.stories.tsx
  ✓ src/components/Table.stories.tsx
  ✓ src/components/Input.stories.tsx

Next Steps:
  1. Run Storybook: npm run storybook
  2. Review generated stories in your browser
  3. Run interaction tests: npm run test-storybook
  4. Run accessibility tests: npm run storybook -- --test-runner
```

## Generated Story Structure

For each selected component, the system generates stories based on the testing level:

#### Full Testing (SOTA Pattern)

```typescript
// Button.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { expect, userEvent, within } from '@storybook/test';
import { Button } from './Button';

const meta = {
  title: 'Components/Button',
  component: Button,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['primary', 'secondary', 'outline', 'ghost'],
      description: 'Button visual style',
    },
    size: {
      control: 'select',
      options: ['small', 'medium', 'large'],
    },
    disabled: {
      control: 'boolean',
    },
    onClick: { action: 'clicked' },
  },
} satisfies Meta<typeof Button>;

export default meta;
type Story = StoryObj<typeof meta>;

// Variant stories
export const Primary: Story = {
  args: {
    variant: 'primary',
    children: 'Button',
  },
};

export const Secondary: Story = {
  args: {
    variant: 'secondary',
    children: 'Button',
  },
};

export const Outline: Story = {
  args: {
    variant: 'outline',
    children: 'Button',
  },
};

// Size variants
export const Small: Story = {
  args: {
    size: 'small',
    children: 'Small Button',
  },
};

export const Large: Story = {
  args: {
    size: 'large',
    children: 'Large Button',
  },
};

// State variants
export const Disabled: Story = {
  args: {
    disabled: true,
    children: 'Disabled Button',
  },
};

// Interaction test
export const WithInteraction: Story = {
  args: {
    variant: 'primary',
    children: 'Click Me',
  },
  play: async ({ canvasElement, args }) => {
    const canvas = within(canvasElement);
    const button = canvas.getByRole('button', { name: /click me/i });

    // Test button is rendered
    await expect(button).toBeInTheDocument();

    // Test click interaction
    await userEvent.click(button);

    // Verify onClick was called (action)
    await expect(args.onClick).toHaveBeenCalled();

    // Test button is not disabled
    await expect(button).not.toBeDisabled();
  },
};

// Accessibility test
export const AccessibilityValidation: Story = {
  args: {
    variant: 'primary',
    children: 'Accessible Button',
  },
  parameters: {
    a11y: {
      config: {
        rules: [
          { id: 'button-name', enabled: true },
          { id: 'color-contrast', enabled: true },
          { id: 'focus-visible', enabled: true },
        ],
      },
    },
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const button = canvas.getByRole('button');

    // Test keyboard accessibility
    button.focus();
    await expect(button).toHaveFocus();

    // Test Enter key
    await userEvent.keyboard('{Enter}');
  },
};

// Edge cases
export const LongText: Story = {
  args: {
    children: 'This is a button with very long text that might wrap',
  },
};

export const WithIcon: Story = {
  args: {
    children: (
      <>
        <span>Icon Button</span>
        <span>→</span>
      </>
    ),
  },
};
```

#### Standard Testing

Same as Full Testing but without accessibility test story.

#### Basic Stories

```typescript
// Button.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { Button } from './Button';

const meta = {
  title: 'Components/Button',
  component: Button,
  tags: ['autodocs'],
} satisfies Meta<typeof Button>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Primary: Story = {
  args: {
    variant: 'primary',
    children: 'Button',
  },
};

export const Secondary: Story = {
  args: {
    variant: 'secondary',
    children: 'Button',
  },
};
```

#### Minimal

```typescript
// Button.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { Button } from './Button';

const meta = {
  title: 'Components/Button',
  component: Button,
} satisfies Meta<typeof Button>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    children: 'Button',
  },
};
```

### Phase 4: Intelligent Variant Detection

The skill automatically generates variants based on:

**1. Enum/Union Props**
```typescript
// If prop type is: variant: 'primary' | 'secondary' | 'outline'
// Generate stories: Primary, Secondary, Outline
```

**2. Size Props**
```typescript
// If prop: size: 'small' | 'medium' | 'large'
// Generate: Small, Medium, Large variants
```

**3. Boolean Props**
```typescript
// If prop: disabled?: boolean
// Generate: Normal + Disabled variants
```

**4. Component Type**
- **Form inputs**: Focus, error, disabled states
- **Modals**: Open, closed, with actions
- **Tables**: Empty, loading, paginated
- **Cards**: With/without image, different layouts

### Phase 5: Visual Mockup Generation (Optional)

If user enabled visual generation and OPENROUTER_API_KEY available:

```python
# Generate mockup for complex components
python ${CLAUDE_PLUGIN_ROOT}/skills/visual-design/scripts/generate_mockup.py \
  "${COMPONENT_TYPE} component with ${DETECTED_VARIANTS}. \
   Framework: ${FRAMEWORK}. Design system: ${DESIGN_SYSTEM}. \
   Modern, clean UI." \
  --output mockups/${COMPONENT_NAME}.png
```

**Generate mockups for:**
- Card components
- Modal dialogs
- Tables with data
- Form layouts
- Navigation menus

**Skip mockups for:**
- Simple buttons
- Input fields
- Icons
- Badges

### Phase 6: Completion Summary

```
✅ Generated Stories: ${STORIES_COUNT} components

Components:
${COMPONENT_LIST.map(c => `  ✓ ${c.name} - ${c.storiesCount} stories`)}

Testing:
${INTERACTION_TESTS ? `  ✓ Interaction tests: ${INTERACTION_COUNT}` : ""}
${A11Y_TESTS ? `  ✓ Accessibility tests: ${A11Y_COUNT}` : ""}
${VISUAL_MOCKUPS ? `  ✓ Visual mockups: ${MOCKUP_COUNT}` : ""}

Next Steps:
1. Run: npm run storybook
2. Review generated stories
3. Customize as needed
4. Add more interaction tests with /testing-suite

Files Created:
${GENERATED_FILES.map(f => `  - ${f}`).join('\n')}
```

## Component Parsing

### TypeScript Interface Parsing

```typescript
// Parse component props from TypeScript
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'outline'; // → Generate 3 variant stories
  size?: 'small' | 'medium' | 'large';          // → Generate 3 size stories
  disabled?: boolean;                             // → Generate disabled story
  onClick?: () => void;                           // → Add to argTypes with action
  children: React.ReactNode;                      // → Default to 'Button'
}
```

### Vue Props Parsing

```typescript
// Parse from defineProps
const props = defineProps<{
  variant: 'primary' | 'secondary';
  size?: 'small' | 'large';
  disabled?: boolean;
}>();
```

### Svelte Props Parsing

```typescript
// Parse from export let
export let variant: 'primary' | 'secondary' = 'primary';
export let size: 'small' | 'large' = 'medium';
export let disabled = false;
```

## Platform-Specific Considerations

### Tauri Components

If component uses `window.__TAURI__`:
```typescript
// Auto-generate mock in story
export const WithTauriAPI: Story = {
  args: { /* ... */ },
  decorators: [
    (Story) => {
      // Mock Tauri API for this story
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

If component uses `window.api`:
```typescript
// Auto-generate mock in story
export const WithElectronAPI: Story = {
  args: { /* ... */ },
  decorators: [
    (Story) => {
      if (typeof window !== 'undefined') {
        window.api = electronMocks;
      }
      return <Story />;
    },
  ],
};
```

## Error Handling

- **No components found**: Inform user, suggest component paths to scan
- **Parse error**: Skip component, log warning, continue with others
- **Existing stories**: Ask if user wants to overwrite or skip
- **OPENROUTER_API_KEY missing**: Skip visual generation, inform user

## Notes

- Always generate TypeScript stories (even for JS components)
- Include CSF 3.0 patterns (satisfies Meta<typeof Component>)
- Add 'autodocs' tag to all generated stories
- Use framework-specific testing imports (@storybook/test)
- Generate mockups only for complex components
- Respect user's testing level selection
