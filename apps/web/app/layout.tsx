import type { ReactNode } from "react";
import "./globals.css";
export const metadata = {
  title: "Kasoma",
  description: "Know what to revise next.",
};
export default function Layout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
