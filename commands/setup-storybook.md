---
description: Initialize Storybook 9 in your project with automatic framework detection, SOTA configuration, and optional visual generation
---

# Setup Storybook Command

When the user invokes `/setup-storybook`, initialize Storybook 9 with automatic framework detection, testing features, and SOTA best practices for 2026.

## Execution Flow

### Phase 1: Environment & Project Analysis

1. **Detect Framework**
   ```bash
   bash ${CLAUDE_PLUGIN_ROOT}/scripts/detect-framework.sh
   ```

   This returns:
   - `FRAMEWORK` (react, vue, svelte, angular, nextjs, solid, lit, unknown)
   - `VERSION` (framework version)
   - `BUNDLER` (vite, webpack, unknown)
   - `PLATFORM` (web, tauri, electron)
   - `DESIGN_SYSTEM` (mui, antd, shadcn, chakra, mantine, custom)

2. **Check Existing Storybook**
   - If `.storybook/` exists, inform user and offer migration
   - If Storybook < 9, suggest `/migrate-storybook` command

3. **Validate Prerequisites**
   - Node.js >= 20
   - npm >= 10
   - Framework version compatible with Storybook 9

### Phase 2: User Configuration (AskUserQuestion)

**CRITICAL: Make questions context-aware and project-specific, NOT generic.**

Use the detected framework, platform, and design system to customize options.

#### Question 1: Testing Features

```javascript
AskUserQuestion({
  questions: [{
    question: `Which testing features do you want for your ${FRAMEWORK} components?`,
    header: "Testing",
    multiSelect: true,
    options: [
      {
        label: "Interaction Tests",
        description: "Recommended: Test user interactions with play functions powered by Vitest + Playwright"
      },
      {
        label: "Accessibility Tests",
        description: "Recommended: WCAG compliance testing with axe-core (catches 57% of issues automatically)"
      },
      {
        label: "Visual Regression Tests",
        description: "Pixel-perfect UI change detection (requires Chromatic or custom setup)"
      },
      {
        label: "Test Coverage Reports",
        description: "V8-powered code coverage analysis (faster than Istanbul)"
      }
    ]
  }]
})
```

#### Question 2: Design System Integration

**Only ask if design system detected OR if user wants to configure:**

```javascript
// If DESIGN_SYSTEM !== 'custom'
AskUserQuestion({
  questions: [{
    question: `I detected ${DESIGN_SYSTEM}. How should Storybook integrate?`,
    header: "Design System",
    multiSelect: false,
    options: [
      {
        label: `Import ${DESIGN_SYSTEM} theme globally`,
        description: `Recommended: Apply your existing ${DESIGN_SYSTEM} theme to all stories automatically`
      },
      {
        label: "Per-story theme control",
        description: "Allow each story to specify its own theme via parameters"
      },
      {
        label: "No automatic integration",
        description: "I'll handle theme setup manually"
      }
    ]
  }]
})

// If DESIGN_SYSTEM === 'custom'
AskUserQuestion({
  questions: [{
    question: "Do you have a custom design system or theme?",
    header: "Design System",
    multiSelect: false,
    options: [
      {
        label: "Yes - I have a ThemeProvider",
        description: "Wrap all stories with my existing theme context"
      },
      {
        label: "Yes - CSS variables/Tailwind",
        description: "Import global styles in Storybook"
      },
      {
        label: "No - Starting fresh",
        description: "Help me create a basic design system"
      }
    ]
  }]
})
```

#### Question 3: Platform-Specific Setup (if Tauri or Electron detected)

```javascript
// If PLATFORM === 'tauri'
AskUserQuestion({
  questions: [{
    question: "I detected a Tauri project. How should I handle Tauri IPC in stories?",
    header: "Tauri IPC",
    multiSelect: false,
    options: [
      {
        label: "Generate IPC mock utilities",
        description: "Recommended: Create window.api mock helpers for testing components in isolation"
      },
      {
        label: "I'll mock IPC manually",
        description: "Skip mock generation, I'll handle it myself"
      }
    ]
  }]
})

// If PLATFORM === 'electron'
// Show warning + architectural guidance
console.log(`
⚠️  Electron Project Detected

Storybook works best with Electron for pure UI components.
Components using window.api.* will need mocking.

Recommendation: Separate UI components from IPC logic using container/presentational pattern.

I'll configure Storybook with Electron-specific webpack overrides.
`)

AskUserQuestion({
  questions: [{
    question: "Would you like me to generate Electron preload API mocks?",
    header: "Electron Mocks",
    multiSelect: false,
    options: [
      {
        label: "Yes",
        description: "Recommended: Generate window.api mock utilities and architectural guidance"
      },
      {
        label: "No",
        description: "Skip mock generation"
      }
    ]
  }]
})
```

#### Question 4: Visual Generation (only if OPENROUTER_API_KEY available)

```javascript
// Only ask if OPENROUTER_API_KEY is set
if (OPENROUTER_API_KEY_AVAILABLE) {
  AskUserQuestion({
    questions: [{
      question: "Would you like me to generate a visual style guide for your components?",
      header: "Visual Assets",
      multiSelect: false,
      options: [
        {
          label: "Yes - Generate style guide",
          description: "Recommended: AI-generated style guide with colors, typography, spacing, and component examples"
        },
        {
          label: "Yes - Generate mockup examples only",
          description: "Create visual mockups for a few example components"
        },
        {
          label: "No - Skip visual generation",
          description: "Set up Storybook only, no AI-generated visuals"
        }
      ]
    }]
  })
}
```

### Phase 3: Installation

Based on detected framework and user preferences, install dependencies:

```bash
# Core Storybook 9
npm install --save-dev storybook@latest

# Framework-specific
# React
npm install --save-dev @storybook/react-vite@latest

# Vue
npm install --save-dev @storybook/vue3-vite@latest

# Svelte
npm install --save-dev @storybook/svelte-vite@latest

# Angular
npm install --save-dev @storybook/angular@latest

# Next.js
npm install --save-dev @storybook/nextjs-vite@latest

# Essential addons (always)
npm install --save-dev @storybook/addon-essentials@latest

# If interaction tests selected
npx storybook@latest add @storybook/addon-vitest
npm install --save-dev @testing-library/react @testing-library/user-event

# If accessibility tests selected
npx storybook@latest add @storybook/addon-a11y

# If coverage selected
npm install --save-dev @vitest/coverage-v8
```

### Phase 4: Configuration Generation

Generate `.storybook/main.ts` with SOTA patterns:

```typescript
import type { StorybookConfig } from '@storybook/${FRAMEWORK}-vite';

const config: StorybookConfig = {
  stories: [
    '../src/**/*.mdx',
    '../src/**/*.stories.@(js|jsx|mjs|ts|tsx)'
  ],

  addons: [
    '@storybook/addon-essentials',
    // Conditional addons based on user selection
    ${INTERACTION_TESTS ? "'@storybook/addon-vitest'," : ""}
    ${A11Y_TESTS ? "'@storybook/addon-a11y'," : ""}
    '@storybook/addon-links',
  ],

  framework: {
    name: '@storybook/${FRAMEWORK}-vite',
    options: {
      ${FRAMEWORK_SPECIFIC_OPTIONS}
    },
  },

  docs: {
    autodocs: 'tag', // Auto-generate docs for stories tagged with 'autodocs'
  },

  ${PLATFORM === 'electron' ? `
  // Electron-specific webpack overrides
  webpackFinal: async (config) => {
    config.target = 'web'; // Override electron-renderer
    config.externals = {}; // Clear Electron externals
    config.resolve.alias = {
      ...(config.resolve?.alias || {}),
      electron: false // Mock electron module
    };
    return config;
  },
  ` : ""}

  // Vite optimization for faster builds
  viteFinal: async (config) => {
    return {
      ...config,
      optimizeDeps: {
        ...config.optimizeDeps,
        include: [
          ...(config.optimizeDeps?.include || []),
          '@storybook/blocks',
        ],
      },
    };
  },

  // Performance: Enable test mode for CI
  build: {
    test: {
      disabledAddons: ['@storybook/addon-docs'], // Faster builds in CI
    },
  },
};

export default config;
```

Generate `.storybook/preview.ts` with theme integration:

```typescript
import type { Preview } from '@storybook/${FRAMEWORK}-vite';

${DESIGN_SYSTEM_IMPORTS}

const preview: Preview = {
  parameters: {
    // SOTA: Better action logging
    actions: { argTypesRegex: '^on[A-Z].*' },

    // SOTA: Default controls behavior
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
      expanded: true, // Show all controls by default
    },

    // SOTA: Better layout defaults
    layout: 'centered',

    ${A11Y_TESTS ? `
    // Accessibility: Configure axe-core
    a11y: {
      config: {
        rules: [
          {
            id: 'color-contrast',
            enabled: true,
          },
        ],
      },
    },
    ` : ""}

    // SOTA: Better backgrounds
    backgrounds: {
      default: 'light',
      values: [
        { name: 'light', value: '#ffffff' },
        { name: 'dark', value: '#1a1a1a' },
        { name: 'gray', value: '#f5f5f5' },
      ],
    },

    // SOTA: Responsive viewports
    viewport: {
      viewports: {
        mobile: { name: 'Mobile', styles: { width: '375px', height: '667px' } },
        tablet: { name: 'Tablet', styles: { width: '768px', height: '1024px' } },
        desktop: { name: 'Desktop', styles: { width: '1280px', height: '800px' } },
      },
    },
  },

  ${DESIGN_SYSTEM_DECORATORS}

  ${PLATFORM === 'tauri' || PLATFORM === 'electron' ? `
  // Platform mock decorators
  decorators: [
    (Story) => {
      // Mock platform APIs
      if (typeof window !== 'undefined' && !window.api) {
        window.api = ${PLATFORM}_MOCKS;
      }
      return Story();
    },
  ],
  ` : ""}

  // Global types (for toolbar customization)
  globalTypes: {
    theme: {
      description: 'Global theme for components',
      defaultValue: 'light',
      toolbar: {
        title: 'Theme',
        icon: 'circlehollow',
        items: ['light', 'dark'],
        dynamicTitle: true,
      },
    },
  },
};

export default preview;
```

### Phase 5: Example Stories Generation

Create initial example stories to demonstrate SOTA patterns:

```typescript
// src/components/Button/Button.stories.tsx
import type { Meta, StoryObj } from '@storybook/${FRAMEWORK}';
import { expect, userEvent, within } from '@storybook/test';
import { Button } from './Button';

const meta = {
  title: 'Components/Button',
  component: Button,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'], // Auto-generate documentation
  argTypes: {
    variant: {
      control: 'select',
      options: ['primary', 'secondary', 'outline'],
    },
    size: {
      control: 'select',
      options: ['small', 'medium', 'large'],
    },
  },
} satisfies Meta<typeof Button>;

export default meta;
type Story = StoryObj<typeof meta>;

// SOTA: Basic variants
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

// SOTA: Interaction test with play function
export const WithInteraction: Story = {
  args: {
    variant: 'primary',
    children: 'Click me',
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const button = canvas.getByRole('button', { name: /click me/i });

    // Test interaction
    await userEvent.click(button);

    // Verify state or behavior
    await expect(button).toBeInTheDocument();
  },
};

// SOTA: Accessibility test
export const AccessibilityTest: Story = {
  args: {
    variant: 'primary',
    children: 'Accessible Button',
  },
  parameters: {
    a11y: {
      config: {
        rules: [
          {
            id: 'button-name',
            enabled: true,
          },
          {
            id: 'color-contrast',
            enabled: true,
          },
        ],
      },
    },
  },
};
```

### Phase 6: Platform-Specific Setup

#### For Tauri Projects:

Generate `.storybook/tauri-mocks.ts`:

```typescript
export const tauriMocks = {
  invoke: async (cmd: string, args?: any) => {
    console.log(`[Tauri Mock] invoke: ${cmd}`, args);

    // Mock responses for common commands
    const mockResponses: Record<string, any> = {
      'read_file': { content: 'Mock file content' },
      'write_file': { success: true },
      'get_config': { theme: 'dark', language: 'en' },
    };

    return mockResponses[cmd] || { success: true };
  },

  listen: (event: string, handler: Function) => {
    console.log(`[Tauri Mock] listen: ${event}`);

    // Return unsubscribe function
    return () => {
      console.log(`[Tauri Mock] unsubscribe: ${event}`);
    };
  },
};

// Inject into window during Storybook initialization
if (typeof window !== 'undefined') {
  (window as any).__TAURI__ = tauriMocks;
}
```

#### For Electron Projects:

Generate `.storybook/electron-mocks.ts`:

```typescript
export const electronMocks = {
  readDir: async (path: string) => {
    console.log(`[Electron Mock] readDir: ${path}`);
    return ['file1.txt', 'file2.txt', 'folder1'];
  },

  readFile: async (path: string) => {
    console.log(`[Electron Mock] readFile: ${path}`);
    return 'Mock file content';
  },

  writeFile: async (path: string, content: string) => {
    console.log(`[Electron Mock] writeFile: ${path}`, content);
    return { success: true };
  },

  saveConfig: async (config: any) => {
    console.log(`[Electron Mock] saveConfig:`, config);
    return { success: true };
  },
};

// Inject into window.api
if (typeof window !== 'undefined') {
  (window as any).api = electronMocks;
}
```

Generate architectural guidance document: `docs/ELECTRON_PATTERNS.md`

### Phase 7: Visual Generation (if enabled and OPENROUTER_API_KEY available)

If user selected visual generation:

```bash
# Generate style guide
python ${CLAUDE_PLUGIN_ROOT}/skills/visual-design/scripts/generate_style_guide.py \
  --framework ${FRAMEWORK} \
  --design-system ${DESIGN_SYSTEM} \
  --output .storybook/public/style-guide.png

# Generate component mockup example
python ${CLAUDE_PLUGIN_ROOT}/skills/visual-design/scripts/generate_mockup.py \
  "Modern ${FRAMEWORK} button component with primary, secondary, and outline variants. \
   ${DESIGN_SYSTEM} design system style. Clean, professional." \
  --output .storybook/public/button-mockup.png
```

### Phase 8: Update package.json Scripts

Add Storybook scripts with SOTA configuration:

```json
{
  "scripts": {
    "storybook": "storybook dev -p 6006",
    "build-storybook": "storybook build",
    "test-storybook": "test-storybook",
    "storybook:test": "storybook dev --test",
    "storybook:coverage": "test-storybook --coverage"
  }
}
```

### Phase 9: Completion Summary

```
✅ Storybook 9 Setup Complete!

Configured for: ${FRAMEWORK} ${VERSION} (${BUNDLER})
Platform: ${PLATFORM}
Design System: ${DESIGN_SYSTEM}

Features Enabled:
${INTERACTION_TESTS ? "✓ Interaction Tests (Vitest + Playwright)" : ""}
${A11Y_TESTS ? "✓ Accessibility Tests (axe-core)" : ""}
${VISUAL_TESTS ? "✓ Visual Regression Tests" : ""}
${COVERAGE ? "✓ Code Coverage (V8)" : ""}
${VISUAL_GENERATION ? "✓ Visual Generation (Style guide & mockups)" : ""}

Next Steps:
1. Run: npm run storybook
2. Open: http://localhost:6006
3. Generate stories: /generate-stories
4. Create components: /create-component

Files Created:
- .storybook/main.ts (Storybook configuration)
- .storybook/preview.ts (Theme & decorators)
${PLATFORM === 'tauri' ? "- .storybook/tauri-mocks.ts (IPC mocks)" : ""}
${PLATFORM === 'electron' ? "- .storybook/electron-mocks.ts (Preload API mocks)" : ""}
${PLATFORM === 'electron' ? "- docs/ELECTRON_PATTERNS.md (Architectural guidance)" : ""}
- src/components/Button/Button.stories.tsx (Example story)
${VISUAL_GENERATION ? "- .storybook/public/style-guide.png (Visual style guide)" : ""}

Documentation: See .storybook/README.md for configuration details
```

## Error Handling

- If framework not detected: Ask user to specify framework manually
- If Node.js < 20: Show upgrade instructions
- If npm < 10: Warn but continue
- If OPENROUTER_API_KEY missing: Skip visual generation, inform user
- If installation fails: Show error, suggest troubleshooting steps

## Notes

- Always use the latest Storybook 9 packages
- Prefer Vite over Webpack for faster builds
- Include SOTA patterns: play functions, a11y tests, coverage
- Make visual generation truly optional
- Provide clear platform-specific guidance (Tauri full support, Electron partial)
