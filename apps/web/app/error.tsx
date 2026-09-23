"use client";
export default function Error({ reset }: { reset: () => void }) {
  return (
    <main>
      <h1>Kasoma is temporarily unavailable</h1>
      <button onClick={reset}>Try again</button>
    </main>
  );
}
