# Electron + Storybook: Limitations & Solutions

## Overview

Storybook works with Electron, but with **significant limitations** due to Electron's architecture and Storybook's iframe-based rendering. This document explains what works, what doesn't, and how to architect your components for maximum testability.

## ⚠️ Major Limitation: Iframe Incompatibility

**The Core Issue:**
- Storybook renders stories in iframes
- Electron modules (`electron`, `ipcRenderer`) are not available in iframe context
- Webpack's `electron-renderer` target creates externals that fail in iframes

**Impact:**
- Components with direct `electron` imports **won't work** in Storybook
- IPC calls **cannot be tested** in Storybook (requires E2E tests)
- Main process code **cannot be accessed** from Storybook

## What Works ✅

### 1. Pure UI Components

Components that don't interact with Electron APIs work perfectly:

```typescript
// ✅ Works perfectly in Storybook
function Button({ variant, onClick }) {
  return (
    <button
      className={`btn-${variant}`}
      onClick={onClick}
    >
      Click Me
    </button>
  );
}

// Storybook story
export const Primary: Story = {
  args: {
    variant: 'primary',
    onClick: () => console.log('clicked'),
  },
};
```

### 2. Design System Components

UI libraries and design systems work without issues:

```typescript
// ✅ Works - Material UI, Ant Design, shadcn/ui, etc.
import { Card, CardContent, CardHeader } from '@mui/material';

function ProfileCard({ name, avatar, bio }) {
  return (
    <Card>
      <CardHeader title={name} avatar={<Avatar src={avatar} />} />
      <CardContent>{bio}</CardContent>
    </Card>
  );
}
```

### 3. Stateful Components (without Electron)

State management works normally:

```typescript
// ✅ Works - useState, useReducer, Redux, Zustand, etc.
function Counter() {
  const [count, setCount] = useState(0);
  return (
    <div>
      <button onClick={() => setCount(count + 1)}>
        Count: {count}
      </button>
    </div>
  );
}
```

## What Doesn't Work ❌

### 1. Direct Electron Module Imports

```typescript
// ❌ Fails in Storybook
import { ipcRenderer } from 'electron';

function FileReader() {
  const [files, setFiles] = useState([]);

  useEffect(() => {
    ipcRenderer.invoke('read-dir', '/path').then(setFiles);
  }, []);

  return <ul>{files.map(f => <li>{f}</li>)}</ul>;
}
```

**Error:** `Cannot find module 'electron'` or `require is not defined`

### 2. Preload API Calls (without mocking)

```typescript
// ❌ Fails in Storybook (window.api undefined)
function ConfigPanel() {
  const [config, setConfig] = useState(null);

  useEffect(() => {
    window.api.getConfig().then(setConfig);  // window.api undefined!
  }, []);

  return <div>{config?.theme}</div>;
}
```

**Error:** `Cannot read property 'getConfig' of undefined`

### 3. Native Module Access

```typescript
// ❌ Fails - Native modules not available
import { app, BrowserWindow } from 'electron';

function WindowControls() {
  const minimize = () => {
    const win = BrowserWindow.getFocusedWindow();
    win?.minimize();  // Doesn't work in Storybook
  };

  return <button onClick={minimize}>Minimize</button>;
}
```

## Architectural Solution: Container/Presentational Pattern

**The recommended approach:** Separate UI components from Electron logic.

### Pattern Implementation

```typescript
// ============================================
// 1. Pure UI Component (Presentational)
// ============================================
// ✅ Testable in Storybook
interface FileListProps {
  files: string[];
  isLoading: boolean;
  error?: string;
  onRefresh: () => void;
}

function FileList({ files, isLoading, error, onRefresh }: FileListProps) {
  if (isLoading) return <Spinner />;
  if (error) return <ErrorMessage message={error} />;

  return (
    <div>
      <button onClick={onRefresh}>Refresh</button>
      <ul>
        {files.map(file => (
          <li key={file}>{file}</li>
        ))}
      </ul>
    </div>
  );
}

// ============================================
// 2. Container Component (Electron-aware)
// ============================================
// ❌ Not testable in Storybook (but that's OK)
function FileListContainer() {
  const [files, setFiles] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>();

  const loadFiles = async () => {
    setIsLoading(true);
    try {
      const result = await window.api.readDir('/path');
      setFiles(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadFiles();
  }, []);

  return (
    <FileList
      files={files}
      isLoading={isLoading}
      error={error}
      onRefresh={loadFiles}
    />
  );
}

// ============================================
// 3. Storybook Stories
// ============================================
// Test pure component with different states
export const Default: Story = {
  args: {
    files: ['file1.txt', 'file2.txt', 'folder1'],
    isLoading: false,
    onRefresh: () => console.log('Refresh clicked'),
  },
};

export const Loading: Story = {
  args: {
    files: [],
    isLoading: true,
    onRefresh: () => {},
  },
};

export const Error: Story = {
  args: {
    files: [],
    isLoading: false,
    error: 'Failed to read directory',
    onRefresh: () => {},
  },
};

export const Empty: Story = {
  args: {
    files: [],
    isLoading: false,
    onRefresh: () => {},
  },
};
```

### Benefits of This Pattern

✅ **Pure component is fully testable** in Storybook
✅ **All states can be tested**: Loading, error, empty, populated
✅ **Interaction tests work**: Click handlers, user input
✅ **Accessibility tests work**: WCAG compliance
✅ **Container handles Electron complexity**: IPC, error handling
✅ **Easy to refactor**: Change IPC implementation without touching UI
✅ **Type-safe**: TypeScript ensures interface consistency

## Webpack Configuration

The plugin auto-generates this configuration:

```typescript
// .storybook/main.ts
const config: StorybookConfig = {
  // ... other config

  webpackFinal: async (config) => {
    // Override electron-renderer target
    config.target = 'web';

    // Clear Electron externals
    config.externals = {};

    // Mock electron module
    config.resolve.alias = {
      ...(config.resolve?.alias || {}),
      electron: false,
    };

    return config;
  },
};
```

## Preload API Mocking

The plugin auto-generates mock utilities:

```typescript
// .storybook/electron-mocks.ts
export const electronMocks = {
  // File system APIs
  readDir: async (path: string) => {
    console.log(`[Mock] readDir: ${path}`);
    return ['file1.txt', 'file2.txt', 'folder1'];
  },

  readFile: async (path: string) => {
    console.log(`[Mock] readFile: ${path}`);
    return 'Mock file content';
  },

  writeFile: async (path: string, content: string) => {
    console.log(`[Mock] writeFile: ${path}`);
    return { success: true };
  },

  // Config APIs
  getConfig: async () => {
    console.log(`[Mock] getConfig`);
    return {
      theme: 'dark',
      language: 'en',
      fontSize: 14,
    };
  },

  saveConfig: async (config: any) => {
    console.log(`[Mock] saveConfig:`, config);
    return { success: true };
  },

  // Dialog APIs
  showOpenDialog: async (options: any) => {
    console.log(`[Mock] showOpenDialog:`, options);
    return {
      canceled: false,
      filePaths: ['/mock/selected/file.txt'],
    };
  },

  // Window APIs
  minimize: () => console.log(`[Mock] minimize`),
  maximize: () => console.log(`[Mock] maximize`),
  close: () => console.log(`[Mock] close`),
};

// Auto-inject into window.api
if (typeof window !== 'undefined') {
  (window as any).api = electronMocks;
}
```

**Usage in preview.ts:**

```typescript
// .storybook/preview.ts
import { electronMocks } from './electron-mocks';

const preview: Preview = {
  decorators: [
    (Story) => {
      // Inject Electron mocks
      if (typeof window !== 'undefined' && !window.api) {
        (window as any).api = electronMocks;
      }
      return <Story />;
    },
  ],
};
```

## Testing Strategy

### 1. Storybook (Component Tests)
- **Test pure UI components**
- Test rendering logic
- Test user interactions
- Test accessibility
- Test different states (loading, error, empty)

### 2. Unit Tests (Jest/Vitest)
- Test business logic
- Test state management
- Test utility functions
- Mock Electron APIs

### 3. E2E Tests (Spectron, Playwright + Electron)
- **Test full Electron integration**
- Test IPC communication
- Test main process <-> renderer interaction
- Test native APIs (file system, dialogs, etc.)

```bash
# Component tests (Storybook)
npm run test:storybook

# Unit tests
npm run test

# E2E tests (full Electron app)
npm run test:e2e
```

## Alternative: Electronic-Stories

For Electron-specific component development, consider [Electronic-Stories](https://github.com/electron-userland/electronic-stories):
- Purpose-built for Electron
- Runs as an Electron app (native environment)
- Better integration with Electron APIs
- Less iframe-related issues

**Trade-off:**
- Storybook: Better ecosystem, more addons, better documentation
- Electronic-Stories: Better Electron integration, fewer workarounds

## Summary

| Aspect | Support Level | Recommendation |
|--------|--------------|----------------|
| Pure UI components | ✅ Full | Use Storybook extensively |
| Design system components | ✅ Full | Test in Storybook |
| Stateful components (no Electron) | ✅ Full | Test in Storybook |
| Components with Electron imports | ❌ Not supported | Refactor using container/presentational pattern |
| IPC testing | ❌ Not supported | Use E2E tests |
| Main process code | ❌ Not supported | Not applicable to Storybook |

## Best Practices

### ✅ Do's

1. **Use container/presentational pattern**: Separate UI from Electron logic
2. **Test pure components in Storybook**: Faster, better DX
3. **Mock preload APIs**: Provide realistic mocks in Storybook
4. **Test IPC in E2E tests**: Use Spectron or Playwright
5. **Use TypeScript**: Prevent `window.api` typos
6. **Document what's tested where**: Clarity on test coverage

### ❌ Don'ts

1. **Don't import `electron` in components**: Use abstraction layer
2. **Don't skip Electron limitations**: Accept and work with them
3. **Don't try to test IPC in Storybook**: Won't work, use E2E
4. **Don't couple UI to Electron**: Makes testing impossible
5. **Don't ignore E2E tests**: They're essential for Electron integration

## Conclusion

**Electron + Storybook works, but requires discipline:**
- Accept architectural constraints
- Separate UI from Electron logic
- Use right tool for right test (Storybook for UI, E2E for integration)
- Follow container/presentational pattern religiously

With this approach, you get:
- ✅ Fast component development in Storybook
- ✅ Comprehensive UI testing
- ✅ Electron integration via E2E tests
- ✅ Maintainable, testable codebase
