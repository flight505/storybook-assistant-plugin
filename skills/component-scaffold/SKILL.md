---
description: Scaffold new components with stories, tests, and documentation following SOTA patterns and best practices
---

# Component Scaffold Skill

This skill provides comprehensive component scaffolding with:
- Framework-specific component templates (React, Vue, Svelte)
- TypeScript interfaces with proper types
- Accessibility attributes (ARIA labels, roles)
- Storybook stories with variants and tests
- Optional visual mockups
- Best practice patterns for each framework

## Features

### Component Generation
- **Type-Based Templates**: Pre-built templates for common component types (Button, Input, Card, Modal, Table, etc.)
- **Custom Components**: Generate components with user-defined props
- **Framework Support**: React, Vue 3, Svelte 5
- **TypeScript First**: All components generated with proper TypeScript types
- **Accessibility**: Built-in ARIA attributes and semantic HTML

### Testing Support
- **Storybook Stories**: Automatically generated with CSF 3.0 format
- **Variant Detection**: Intelligent variants based on component type
- **Interaction Tests**: Play functions with Testing Library
- **A11y Tests**: Accessibility testing with axe-core

### Visual Design
- **AI Mockups**: Optional visual references using NanoBanana
- **Design Tokens**: Integration with design system tokens
- **Responsive**: Mobile-first, responsive patterns

## Component Types Supported

### Form Components
- **Button**: Variants, sizes, loading states, icons
- **Input**: Validation, error states, helper text
- **Checkbox**: Indeterminate state, controlled/uncontrolled
- **Radio**: Radio groups with proper accessibility
- **Select**: Dropdown with search, multi-select
- **Textarea**: Auto-resize, character count
- **Switch/Toggle**: Binary state with labels

### Layout Components
- **Card**: Header, footer, image, variants
- **Container**: Max-width, padding, responsive
- **Grid**: CSS Grid with responsive columns
- **Stack**: Vertical/horizontal spacing
- **Divider**: Horizontal/vertical separators

### Navigation Components
- **Tabs**: Controlled tabs with keyboard navigation
- **Menu**: Dropdown menu with submenus
- **Breadcrumb**: Navigation breadcrumbs
- **Pagination**: Page navigation with ellipsis

### Feedback Components
- **Alert**: Success, warning, error, info variants
- **Toast**: Toast notifications with auto-dismiss
- **Modal/Dialog**: Focus trap, backdrop, ESC handling
- **Spinner**: Loading indicators
- **Progress**: Progress bars and circular progress
- **Skeleton**: Loading skeletons

### Data Display Components
- **Table**: Sorting, filtering, pagination, selection
- **List**: Virtual scrolling for large lists
- **Avatar**: User avatars with fallbacks
- **Badge**: Status badges with variants
- **Tooltip**: Hover tooltips with positioning
- **Popover**: Contextual popovers

## Templates

Templates are located in `templates/` directory:

```
templates/
├── react/
│   ├── button.template.tsx
│   ├── input.template.tsx
│   ├── card.template.tsx
│   ├── modal.template.tsx
│   ├── table.template.tsx
│   └── custom.template.tsx
├── vue/
│   ├── button.template.vue
│   ├── input.template.vue
│   └── ...
├── svelte/
│   ├── button.template.svelte
│   ├── input.template.svelte
│   └── ...
└── styles/
    ├── button.template.css
    ├── input.template.css
    └── ...
```

## Scripts

### create_component.py

Main script for component generation:

```bash
python3 create_component.py \
  --name Button \
  --type button \
  --framework react \
  --typescript \
  --output src/components/Button.tsx
```

**Arguments:**
- `--name`: Component name (PascalCase)
- `--type`: Component type (button, input, card, modal, table, custom)
- `--framework`: Target framework (react, vue, svelte)
- `--typescript`: Generate TypeScript (default: true)
- `--output`: Output file path
- `--props`: Custom props (comma-separated, for custom type)
- `--variants`: Custom variants (comma-separated)

### get_component_template.py

Helper to retrieve appropriate template:

```python
from get_component_template import get_template

template = get_template(
    component_type='button',
    framework='react',
    typescript=True
)
```

## Usage Examples

### Example 1: Create Button Component

```bash
python3 create_component.py \
  --name MyButton \
  --type button \
  --framework react \
  --output src/components/MyButton.tsx
```

**Generated:**
```typescript
import React from 'react';
import './MyButton.css';

export interface MyButtonProps {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  loading?: boolean;
  onClick?: () => void;
  children: React.ReactNode;
}

/**
 * MyButton component with multiple variants and sizes
 */
export function MyButton({
  variant = 'primary',
  size = 'medium',
  disabled = false,
  loading = false,
  onClick,
  children,
}: MyButtonProps) {
  return (
    <button
      className={`btn btn-${variant} btn-${size}`}
      disabled={disabled || loading}
      onClick={onClick}
      aria-busy={loading}
    >
      {loading ? 'Loading...' : children}
    </button>
  );
}
```

### Example 2: Create Modal Component

```bash
python3 create_component.py \
  --name Dialog \
  --type modal \
  --framework react \
  --output src/components/Dialog.tsx
```

**Generated:**
- Dialog.tsx with focus trap
- Backdrop click handling
- ESC key handling
- Accessibility attributes (aria-modal, role="dialog")

### Example 3: Create Custom Component

```bash
python3 create_component.py \
  --name UserCard \
  --type custom \
  --framework react \
  --props "name:string,email:string,avatar:string,onEdit:function" \
  --output src/components/UserCard.tsx
```

## Integration with Story Generation

After creating a component, automatically generate its story:

```bash
# Create component
python3 create_component.py --name Button --type button --output src/components/Button.tsx

# Generate story (using story-generation skill)
python3 ../story-generation/scripts/generate_story.py \
  src/components/Button.tsx \
  --level full \
  --output src/components/Button.stories.tsx
```

## Best Practices

### React Components
- Use function components (not class components)
- Use hooks for state and effects
- Proper TypeScript interfaces for props
- Export component and interface
- Include displayName for dev tools

### Vue 3 Components
- Use Composition API (not Options API)
- Use `<script setup lang="ts">`
- Define props with `defineProps<T>()`
- Use `defineEmits` for events
- Scoped styles

### Svelte Components
- Use TypeScript in script blocks
- Export props with `export let`
- Use stores for state management
- Component-scoped styles
- Proper event forwarding

### Accessibility
- Include ARIA attributes (aria-label, aria-describedby)
- Use semantic HTML (button, nav, dialog)
- Keyboard navigation (Tab, Enter, ESC)
- Focus management (focus trap in modals)
- Screen reader support

## Customization

### Adding New Component Types

1. Create template file in `templates/{framework}/{type}.template.{ext}`
2. Add type definition in `create_component.py`
3. Define default props for the type
4. Update this documentation

### Modifying Templates

Templates use variable replacement:
- `{{COMPONENT_NAME}}`: Component name (PascalCase)
- `{{COMPONENT_CLASS}}`: CSS class name (kebab-case)
- `{{PROPS}}`: Props interface
- `{{PROP_DESTRUCTURING}}`: Destructured props with defaults
- `{{COMPONENT_LOGIC}}`: Component logic (hooks, computed, etc.)
- `{{COMPONENT_CONTENT}}`: JSX/template content
- `{{ATTRIBUTES}}`: HTML attributes (aria, data, etc.)

## Error Handling

The script handles common errors:
- Invalid component names
- Missing required arguments
- Unsupported frameworks
- File already exists
- Invalid prop definitions

## Platform Support

### Tauri
- Components work fully in Tauri applications
- IPC mocking included in generated stories
- Native API mocks provided

### Electron
- Components follow container/presentational pattern
- IPC interactions isolated in container components
- Testable presentational components in Storybook

### Web
- Full support for all component types
- Responsive, mobile-first designs
- Progressive enhancement

## Future Enhancements

Potential improvements:
- [ ] Component composition helpers
- [ ] Animation templates (Framer Motion, Vue Transition)
- [ ] Form validation templates (React Hook Form, VeeValidate)
- [ ] State management integration (Zustand, Pinia)
- [ ] API integration templates (React Query, Vue Query)
- [ ] CSS-in-JS templates (Styled Components, Emotion)
- [ ] Testing templates (Vitest, Jest)

## Related Skills

- **story-generation**: Generates Storybook stories for components
- **visual-design**: Generates visual mockups for components
- **testing-suite**: Generates comprehensive test suites
- **storybook-config**: Configures Storybook for the project
