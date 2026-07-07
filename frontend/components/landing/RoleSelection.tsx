"use client";

import { useRouter } from "next/navigation";
import {
  User,
  Landmark,
  ArrowRight,
} from "lucide-react";

export default function RoleSelection() {
  const router = useRouter();

  return (
    <section className="mx-auto mt-12 grid max-w-5xl gap-8 px-6 md:grid-cols-2">
      {/* Citizen Card */}
      <button
        onClick={() => router.push("/citizen/dashboard")}
        className="group rounded-2xl border border-[#e6edf3] bg-white/80 p-10 text-left shadow-sm backdrop-blur-xl transition-all duration-300 hover:-translate-y-2 hover:border-black hover:shadow-2xl"
      >
        <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-gray-100 transition group-hover:bg-black">
          <User
            size={30}
            className="text-black transition group-hover:text-white"
          />
        </div>

        <h2 className="mb-4 text-4xl font-bold text-[#222]">
          Continue as Citizen
        </h2>

        <p className="mb-10 text-lg leading-8 text-[#43474b]">
          Raise local issues, track complaints, explore nearby government
          projects and interact with your AI-powered constituency assistant.
        </p>

        <div className="flex items-center gap-3 font-semibold text-black">
          <span>Get Started</span>

          <ArrowRight
            size={20}
            className="transition-transform duration-300 group-hover:translate-x-2"
          />
        </div>
      </button>

      {/* MP Card */}
      <button
        onClick={() => router.push("/mp/dashboard")}
        className="group rounded-2xl border border-[#e6edf3] bg-white/80 p-10 text-left shadow-sm backdrop-blur-xl transition-all duration-300 hover:-translate-y-2 hover:border-[#ad7b00] hover:shadow-2xl"
      >
        <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-[#ffdea9]/30 transition group-hover:bg-[#ad7b00]">
          <Landmark
            size={30}
            className="text-[#ad7b00] transition group-hover:text-white"
          />
        </div>

        <h2 className="mb-4 text-4xl font-bold text-[#222]">
          Continue as Member of Parliament
        </h2>

        <p className="mb-10 text-lg leading-8 text-[#43474b]">
          Access constituency intelligence, prioritize development
          projects and review AI-generated summaries to support informed
          decision-making.
        </p>

        <div className="flex items-center gap-3 font-semibold text-[#ad7b00]">
          <span>Portal Access</span>

          <ArrowRight
            size={20}
            className="transition-transform duration-300 group-hover:translate-x-2"
          />
        </div>
      </button>
    </section>
  );
}