# Tauri + Storybook Setup Guide

## Overview

Tauri and Storybook work **excellently** together! Storybook runs independently from the Tauri runtime, allowing you to develop and test UI components in isolation without rebuilding the entire desktop application.

## Why It Works

- **Separate Processes**: Storybook runs in the browser (port 6006), Tauri dev server runs separately (port 5173)
- **No Conflicts**: No IPC or native API conflicts
- **Faster Iteration**: Component development without full app rebuilds
- **Framework Agnostic**: Works with any frontend framework (React, Vue, Svelte)

## Development Workflow

```bash
# Terminal 1: Start Tauri development server
npm run tauri dev
# Tauri app runs on http://localhost:5173

# Terminal 2: Start Storybook (in parallel)
npm run storybook
# Storybook runs on http://localhost:6006

# Terminal 3: Run tests in watch mode
npm run test:watch
```

## Project Structure

```
tauri-app/
├── src/
│   ├── components/           # UI components (Storybook-ready)
│   │   ├── Button.tsx
│   │   ├── Button.stories.tsx
│   │   ├── Card.tsx
│   │   └── Card.stories.tsx
│   ├── api/
│   │   └── tauri.ts         # Tauri IPC calls (abstracted)
│   └── main.tsx
├── src-tauri/                # Rust backend
│   ├── src/
│   └── tauri.conf.json
├── .storybook/               # Storybook configuration
│   ├── main.ts
│   ├── preview.ts
│   └── tauri-mocks.ts       # IPC mocks for stories
└── package.json
```

## Component Architecture Pattern

**Best Practice: Dependency Injection**

Keep UI components Tauri-agnostic by injecting IPC functionality:

```typescript
// ✅ Good: Testable component
interface ApiClient {
  fetchData: () => Promise<Data>;
  saveData: (data: Data) => Promise<void>;
}

function DataComponent({ api }: { api: ApiClient }) {
  const { data, isLoading } = useQuery(['data'], api.fetchData);

  if (isLoading) return <Spinner />;

  return (
    <div>
      <h1>{data.title}</h1>
      <button onClick={() => api.saveData(data)}>Save</button>
    </div>
  );
}

// Storybook story with mock API
export const Default: Story = {
  args: {
    api: {
      fetchData: async () => ({ title: 'Mock Data' }),
      saveData: async (data) => console.log('Mock save:', data),
    },
  },
};

// Production usage with real Tauri IPC
function App() {
  const tauriApi: ApiClient = {
    fetchData: () => invoke('fetch_data'),
    saveData: (data) => invoke('save_data', { data }),
  };

  return <DataComponent api={tauriApi} />;
}
```

## IPC Mocking in Storybook

The plugin auto-generates `.storybook/tauri-mocks.ts`:

```typescript
// .storybook/tauri-mocks.ts
export const tauriMocks = {
  invoke: async (cmd: string, args?: any) => {
    console.log(`[Tauri Mock] invoke: ${cmd}`, args);

    // Mock responses for common commands
    const mockResponses: Record<string, any> = {
      'fetch_data': {
        title: 'Mock Title',
        items: ['Item 1', 'Item 2', 'Item 3']
      },
      'save_data': { success: true },
      'read_file': { content: 'Mock file content' },
      'write_file': { success: true },
      'get_config': {
        theme: 'dark',
        language: 'en'
      },
    };

    return mockResponses[cmd] || { success: true };
  },

  listen: (event: string, handler: Function) => {
    console.log(`[Tauri Mock] listen: ${event}`);

    // Simulate event after 1 second (optional)
    setTimeout(() => {
      handler({ payload: { message: 'Mock event data' } });
    }, 1000);

    // Return unsubscribe function
    return () => {
      console.log(`[Tauri Mock] unsubscribe: ${event}`);
    };
  },

  emit: async (event: string, payload?: any) => {
    console.log(`[Tauri Mock] emit: ${event}`, payload);
  },
};

// Auto-inject during Storybook initialization
if (typeof window !== 'undefined') {
  (window as any).__TAURI__ = tauriMocks;
}
```

**Usage in preview.ts:**

```typescript
// .storybook/preview.ts
import { tauriMocks } from './tauri-mocks';

const preview: Preview = {
  decorators: [
    (Story) => {
      // Inject Tauri mocks for all stories
      if (typeof window !== 'undefined' && !window.__TAURI__) {
        (window as any).__TAURI__ = tauriMocks;
      }
      return <Story />;
    },
  ],
};
```

## Testing Strategy

### 1. Component Tests in Storybook
- Test UI logic and rendering
- Test user interactions (clicks, typing)
- Test accessibility (WCAG compliance)
- Mock Tauri IPC calls

### 2. E2E Tests with WebDriver
- Test full Tauri application
- Test actual IPC integration
- Test native APIs (file system, notifications, etc.)
- Use Tauri's WebDriver capabilities

```bash
# E2E tests (separate from Storybook)
npm run test:e2e
```

## Port Configuration

Update `tauri.conf.json` if needed:

```json
{
  "build": {
    "devUrl": "http://localhost:5173",
    "beforeDevCommand": "npm run dev"
  }
}
```

Storybook will run on a different port (6006 by default), so no conflicts.

## Package.json Scripts

```json
{
  "scripts": {
    "dev": "vite",
    "tauri": "tauri",
    "tauri:dev": "tauri dev",
    "storybook": "storybook dev -p 6006",
    "build-storybook": "storybook build",
    "test": "vitest",
    "test:watch": "vitest --watch",
    "test:storybook": "test-storybook"
  }
}
```

## Common Patterns

### Pattern 1: Custom Hooks for IPC

```typescript
// hooks/useTauriInvoke.ts
function useTauriInvoke<T>(cmd: string, args?: any) {
  return useQuery([cmd, args], () => invoke<T>(cmd, args));
}

// Component
function DataList() {
  const { data } = useTauriInvoke<string[]>('fetch_items');
  return <ul>{data?.map(item => <li key={item}>{item}</li>)}</ul>;
}

// Story with mock
export const Default: Story = {
  decorators: [
    (Story) => {
      window.__TAURI__.invoke = async (cmd) => {
        if (cmd === 'fetch_items') return ['Mock 1', 'Mock 2'];
        return null;
      };
      return <Story />;
    },
  ],
};
```

### Pattern 2: Context Provider

```typescript
// TauriContext.tsx
const TauriContext = createContext<ApiClient | null>(null);

export function TauriProvider({ children, api }: { children: ReactNode, api?: ApiClient }) {
  const defaultApi: ApiClient = {
    fetchData: () => invoke('fetch_data'),
    saveData: (data) => invoke('save_data', { data }),
  };

  return (
    <TauriContext.Provider value={api || defaultApi}>
      {children}
    </TauriContext.Provider>
  );
}

// Storybook decorator
decorators: [
  (Story) => (
    <TauriProvider api={mockApi}>
      <Story />
    </TauriProvider>
  ),
]
```

## Best Practices

### ✅ Do's

1. **Decouple UI from IPC**: Use dependency injection or context providers
2. **Mock Tauri APIs in Stories**: Provide realistic mock data
3. **Test UI logic in Storybook**: Interaction and accessibility tests
4. **Test IPC integration separately**: Use E2E tests for full integration
5. **Run Storybook in parallel**: Develop components while Tauri app runs
6. **Use TypeScript**: Strong typing prevents IPC command typos

### ❌ Don'ts

1. **Don't import `@tauri-apps/api` directly in components**: Use abstraction layer
2. **Don't test Tauri IPC in Storybook**: Mock it, test in E2E
3. **Don't skip component testing**: Storybook tests are faster than E2E
4. **Don't hardcode Tauri calls**: Makes components hard to test and maintain
5. **Don't forget error handling**: Mock error scenarios in stories

## Production Examples

- [offline-first-react-router-tauri-template](https://github.com/jhovadev/offline-first-react-router-tauri-template) - React + Tauri + Storybook 10
- [tauri-tray-app](https://github.com/jondot/tauri-tray-app) - React + Zustand + shadcn/ui + Storybook

## Troubleshooting

### Issue: `__TAURI__` is undefined in stories

**Solution**: Ensure tauri-mocks are loaded in preview.ts decorator

### Issue: IPC commands not working in Tauri app

**Solution**: This is expected - Storybook mocks don't affect the Tauri app. Test IPC in E2E tests.

### Issue: Port conflicts

**Solution**: Tauri (5173) and Storybook (6006) use different ports. If conflicts occur, change ports in configs.

## Summary

**Tauri + Storybook = Perfect Match!** 🚀

- Full support with no workarounds needed
- Faster development (no app rebuilds for UI changes)
- Better testing (component tests + E2E tests)
- Clean architecture (decoupled UI from backend)
- Production-proven patterns available
