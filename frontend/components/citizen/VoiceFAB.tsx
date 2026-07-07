"use client";

import { useRouter } from "next/navigation";
import { Mic } from "lucide-react";

export default function VoiceFAB() {
  const router = useRouter();

  return (
    <button
      onClick={() => router.push("/citizen/new-issue")}
      className="group fixed bottom-24 right-6 z-50 flex h-16 w-16 items-center justify-center overflow-hidden rounded-full bg-[#FF9933] text-white shadow-xl transition-all duration-300 hover:w-52 md:bottom-10 md:right-10"
    >
      <div className="flex items-center whitespace-nowrap">
        <Mic
          size={26}
          className="mx-5 shrink-0"
        />

        <span className="pr-6 text-sm font-semibold opacity-0 transition-opacity duration-200 group-hover:opacity-100">
          Report Issue
        </span>
      </div>
    </button>
  );
}