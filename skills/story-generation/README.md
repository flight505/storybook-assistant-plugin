# Story Generation - Component Parser & Story Generator

Complete component analysis and story generation system for React, Vue, and Svelte.

## Features

### ✅ Component Parser (`parse_component.py`)
- **React/TypeScript**: Parse interfaces, types, function components, arrow functions
- **Vue 3**: Parse `defineProps` (TypeScript and runtime)
- **Svelte**: Parse `export let` statements
- Extracts: component name, props, types, required/optional, defaults
- Classifies component type: button, input, card, table, etc.

### ✅ Variant Detector (`detect_variants.py`)
- **Intelligent variant detection** from prop types
- Detects enum/union types: `'primary' | 'secondary' | 'outline'`
- Detects size variants: `small`, `medium`, `large`
- Detects boolean states: `disabled`, `loading`, `error`
- Component-type specific variants (e.g., modal open state)
- Priority-based sorting

### ✅ Story Generator (`generate_story.py`)
- **Complete story file generation** with templates
- Multiple testing levels: `full`, `standard`, `basic`, `minimal`
- **Full testing includes**:
  - Variant stories for all detected variations
  - Interaction tests with play functions
  - Accessibility tests with axe-core
  - Component-specific test patterns
- **Template-based** (easily extensible)
- **Framework support**: React, Vue, Svelte

### ✅ Component Scanner (`scan_components.py`)
- **Project-wide component discovery**
- Scans directories recursively
- Filters out test files, node_modules, etc.
- Groups by framework
- Generates component metadata for all files

---

## Installation

No installation needed - pure Python 3 scripts.

**Requirements:**
- Python 3.8+
- No external dependencies (uses standard library only)

---

## Usage

### 1. Parse a Component

```bash
python3 parse_component.py path/to/Component.tsx

# Output:
# Component: Button
# Framework: react
# Type: button
# Props (6):
#   - variant: 'primary' | 'secondary' | 'outline' | 'ghost' (required)
#   - size: 'small' | 'medium' | 'large' (optional)
#   - disabled: boolean (optional)
#   ...
```

**JSON output:**
```bash
python3 parse_component.py Component.tsx --json
```

### 2. Detect Variants

```bash
python3 detect_variants.py path/to/Component.tsx

# Output:
# Detected 11 variants:
# 1. Primary
#    Description: variant: primary
#    Args: {'variant': 'primary'}
#    Priority: 1
# ...
```

**JSON output:**
```bash
python3 detect_variants.py Component.tsx --json
```

### 3. Generate Story

```bash
# Full testing (interaction + accessibility + variants)
python3 generate_story.py Component.tsx --level full --output Component.stories.tsx

# Basic stories only
python3 generate_story.py Component.tsx --level basic --output Component.stories.tsx

# Dry run (print to stdout)
python3 generate_story.py Component.tsx --level full --dry-run
```

**Testing levels:**
- `full`: All features (variants + interaction tests + a11y tests)
- `standard`: Variants + interaction tests (no a11y)
- `basic`: Variants with args/controls only
- `minimal`: Single default story

### 4. Scan Project for Components

```bash
# Scan current directory
python3 scan_components.py

# Scan specific directory
python3 scan_components.py src/components

# JSON output
python3 scan_components.py src --json

# Exclude additional patterns
python3 scan_components.py src --exclude '*.test.*' --exclude 'draft'
```

---

## Quick Test

Run the test suite on sample components:

```bash
./test_parser.sh

# Output:
# 🧪 Testing Component Parser & Story Generator
# ==============================================
#
# 📋 Test 1: Parse Component
# ...
# ✅ All tests completed successfully!
```

---

## Examples

### Example 1: React Button Component

**Input: `Button.tsx`**
```typescript
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'outline';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  onClick?: () => void;
  children: React.ReactNode;
}

export function Button({ variant, size, disabled, onClick, children }: ButtonProps) {
  return <button className={`btn-${variant} btn-${size}`} disabled={disabled} onClick={onClick}>{children}</button>;
}
```

**Command:**
```bash
python3 generate_story.py Button.tsx --level full --output Button.stories.tsx
```

**Output: `Button.stories.tsx`**
```typescript
import type { Meta, StoryObj } from '@storybook/react';
import { expect, userEvent, within } from '@storybook/test';
import { Button } from './Button';

const meta = {
  title: 'Components/Button',
  component: Button,
  parameters: { layout: 'centered' },
  tags: ['autodocs'],
  argTypes: {
    variant: { control: 'select', options: ['primary', 'secondary', 'outline'] },
    size: { control: 'select', options: ['small', 'medium', 'large'] },
    disabled: { control: 'boolean' },
    onClick: { action: 'onClick' },
  },
} satisfies Meta<typeof Button>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Primary: Story = {
  args: { variant: 'primary', children: 'Button' },
};

export const Secondary: Story = {
  args: { variant: 'secondary', children: 'Button' },
};

export const Outline: Story = {
  args: { variant: 'outline', children: 'Button' },
};

export const Small: Story = {
  args: { size: 'small', children: 'Button' },
};

export const Large: Story = {
  args: { size: 'large', children: 'Button' },
};

export const Disabled: Story = {
  args: { disabled: true, children: 'Button' },
};

// Interaction test
export const WithInteraction: Story = {
  args: { children: 'Button', onClick: () => {} },
  play: async ({ canvasElement, args }) => {
    const canvas = within(canvasElement);
    const button = canvas.getByRole('button');
    await expect(button).toBeInTheDocument();
    await userEvent.click(button);
    if (args.onClick) {
      await expect(args.onClick).toHaveBeenCalled();
    }
    await expect(button).not.toBeDisabled();
  },
};

// Accessibility test
export const AccessibilityValidation: Story = {
  args: { children: 'Button' },
  parameters: {
    a11y: {
      config: {
        rules: [
          { id: 'button-name', enabled: true },
          { id: 'color-contrast', enabled: true },
        ],
      },
    },
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const button = canvas.getByRole('button');
    button.focus();
    await expect(button).toHaveFocus();
    await userEvent.keyboard('{Enter}');
  },
};
```

### Example 2: Vue Component

**Input: `Button.vue`**
```vue
<script setup lang="ts">
defineProps<{
  variant: 'primary' | 'secondary';
  size?: 'small' | 'large';
  disabled?: boolean;
}>();
</script>

<template>
  <button :class="`btn-${variant} btn-${size}`" :disabled="disabled">
    <slot />
  </button>
</template>
```

**Command:**
```bash
python3 generate_story.py Button.vue --level full --output Button.stories.ts
```

**Output:** Similar structure with Vue 3 imports and syntax.

---

## Architecture

### Component Parser Flow

```
Component File (.tsx/.vue/.svelte)
          ↓
    parse_component()
          ↓
   Extract metadata:
   - Component name
   - Props with types
   - Required/optional
   - Component type
          ↓
   ComponentMetadata
```

### Variant Detection Flow

```
ComponentMetadata
          ↓
  detect_variants()
          ↓
   Analyze props:
   - Enum/union types
   - Size props
   - Boolean states
   - Type-specific
          ↓
   List[Variant]
```

### Story Generation Flow

```
ComponentMetadata + Variants
          ↓
  generate_story()
          ↓
   Load template:
   - framework-level.template
          ↓
   Replace placeholders:
   - {{COMPONENT_NAME}}
   - {{VARIANT_STORIES}}
   - {{INTERACTION_TEST_CODE}}
          ↓
   Generated .stories.tsx file
```

---

## Supported Component Types

The system automatically detects component types and generates appropriate tests:

| Type | Detection | Interaction Test | A11y Rules |
|------|-----------|------------------|------------|
| `button` | Name contains 'button', 'btn' | Click test, disabled check | button-name, color-contrast |
| `input` | Name contains 'input', 'textfield' | Type test, value check | label, color-contrast |
| `checkbox` | Name contains 'checkbox' | Click test, checked state | ... |
| `select` | Name contains 'select', 'dropdown' | Select option test | ... |
| `modal` | Name contains 'modal', 'dialog' | Focus trap test | aria-dialog-name, focus-trap |
| `card` | Name contains 'card' | Generic render test | ... |
| `table` | Name contains 'table', 'datagrid' | Row/column tests | ... |

---

## Templates

Templates are located in `templates/` directory:

```
templates/
├── react-full.template       # React with full testing
├── react-basic.template      # React basic stories
├── vue-full.template         # Vue 3 with full testing
├── vue-basic.template        # Vue 3 basic stories
├── svelte-full.template      # Svelte with full testing
└── svelte-basic.template     # Svelte basic stories
```

**Template variables:**
- `{{COMPONENT_NAME}}` - Component name
- `{{STORY_TITLE}}` - Story title (e.g., Components/Button)
- `{{ARG_TYPES}}` - ArgTypes configuration
- `{{VARIANT_STORIES}}` - Generated variant story exports
- `{{DEFAULT_ARGS}}` - Default args for tests
- `{{INTERACTION_TEST_CODE}}` - Interaction test code
- `{{A11Y_RULES}}` - Accessibility rules
- `{{A11Y_TEST_CODE}}` - Accessibility test code

### Adding Custom Templates

Create new template file: `templates/{framework}-{level}.template`

Example: `templates/react-custom.template`

---

## Advanced Usage

### Custom Component Scanning

```python
from scan_components import ComponentScanner

# Scan with custom patterns
components = ComponentScanner.scan(
    root_dir='src',
    exclude_patterns=['legacy', 'deprecated']
)

# Filter by component type
buttons = [c for c in components if c['component_type'] == 'button']
```

### Custom Variant Detection

```python
from detect_variants import VariantDetector

# Add custom variant patterns
VariantDetector.VARIANT_PATTERNS['theme'] = ['light', 'dark', 'auto']

variants = VariantDetector.detect_variants(metadata_dict)
```

### Custom Story Templates

```python
from generate_story import StoryGenerator

# Override template directory
StoryGenerator.TEMPLATE_DIR = Path('custom/templates')

# Generate with custom template
story = StoryGenerator.generate_story(
    'Component.tsx',
    testing_level='custom',
    output_path='Component.stories.tsx'
)
```

---

## Integration with Plugin

These scripts are used by the `/generate-stories` command:

1. **Scan phase**: `scan_components.py` finds all components
2. **User selection**: AskUserQuestion presents discovered components
3. **Generation phase**: For each selected component:
   - `parse_component.py` extracts metadata
   - `detect_variants.py` finds variants
   - `generate_story.py` creates story file

---

## Troubleshooting

### Issue: Parser fails on component

**Solution**: Check if component follows standard patterns:
- TypeScript interfaces/types for React
- `defineProps<T>` for Vue
- `export let` for Svelte

### Issue: No variants detected

**Solution**: Variants are detected from union types like `'a' | 'b'`. Check if props use string literals or enums.

### Issue: Generated story has errors

**Solution**:
- Ensure component exports are correct
- Check if component needs additional imports
- Verify prop types match actual component

### Issue: Test code doesn't match component

**Solution**: Component type classification may be wrong. Manually classify or add custom test patterns.

---

## Performance

- **Parser**: ~10ms per component (Python)
- **Variant detection**: ~1ms per component
- **Story generation**: ~5ms per component
- **Project scan**: ~100-500ms for 100 components

**Batch processing** is efficient - scan entire project at once.

---

## Future Enhancements

Potential improvements (not yet implemented):
- [ ] Angular component support
- [ ] Props documentation extraction from JSDoc
- [ ] Custom story template language (beyond string replacement)
- [ ] Visual mockup integration (call NanoBanana)
- [ ] Component snapshot testing generation
- [ ] E2E test generation from stories
- [ ] Design system token detection

---

## Contributing

To add support for a new framework:

1. Create parser class in `parse_component.py`:
   ```python
   class NewFrameworkParser(ComponentParser):
       @staticmethod
       def parse(file_path: str) -> Optional[ComponentMetadata]:
           # Implementation
   ```

2. Add templates: `templates/newframework-{level}.template`

3. Update file extension detection

4. Test with sample components

---

## License

MIT - Part of Storybook Assistant Plugin
