import type { ReactNode } from "react";
import { StaffNavigation } from "./navigation";

export default function StaffLayout({ children }: { children: ReactNode }) {
  return (
    <>
      <StaffNavigation />
      {children}
    </>
  );
}
