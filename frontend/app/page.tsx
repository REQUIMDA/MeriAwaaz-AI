"use client";

import { useState } from "react";

import Header from "@/components/layout/Header";
import Hero from "@/components/landing/Hero";
import RoleSelection from "@/components/landing/RoleSelection";
import Footer from "@/components/layout/Footer";

export default function Home() {
  const [role, setRole] = useState<"citizen" | "mp" | null>(null);

  return (
    <>
      <Header />

      <main className="min-h-[calc(100vh-64px)] bg-[#f7f9fc] px-6 py-16">
        <div className="mx-auto max-w-5xl">
          <Hero hidden={role !== null} />

          <RoleSelection
            role={role}
            setRole={setRole}
          />
        </div>
      </main>

      <Footer />
    </>
  );
}