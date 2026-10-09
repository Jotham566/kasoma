"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const destinations = [
  ["/admin/content", "Content & review"],
  ["/admin/content/imports", "Imports"],
  ["/admin/flags", "Flags"],
  ["/admin/data-requests", "Privacy review"],
  ["/admin/operations", "Operations"],
] as const;

export function StaffNavigation() {
  const pathname = usePathname();
  return (
    <header className="staff-header">
      <div className="staff-header-inner">
        <div>
          <p className="staff-title">Kasoma · Staff workspace</p>
          <p className="staff-caption">
            Synthetic development · Access checked by each service
          </p>
        </div>
        <Link className="ui-text-link" href="/onboarding" prefetch={false}>
          Staff sign-in
        </Link>
        <nav
          aria-label="Workspace navigation"
          className="learner-navigation staff-navigation"
        >
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
