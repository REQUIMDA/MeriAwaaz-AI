"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import Navbar from "@/components/citizen/Navbar";
import BottomNav from "@/components/citizen/BottomNav";

import IssueProgress from "@/components/citizen/IssueProgress";
import StepThree from "@/components/citizen/StepThree";

import { useIssueStore } from "@/store/issueStore";
import { submitIssue } from "@/services/api";

export default function ReviewPage() {
  const router = useRouter();

  const [loading, setLoading] = useState(false);

  const {
    category,
    description,
    location,
    locationLat,
    locationLng,
    photo,
    audio,
    setSubmissionId,
    setStatus,
    setResponse,
  } = useIssueStore();

  async function handleSubmit() {
    try {
      setLoading(true);

      // Real submission → runs the backend AI pipeline.
      const res = await submitIssue({
        text: description,
        category,
        location,
        lat: locationLat,
        lng: locationLng,
        photo,
        audio,
      });

      setSubmissionId(res.submission_id);
      setStatus(
        res.status === "processed"
          ? "Processed by AI"
          : res.status === "degraded"
          ? "Received (AI degraded)"
          : "Received"
      );
      setResponse(res);

      router.push("/citizen/success");
    } catch (err) {
      console.error(err);
      alert(
        "Unable to submit issue. Please make sure the backend is running, then try again."
      );
    } finally {
      setLoading(false);
    }
  }

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
              disabled={loading}
            >
              Back
            </button>

            <button
              onClick={handleSubmit}
              disabled={loading}
              className="rounded-full bg-[#FFB703] px-8 py-4 font-semibold text-black transition hover:scale-105 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading ? "Submitting..." : "Submit Issue"}
            </button>
          </div>
        </div>
      </main>

      <BottomNav />
    </>
  );
}