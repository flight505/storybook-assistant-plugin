---
description: Use this skill when the user asks to "create server component", "add React Server Component", "use async component", "setup Next.js 15", "use React 19", "implement PPR", "add Server Actions", mentions "use server", "use client", "Suspense boundaries", or wants to build modern server-rendered components with React 19 and Next.js 15 patterns.
---

# Server Components Skill

## Overview

Generate modern React Server Components with React 19 and Next.js 15 patterns including async/await data fetching, streaming with Suspense, Server Actions, and Partial Prerendering (PPR).

This skill provides templates and best practices for building server-first applications with client-side interactivity only where needed.

## What This Skill Provides

### React Server Components
Modern server-rendered components with:
- **Async components**: Fetch data directly in components
- **No useEffect needed**: Server-side data fetching
- **Reduced bundle size**: Server code stays on server
- **Automatic code splitting**: Client boundaries only

### Client Component Boundaries
Strategic client-side interactivity:
- **"use client" directive**: Mark client boundaries
- **State management**: useState, useContext where needed
- **Event handlers**: onClick, onChange for interactivity
- **Browser APIs**: Access window, document, localStorage

### Streaming & Suspense
Progressive rendering patterns:
- **Suspense boundaries**: Stream components as they load
- **Loading skeletons**: Show placeholders during fetch
- **Error boundaries**: Handle server errors gracefully
- **Nested Suspense**: Granular loading states

### React 19 Features
Latest React patterns:
- **useActionState**: Form submissions without client JS
- **use() hook**: Unwrap promises in components
- **Server Actions**: Backend mutations from client
- **Optimistic updates**: Instant UI feedback

### Next.js 15 Patterns
Framework-specific optimizations:
- **Partial Prerendering (PPR)**: Mix static and dynamic
- **Improved caching**: Smarter fetch deduplication
- **Turbopack**: Faster builds and HMR
- **Server-only code**: Prevents client bundling

## Component Patterns

### Basic Server Component

```tsx
// app/ProductList.tsx (Server Component)
import { fetchProducts } from '@/lib/api';
import { ProductCard } from './ProductCard';

// ✨ Async Server Component
export default async function ProductList({ category }: Props) {
  // Direct data fetching - no useEffect!
  const products = await fetchProducts(category);

  return (
    <div className="grid grid-cols-3 gap-4">
      {products.map(product => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  );
}
```

### Client Component for Interactivity

```tsx
// app/ProductCard.client.tsx
'use client'; // ✨ Client boundary

import { useState } from 'react';
import { addToCart } from '@/actions/cart';

export function ProductCard({ product }: Props) {
  const [loading, setLoading] = useState(false);

  const handleAddToCart = async () => {
    setLoading(true);
    await addToCart(product.id);
    setLoading(false);
  };

  return (
    <article>
      <img src={product.image} alt={product.name} />
      <h3>{product.name}</h3>
      <p>${product.price}</p>

      {/* ✨ Client-side interactivity */}
      <button onClick={handleAddToCart} disabled={loading}>
        {loading ? 'Adding...' : 'Add to Cart'}
      </button>
    </article>
  );
}
```

### Streaming with Suspense

```tsx
// app/Dashboard.tsx
import { Suspense } from 'react';
import { UserStats } from './UserStats';
import { RecentActivity } from './RecentActivity';
import { Skeleton } from './Skeleton';

export default function Dashboard() {
  return (
    <div>
      <h1>Dashboard</h1>

      {/* ✨ Stream components independently */}
      <Suspense fallback={<Skeleton type="stats" />}>
        <UserStats />  {/* Slow fetch */}
      </Suspense>

      <Suspense fallback={<Skeleton type="activity" />}>
        <RecentActivity />  {/* Fast fetch */}
      </Suspense>
    </div>
  );
}
```

### Server Actions (React 19)

```tsx
// app/CommentForm.tsx
'use client';

import { useActionState } from 'react';
import { postComment } from '@/actions/comments';

export function CommentForm({ postId }: Props) {
  const [state, submitAction, isPending] = useActionState(
    async (prevState, formData) => {
      const comment = formData.get('comment') as string;

      try {
        await postComment(postId, comment);
        return { success: true, message: 'Comment posted!' };
      } catch (error) {
        return { success: false, message: 'Failed to post comment' };
      }
    },
    { success: false, message: '' }
  );

  return (
    <form action={submitAction}>
      <textarea name="comment" required />
      <button disabled={isPending}>
        {isPending ? 'Posting...' : 'Post Comment'}
      </button>
      {state.message && <p>{state.message}</p>}
    </form>
  );
}

// actions/comments.ts
'use server';

export async function postComment(postId: string, comment: string) {
  const user = await getCurrentUser();
  await db.comments.create({
    data: { postId, userId: user.id, content: comment }
  });
}
```

### Partial Prerendering (Next.js 15)

```tsx
// app/page.tsx
export const experimental_ppr = true;

export default function ProductPage() {
  return (
    <>
      {/* ✨ Static: Prerendered at build time */}
      <ProductHeader />
      <ProductDescription />

      {/* ✨ Dynamic: Streamed for each request */}
      <Suspense fallback={<ReviewsSkeleton />}>
        <UserReviews />  {/* Personalized content */}
      </Suspense>

      <Suspense fallback={<RecommendationsSkeleton />}>
        <Recommendations />  {/* User-specific */}
      </Suspense>
    </>
  );
}
```

## Templates

### Server Component Template

```tsx
// templates/server-component.template
import { Suspense } from 'react';

interface {{COMPONENT_NAME}}Props {
  {{PROP_NAME}}: {{PROP_TYPE}};
}

export default async function {{COMPONENT_NAME}}({
  {{PROP_NAME}}
}: {{COMPONENT_NAME}}Props) {
  // ✨ Server-side data fetching
  const data = await fetch{{DATA_NAME}}({{PROP_NAME}});

  return (
    <div>
      <h2>{{COMPONENT_NAME}}</h2>
      {/* Render data */}
    </div>
  );
}
```

### Client Component Template

```tsx
// templates/client-component.template
'use client';

import { useState } from 'react';

interface {{COMPONENT_NAME}}Props {
  {{PROP_NAME}}: {{PROP_TYPE}};
}

export function {{COMPONENT_NAME}}({
  {{PROP_NAME}}
}: {{COMPONENT_NAME}}Props) {
  const [state, setState] = useState(initialValue);

  const handleAction = () => {
    // Client-side logic
  };

  return (
    <div>
      {/* Interactive UI */}
    </div>
  );
}
```

## Storybook Integration

### Mocking Server Components

```tsx
// ProductList.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import ProductList from './ProductList';

const meta = {
  title: 'Server/ProductList',
  component: ProductList,
  parameters: {
    nextjs: {
      appDirectory: true,  // Enable App Router
    },
  },
} satisfies Meta<typeof ProductList>;

export default meta;
type Story = StoryObj<typeof meta>;

// ✨ Mock server data
export const Default: Story = {
  parameters: {
    async loaders() {
      return {
        products: [
          { id: 1, name: 'Product 1', price: 29.99 },
          { id: 2, name: 'Product 2', price: 39.99 },
        ],
      };
    },
  },
};

export const Loading: Story = {
  parameters: {
    async loaders() {
      // Simulate slow load
      await new Promise(resolve => setTimeout(resolve, 2000));
      return { products: [] };
    },
  },
};

export const Error: Story = {
  parameters: {
    async loaders() {
      throw new Error('Failed to fetch products');
    },
  },
};
```

## Best Practices

### Server vs Client Decision Tree

```
Does it need interactivity (state, events)?
  ├─ YES → Client Component ('use client')
  └─ NO → Can it fetch data?
      ├─ YES → Server Component (async)
      └─ NO → Server Component (static)
```

### Component Colocation

```
app/
├── ProductList/
│   ├── ProductList.tsx          # Server Component
│   ├── ProductCard.client.tsx   # Client Component
│   ├── ProductCard.stories.tsx  # Storybook
│   └── ProductList.test.tsx     # Tests
```

### Data Fetching Patterns

```tsx
// ✅ Server Component - Direct fetch
async function ServerComponent() {
  const data = await fetchData();
  return <div>{data}</div>;
}

// ✅ Client Component - Props from server
function ClientComponent({ data }: { data: Data }) {
  const [selected, setSelected] = useState(data[0]);
  return <div onClick={() => setSelected(data[1])}>{selected}</div>;
}

// ❌ Client Component - Don't fetch on client if avoidable
function ClientComponent() {
  const [data, setData] = useState(null);
  useEffect(() => {
    fetchData().then(setData);  // Prefer server fetch
  }, []);
}
```

### Minimize Client Boundaries

```tsx
// ❌ Entire component is client
'use client';
export default function Page() {
  return (
    <div>
      <Header />  {/* Could be server */}
      <Content /> {/* Could be server */}
      <InteractiveButton />  {/* Needs client */}
    </div>
  );
}

// ✅ Only interactive part is client
export default function Page() {
  return (
    <div>
      <Header />  {/* Server */}
      <Content /> {/* Server */}
      <InteractiveButton />  {/* Client */}
    </div>
  );
}
```

## References

- **Templates**: `skills/server-components/templates/`
- **Examples**: `skills/server-components/examples/server-patterns.md`
- **React 19 Docs**: https://react.dev/blog/2024/12/05/react-19
- **Next.js 15 Docs**: https://nextjs.org/docs

## Summary

Build modern React applications with:
1. **Server Components** for data fetching (no useEffect)
2. **Client Components** only where needed (interactivity)
3. **Streaming** with Suspense (progressive rendering)
4. **Server Actions** for mutations (React 19)
5. **PPR** for optimal performance (Next.js 15)

**Result:** Faster, smaller, more maintainable applications with better UX.
