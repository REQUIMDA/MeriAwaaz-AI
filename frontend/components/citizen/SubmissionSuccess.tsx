"use client";

import { Check } from "lucide-react";
import { useRouter } from "next/navigation";

export default function SubmissionSuccess() {
  const router = useRouter();

  return (
    <main className="mx-auto flex min-h-[70vh] max-w-xl flex-col items-center justify-center px-6 text-center">

      <div className="mb-8 flex h-24 w-24 items-center justify-center rounded-full bg-[#FFB703]">
        <Check size={52} className="text-white" />
      </div>

      <h1 className="mb-4 text-5xl font-bold">
        Thank You
      </h1>

      <p className="mb-8 text-gray-600">
        Your issue has been successfully reported.
        Our team will review it shortly.
      </p>

      <div className="mb-10 rounded-xl bg-[#f2f4f7] px-8 py-5">
        <p className="text-xs uppercase tracking-widest text-gray-500">
          Submission ID
        </p>

        <h2 className="mt-2 text-xl font-semibold">
          #MA-2026-001245
        </h2>
      </div>

      <button
        onClick={() => router.push("/citizen/dashboard")}
        className="rounded-full bg-black px-10 py-4 text-white"
      >
        Return to Home
      </button>

    </main>
  );
}