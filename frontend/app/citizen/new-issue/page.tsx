"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import Navbar from "@/components/citizen/Navbar";
import BottomNav from "@/components/citizen/BottomNav";

import IssueProgress from "@/components/citizen/IssueProgress";
import StepOne from "@/components/citizen/StepOne";
import StepTwo from "@/components/citizen/StepTwo";

import { useIssueStore } from "@/store/issueStore";

export default function NewIssuePage() {
  const router = useRouter();
  const [step, setStep] = useState<1 | 2>(1);

  const { location } = useIssueStore();

  function handleContinue() {
    // Address is compulsory regardless of whether a map marker was placed.
    if (!location.trim()) {
      alert("Please enter the issue address in the text box before continuing.");
      return;
    }
    router.push("/citizen/review");
  }

  return (
    <>
      <Navbar />

      <main className="min-h-screen bg-[#f7f9fc] px-6 py-12">
        <div className="mx-auto max-w-5xl">
          <IssueProgress step={step} />

          <div className="mt-10">
            {step === 1 && <StepOne />}
            {step === 2 && <StepTwo />}
          </div>

          <div className="mt-12 flex justify-between">
            {step === 1 ? (
              <button
                onClick={() => router.push("/citizen/dashboard")}
                className="rounded-full border border-gray-300 px-8 py-4 transition hover:bg-gray-100"
              >
                Cancel
              </button>
            ) : (
              <button
                onClick={() => setStep(1)}
                className="rounded-full border border-gray-300 px-8 py-4 transition hover:bg-gray-100"
              >
                Back
              </button>
            )}

            {step === 1 ? (
              <button
                onClick={() => setStep(2)}
                className="rounded-full bg-black px-8 py-4 font-semibold text-white transition hover:scale-105"
              >
                Next
              </button>
            ) : (
              <button
                onClick={handleContinue}
                className="rounded-full bg-black px-8 py-4 font-semibold text-white transition hover:scale-105"
              >
                Continue to Review
              </button>
            )}
          </div>
        </div>
      </main>

      <BottomNav />
    </>
  );
}
