import type { ReactNode } from "react";
import "./globals.css";
import { LearnerNavigation } from "./learner-navigation";
export const metadata = {
  title: "Kasoma",
  description: "Know what to revise next.",
};
export default function Layout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <a className="skip-link" href="#main-content">
          Skip to content
        </a>
        <LearnerNavigation />
        <div id="main-content" tabIndex={-1}>
          {children}
        </div>
      </body>
    </html>
  );
}
