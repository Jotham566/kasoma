"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const destinations = [
  ["/admin/content", "Content & review"],
  ["/admin/content/imports", "Imports"],
  ["/admin/flags", "Flags"],
  ["/admin/grading", "Grading review"],
  ["/admin/data-requests", "Privacy review"],
  ["/admin/operations", "Operations"],
  ["/admin/audit", "Audit"],
] as const;

export function StaffNavigation() {
  const pathname = usePathname();
  return <WorkspaceNavigation key={pathname} pathname={pathname} />;
}

function WorkspaceNavigation({ pathname }: { pathname: string }) {
  const [open, setOpen] = useState(false);
  return (
    <header className="staff-header">
      <div className="staff-header-inner">
        <div>
          <p className="staff-title">Kasoma · Staff workspace</p>
          <p className="staff-caption">
            Synthetic development · Fictional data only
          </p>
        </div>
        <Link
          className="ui-text-link staff-sign-in"
          href="/onboarding"
          prefetch={false}
        >
          Staff sign-in
        </Link>
        <button
          type="button"
          className="staff-menu-toggle"
          aria-expanded={open}
          aria-controls="staff-workspace-navigation"
          onClick={() => setOpen(!open)}
        >
          <span>Workspace menu</span>
          <svg aria-hidden="true" viewBox="0 0 24 24" width="20" height="20">
            <path
              d={open ? "m6 15 6-6 6 6" : "m6 9 6 6 6-6"}
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            />
          </svg>
        </button>
        <nav
          id="staff-workspace-navigation"
          aria-label="Workspace navigation"
          className={`learner-navigation staff-navigation${open ? " is-open" : ""}`}
        >
          {destinations.map(([href, label]) => (
            <Link
              key={href}
              href={href}
              prefetch={false}
              onClick={() => setOpen(false)}
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
