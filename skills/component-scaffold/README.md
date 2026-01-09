# Component Scaffold - Quick Reference

Generate production-ready components with TypeScript, accessibility, and best practices.

## Quick Start

### Generate a Button Component

```bash
python3 scripts/create_component.py \
  --name MyButton \
  --type button \
  --framework react \
  --output src/components/MyButton.tsx
```

### Generate a Custom Component

```bash
python3 scripts/create_component.py \
  --name UserCard \
  --type custom \
  --framework react \
  --props "name:string,email:string,avatar:string" \
  --output src/components/UserCard.tsx
```

## Supported Component Types

- **button**: Interactive button with variants and sizes
- **input**: Form input with validation and error states
- **card**: Content card with header, footer, image
- **modal**: Modal dialog with focus management
- **table**: Data table with sorting and pagination
- **custom**: Define your own props

## Arguments

- `--name`: Component name (PascalCase) [required]
- `--type`: Component type (see above) [default: custom]
- `--framework`: Target framework (react, vue, svelte) [default: react]
- `--typescript`: Generate TypeScript [default: true]
- `--props`: Custom props (comma-separated: name:type,name2:type2)
- `--output`: Output file path
- `--dry-run`: Print to stdout instead of writing file
- `--json`: Output component spec as JSON

## Examples

### Button with All Features
```bash
python3 scripts/create_component.py --name SubmitButton --type button --output src/components/SubmitButton.tsx
```

Generated props:
- variant (primary, secondary, outline, ghost)
- size (small, medium, large)
- disabled, loading
- onClick handler
- children

### Input with Validation
```bash
python3 scripts/create_component.py --name EmailInput --type input --output src/components/EmailInput.tsx
```

Generated props:
- label, type, placeholder, value
- error, helperText
- required, disabled
- onChange handler

### Card Component
```bash
python3 scripts/create_component.py --name ProductCard --type card --output src/components/ProductCard.tsx
```

Generated props:
- variant (elevated, outlined, flat)
- image, imageAlt
- header, footer
- onClick handler
- children

### Modal Dialog
```bash
python3 scripts/create_component.py --name ConfirmDialog --type modal --output src/components/ConfirmDialog.tsx
```

Generated props:
- isOpen, onClose
- title, size
- closeOnBackdropClick, closeOnEsc
- children

Generated features:
- Focus trap
- ESC key handler
- ARIA attributes

### Custom Component
```bash
python3 scripts/create_component.py \
  --name ProfileCard \
  --type custom \
  --props "username:string,bio:string,avatar:string,isVerified:boolean,onFollow:function" \
  --output src/components/ProfileCard.tsx
```

## Templates

Templates are located in `templates/{framework}/{type}.template`:

```
templates/
├── react/
│   ├── button.template
│   ├── input.template
│   ├── card.template
│   ├── modal.template
│   ├── table.template
│   └── custom.template
├── vue/
│   └── (coming soon)
└── svelte/
    └── (coming soon)
```

## Template Variables

Templates use these variables:
- `{{COMPONENT_NAME}}`: Component name (e.g., MyButton)
- `{{COMPONENT_CLASS}}`: CSS class (e.g., my-button)
- `{{COMPONENT_DESCRIPTION}}`: Component description
- `{{PROPS}}`: TypeScript interface props
- `{{PROP_DESTRUCTURING}}`: Destructured props with defaults
- `{{COMPONENT_LOGIC}}`: Component logic (hooks, etc.)
- `{{COMPONENT_CONTENT}}`: JSX/template content

## Integration with Story Generation

After creating a component, generate its story:

```bash
# Create component
python3 scripts/create_component.py --name Button --type button --output src/components/Button.tsx

# Generate story (from story-generation skill)
python3 ../../story-generation/scripts/generate_story.py \
  src/components/Button.tsx \
  --level full \
  --output src/components/Button.stories.tsx
```

Or use the integrated workflow script:

```bash
bash ../../commands/scripts/create-component-workflow.sh \
  Button button react full false src/components
```

## Prop Type Shortcuts

When defining custom props, use these shortcuts:

| Shortcut | TypeScript Type |
|----------|----------------|
| string, str | string |
| number, num | number |
| boolean, bool | boolean |
| function, func | () => void |
| node, element | React.ReactNode |

Example:
```bash
--props "title:string,count:number,active:boolean,onClick:function"
```

Generates:
```typescript
interface ComponentProps {
  title: string;
  count: number;
  active: boolean;
  onClick: () => void;
}
```

## Component Features

All generated components include:

- ✓ **TypeScript**: Proper interfaces and types
- ✓ **Accessibility**: ARIA attributes (aria-label, aria-busy, etc.)
- ✓ **Documentation**: JSDoc comments for props
- ✓ **Defaults**: Sensible default values
- ✓ **Best Practices**: Framework-specific patterns
- ✓ **Display Name**: Component.displayName set

## Adding New Component Types

1. Add type definition in `scripts/create_component.py`:

```python
COMPONENT_TYPE_DEFAULTS = {
    'checkbox': {
        'description': 'Checkbox input component',
        'props': [
            PropDefinition('checked', 'boolean', False, 'false'),
            PropDefinition('onChange', '(checked: boolean) => void', False, None),
        ],
        'has_children': False,
    }
}
```

2. Create template `templates/react/checkbox.template`

3. Add component-specific logic in `generate_component_content_react()`

See SKILL.md for detailed instructions.

## Troubleshooting

### Component name validation error

Component names must start with uppercase letter (PascalCase):
- ✓ MyButton, UserCard, DataTable
- ✗ myButton, user-card, data_table

### Template not found

If you get "Template not found", the system falls back to `custom.template`. Create a specific template for your component type or use `--type custom`.

### Invalid prop format

Props must be in format `name:type`:
```bash
--props "title:string,count:number"  # ✓ Correct
--props "title,count"                 # ✗ Wrong
```

## Performance

- Component generation: ~5ms per component
- Template loading: ~1ms (cached)
- Story generation: ~15ms per component
- Total workflow: ~20ms per component

## Further Reading

- **SKILL.md**: Complete skill documentation
- **commands/create-component.md**: Full command workflow
- **CREATE_COMPONENT_IMPLEMENTATION.md**: Implementation details
