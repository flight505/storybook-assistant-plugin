---
description: Use this skill when the user asks to "analyze performance", "check bundle size", "optimize component", "analyze imports", "reduce bundle", "check for performance issues", or wants to identify and fix performance bottlenecks in their Storybook components with AI-powered suggestions.
---

# Performance Analysis Skill

## Overview

Automatically analyze component performance, bundle size, and render efficiency with AI-powered optimization suggestions.

## What It Analyzes

### Bundle Impact
- Package sizes and tree-shaking
- Heavy dependencies (moment.js, lodash, etc.)
- Unused imports
- Code splitting opportunities

### Render Performance
- Unnecessary re-renders
- Missing React.memo
- Inline function creation
- Large dependency arrays
- Expensive computations without useMemo

### Optimization Opportunities
- Image optimization
- Lazy loading
- Dynamic imports
- Code splitting

## Example Output

```
⚡ Performance Analysis: Button.tsx

Bundle Impact: 45.2KB (gzipped: 12.1KB)
  ❌ lodash: 71KB (using only 'debounce')
     Fix: import debounce from 'lodash/debounce'  // Saves 69KB

  ⚠️  moment.js: 72KB (date formatting only)
     Alternatives:
     [1] date-fns (13KB) ⭐ RECOMMENDED
     [2] Intl API (0KB - native)
     [3] Day.js (2KB)

Render Performance:
  ⚠️  Inline function in render (Line 42)
     onClick={() => handleClick(id)}
     Fix: Use useCallback or extract to stable reference

  ✅ Component properly memoized
  ✅ No expensive computations detected

Apply fixes? [All] [Select] [Skip]
```

## Optimization Rules

### Replace Heavy Packages
```tsx
// ❌ Before: 71KB
import _ from 'lodash';
const debouncedSearch = _.debounce(handleSearch, 300);

// ✅ After: 2KB
import debounce from 'lodash/debounce';
const debouncedSearch = debounce(handleSearch, 300);
```

### Fix Inline Functions
```tsx
// ❌ Before: New function every render
<button onClick={() => handleClick(id)}>Click</button>

// ✅ After: Stable reference
const handleButtonClick = useCallback(() => handleClick(id), [id]);
<button onClick={handleButtonClick}>Click</button>
```

### Add Memoization
```tsx
// ❌ Before: Expensive calculation every render
const filtered = items.filter(item => item.active);

// ✅ After: Memoized
const filtered = useMemo(
  () => items.filter(item => item.active),
  [items]
);
```

## Summary

AI-powered performance analysis:
- Detects bundle bloat
- Suggests lighter alternatives
- Identifies render issues
- One-click fixes

**Result:** 30-40% bundle size reduction, faster renders.
