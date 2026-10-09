"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const destinations = [
  ["/", "Home"],
  ["/revise", "Revise"],
  ["/progress", "Progress"],
  ["/history", "History"],
  ["/onboarding", "Profile & settings"],
] as const;

export function LearnerNavigation() {
  const pathname = usePathname();
  if (pathname.startsWith("/admin")) return null;
  return (
    <header className="learner-header">
      <div className="learner-header-inner">
        <Link
          className="kasoma-brand"
          href="/"
          prefetch={false}
          aria-label="Kasoma home"
        >
          <span className="brand-mark" aria-hidden="true">
            k
          </span>
          <span>
            kasoma
            <span className="brand-caption">
              A little practice. Clearer progress.
            </span>
          </span>
        </Link>
        <nav aria-label="Learner navigation" className="learner-navigation">
          {destinations.map(([href, label]) => (
            <Link
              key={href}
              href={href}
              prefetch={false}
              aria-current={pathname === href ? "page" : undefined}
            >
              {label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
