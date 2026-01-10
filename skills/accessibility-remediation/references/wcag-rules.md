# WCAG 2.2 Rules Reference

Quick reference for common WCAG 2.2 success criteria with fix patterns.

## Level A (Essential)

### 1.1.1 Non-text Content
- **Images**: Must have alt text or be marked as decorative
- **Fix**: `<img alt="description" />` or `<img alt="" aria-hidden="true" />`

### 2.1.1 Keyboard
- **All functionality**: Must be keyboard accessible
- **Fix**: Use semantic elements or add role + tabIndex + keydown handler

### 3.3.2 Labels or Instructions
- **Form inputs**: Must have labels
- **Fix**: `<label htmlFor="id">Label</label>` or `aria-label`

### 4.1.2 Name, Role, Value
- **UI components**: Must have accessible names
- **Fix**: aria-label, visible text, or sr-only text

## Level AA (Recommended)

### 1.4.3 Contrast (Minimum)
- **Normal text**: 4.5:1 contrast ratio
- **Large text**: 3:1 contrast ratio
- **Fix**: Darken foreground or lighten background

### 2.4.7 Focus Visible
- **Focus indicators**: Must be visible
- **Fix**: Custom `:focus` or `:focus-visible` styles

### 3.1.2 Language of Parts
- **Language changes**: Mark with lang attribute
- **Fix**: `<span lang="es">Hola</span>`

## Level AAA (Enhanced)

### 1.4.6 Contrast (Enhanced)
- **Normal text**: 7:1 contrast ratio
- **Large text**: 4.5:1 contrast ratio

## Common Violations

See analyze_component.py for automated detection of:
- Missing button labels
- Missing image alt text
- Missing form labels
- Poor color contrast
- Redundant ARIA
- Invalid ARIA attributes
- Missing focus indicators
- Missing keyboard support
- Heading hierarchy issues
- Ambiguous link text

## Resources

- WCAG 2.2: https://www.w3.org/WAI/WCAG22/quickref/
- ARIA Practices: https://www.w3.org/WAI/ARIA/apg/
