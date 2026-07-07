"use client";

import { useRouter } from "next/navigation";

import Navbar from "@/components/citizen/Navbar";
import BottomNav from "@/components/citizen/BottomNav";
import VoiceFAB from "@/components/citizen/VoiceFAB";

import IssueProgress from "@/components/citizen/IssueProgress";
import StepThree from "@/components/citizen/StepThree";

export default function ReviewPage() {
  const router = useRouter();

  return (
    <>
      <Navbar />

      <main className="min-h-screen bg-[#f7f9fc] px-6 py-12">
        <div className="mx-auto max-w-5xl">

          <IssueProgress step={3} />

          <div className="mt-10">
            <StepThree />
          </div>

          <div className="mt-12 flex justify-between">

            <button
              onClick={() => router.push("/citizen/new-issue")}
              className="rounded-full border border-gray-300 px-8 py-4 transition hover:bg-gray-100"
            >
              Back
            </button>

            <button
              onClick={() => router.push("/citizen/success")}
              className="rounded-full bg-[#FFB703] px-8 py-4 font-semibold text-black transition hover:scale-105"
            >
              Submit Issue
            </button>

          </div>

        </div>
      </main>

      <VoiceFAB />
      <BottomNav />
    </>
  );
}