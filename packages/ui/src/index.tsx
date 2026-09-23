import type { ReactNode } from "react";

export function Status({ children }: { children: ReactNode }) {
  return (
    <p role="status" aria-live="polite">
      {children}
    </p>
  );
}
