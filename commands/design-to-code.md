---
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
description: Transform design screenshots and mockups into pixel-perfect React components using Claude's vision AI
argument-hint: "[image-path or URL]"
---

# Design-to-Code Command

Transform visual designs into production-ready React components.

## Usage

```bash
/design-to-code <image-path>
/design-to-code https://example.com/design.png
/design-to-code ./mockups/pricing-card.png
```

## Workflow

1. **Upload/Provide Image**: Screenshot, Figma export, or mockup
2. **AI Analysis**: Vision model extracts layout, colors, typography, spacing
3. **Preview**: Shows extracted design data
4. **Confirm**: User approves or adjusts
5. **Generate**: Creates component + stories + design tokens

## Example

```bash
User: /design-to-code ./designs/product-card.png

Analyzing design...

✓ Component type: ProductCard
✓ Layout: Vertical stack (image → content → button)
✓ Colors: 5 detected (#FFFFFF, #2196F3, #1F2937, #6B7280, #E5E7EB)
✓ Typography: 3 sizes (24px, 16px, 14px)
✓ Spacing: 24px padding, 16px gaps
✓ States: Default + Hover (detected shadow increase)

Generating:
  ✓ components/ProductCard/ProductCard.tsx
  ✓ components/ProductCard/ProductCard.stories.tsx
  ✓ themes/product-card-tokens.css

Done! Component ready for use.
```

Load the `design-to-code` skill for detailed guidance.
