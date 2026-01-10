---
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
description: Analyze and fix accessibility issues with AI-powered suggestions
argument-hint: "[component-file]"
---

# Fix Accessibility Command

AI-powered WCAG 2.2 compliance with one-click fixes.

## Usage

```bash
/fix-accessibility Button.tsx
/fix-accessibility src/components/Modal.tsx
/fix-accessibility  # Analyzes current file
```

Triggers the `accessibility-auditor` agent for comprehensive analysis and remediation.
