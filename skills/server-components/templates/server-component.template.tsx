import { Suspense } from 'react';
import type { {{COMPONENT_NAME}}Props } from './types';

/**
 * {{COMPONENT_NAME}} - Server Component
 *
 * This component runs on the server and can:
 * - Fetch data directly with async/await
 * - Access backend resources (database, APIs)
 * - Keep sensitive code on server
 * - Reduce client bundle size
 */
export default async function {{COMPONENT_NAME}}({
  {{PROPS}}
}: {{COMPONENT_NAME}}Props) {
  // ✨ Server-side data fetching
  const data = await fetch{{DATA_NAME}}({{FETCH_PARAMS}});

  return (
    <div className="{{COMPONENT_CLASSNAME}}">
      <h2>{{COMPONENT_TITLE}}</h2>

      <Suspense fallback={<{{LOADING_COMPONENT}} />}>
        {/* Render fetched data */}
        {data.map(item => (
          <{{CHILD_COMPONENT}} key={item.id} {...item} />
        ))}
      </Suspense>
    </div>
  );
}
