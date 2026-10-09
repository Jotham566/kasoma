import type { ReactNode } from "react";

export function Status({ children }: { children: ReactNode }) {
  return (
    <p role="status" aria-live="polite">
      {children}
    </p>
  );
}

export function SavedProgress({
  answered,
  total,
}: {
  answered: number;
  total: number;
}) {
  return (
    <div className="saved-progress">
      <p>
        {answered} of {total} answers saved
      </p>
      <progress aria-label="Saved answers" value={answered} max={total} />
    </div>
  );
}
