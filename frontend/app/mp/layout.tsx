import type { ReactNode } from "react";

import Sidebar from "@/components/mp/Sidebar";

interface DashboardLayoutProps {
  children: ReactNode;
}

export default function DashboardLayout({
  children,
}: DashboardLayoutProps) {
  return (
    <>
      <Sidebar />

      <main className="min-h-screen bg-[#F7F9FC] md:ml-[280px]">
        <div className="p-4 md:p-10">
          {children}
        </div>
      </main>
    </>
  );
}
