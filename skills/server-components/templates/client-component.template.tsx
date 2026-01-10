'use client';

import { useState } from 'react';
import type { {{COMPONENT_NAME}}Props } from './types';

/**
 * {{COMPONENT_NAME}} - Client Component
 *
 * This component runs on the client and can:
 * - Use React hooks (useState, useEffect, etc.)
 * - Handle user interactions (onClick, onChange)
 * - Access browser APIs (window, localStorage)
 * - Manage client-side state
 */
export function {{COMPONENT_NAME}}({
  {{PROPS}}
}: {{COMPONENT_NAME}}Props) {
  const [{{STATE_NAME}}, set{{STATE_NAME_CAPITALIZED}}] = useState({{INITIAL_STATE}});

  const handle{{ACTION_NAME}} = () => {
    // Client-side logic
    set{{STATE_NAME_CAPITALIZED}}({{NEW_STATE}});
  };

  return (
    <div className="{{COMPONENT_CLASSNAME}}">
      {/* Interactive UI */}
      <button onClick={handle{{ACTION_NAME}}}>
        {{BUTTON_TEXT}}
      </button>
    </div>
  );
}
