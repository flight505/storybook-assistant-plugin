---
allowed-tools:
  - Read
  - Write
  - Bash
description: Generate production-ready components from natural language descriptions
argument-hint: "<component description>"
---

# Generate From Description Command

Create components by describing them in plain English.

## Usage

```bash
/generate-from-description "Create a user profile card with avatar on the left, name and title in the middle, and a follow button on the right"
```

## Example

```bash
User: /generate-from-description "I need a notification card with icon, title, message, timestamp, and dismiss button. Support success, warning, error types. Auto-dismiss after 5 seconds unless pinned."

Analyzing requirements...
  ✓ Component: NotificationCard
  ✓ Elements: Icon, Title, Message, Timestamp, DismissButton
  ✓ Variants: Success, Warning, Error
  ✓ Behavior: Auto-dismiss (5s), Pinnable
  ✓ Props inferred: type, title, message, timestamp, onDismiss, pinned, autoDismiss

Generating:
  ✓ NotificationCard.tsx (with useEffect for auto-dismiss)
  ✓ NotificationCard.stories.tsx (8 variants)
  ✓ TypeScript interfaces
  ✓ Accessibility attributes

Done! Component ready with:
- Success/Warning/Error variants
- Auto-dismiss functionality
- Pinned mode
- WCAG 2.2 compliant
```

Uses the `component-generator` agent for intelligent code generation.
