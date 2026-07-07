"use client";

import { useRouter } from "next/navigation";
import { CheckCircle2, Home } from "lucide-react";

import Navbar from "@/components/citizen/Navbar";
import BottomNav from "@/components/citizen/BottomNav";

export default function SuccessPage() {
  const router = useRouter();

  return (
    <>
      <Navbar />

      <main className="min-h-screen bg-[#f7f9fc] px-6 py-20">
        <div className="mx-auto flex max-w-2xl flex-col items-center text-center">

          {/* Success Icon */}

          <div className="mb-8 flex h-28 w-28 items-center justify-center rounded-full bg-green-100">
            <CheckCircle2
              size={64}
              className="text-green-600"
            />
          </div>

          {/* Heading */}

          <h1 className="mb-4 text-5xl font-bold text-black">
            Issue Submitted Successfully!
          </h1>

          {/* Description */}

          <p className="mb-10 max-w-xl text-lg leading-8 text-[#43474b]">
            Thank you for helping improve your constituency.
            Your complaint has been securely recorded and will
            now be processed by the AI engine before being
            forwarded to the appropriate authorities.
          </p>

          {/* Tracking Card */}

          <div className="mb-10 w-full rounded-3xl border border-[#e6edf3] bg-white p-8 shadow-sm">

            <p className="mb-2 text-sm uppercase tracking-[0.2em] text-gray-500">
              Complaint ID
            </p>

            <h2 className="mb-6 text-3xl font-bold">
              MA-2026-001245
            </h2>

            <div className="rounded-xl bg-[#f7f9fc] p-4">

              <p className="text-sm text-[#43474b]">
                Current Status
              </p>

              <p className="mt-2 text-lg font-semibold text-green-600">
                Received & Awaiting AI Analysis
              </p>

            </div>

          </div>

          {/* Buttons */}

          <div className="flex flex-wrap items-center justify-center gap-4">

            <button
              onClick={() => router.push("/citizen/dashboard")}
              className="flex items-center gap-2 rounded-full bg-black px-8 py-4 font-semibold text-white transition hover:scale-105"
            >
              <Home size={20} />
              Return Home
            </button>

            <button
              onClick={() => router.push("/citizen/new-issue")}
              className="rounded-full border border-gray-300 px-8 py-4 font-semibold transition hover:bg-gray-100"
            >
              Submit Another Issue
            </button>

          </div>

        </div>
      </main>

      <BottomNav />
    </>
  );
}