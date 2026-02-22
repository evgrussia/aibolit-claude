import '@testing-library/jest-dom/vitest';
import { vi } from 'vitest';
import React from 'react';

// Mock framer-motion to avoid animation issues in tests
vi.mock('framer-motion', () => {
  const motion = new Proxy({}, {
    get: (_target, prop: string) => {
      return React.forwardRef(function MotionComponent(
        props: Record<string, unknown>,
        ref: React.Ref<HTMLElement>,
      ) {
        const {
          initial: _i, animate: _a, exit: _e, transition: _t,
          whileHover: _wh, whileTap: _wt, variants: _v,
          ...rest
        } = props;
        return React.createElement(prop, { ...rest, ref });
      });
    },
  });

  return {
    motion,
    AnimatePresence: ({ children }: { children: React.ReactNode }) => children,
  };
});
