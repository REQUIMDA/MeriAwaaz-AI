"use client";

import { useRouter } from "next/navigation";
import { PlusCircle } from "lucide-react";

export default function Hero() {
  const router = useRouter();

  return (
    <section className="bg-[#f7f9fc] px-6 py-24">
      <div className="mx-auto max-w-5xl text-center">

        {/* Badge */}

        <div className="mb-8 inline-flex items-center gap-2 rounded-full bg-[#b5d0fd]/30 px-5 py-2">
          <div className="h-2.5 w-2.5 rounded-full bg-[#2d486d]" />

          <span className="text-xs font-semibold uppercase tracking-[0.2em] text-[#2d486d]">
            Official Citizen Platform
          </span>
        </div>

        {/* Heading */}

        <h1 className="mx-auto max-w-4xl text-5xl font-extrabold leading-tight text-black md:text-7xl">
          Shape the Future of
          <br />
          Your Neighborhood.
        </h1>

        {/* Subtitle */}

        <p className="mx-auto mt-8 max-w-3xl text-xl leading-9 text-[#43474b]">
          Your voice, amplified by AI, helps your representatives solve
          local issues faster and more effectively. Together, we build
          smarter cities.
        </p>

        {/* CTA */}

        <button
          onClick={() => router.push("/citizen/new-issue")}
          className="mx-auto mt-12 flex items-center gap-3 rounded-full bg-black px-8 py-4 text-lg font-semibold text-white shadow-lg transition-all duration-300 hover:scale-105 hover:shadow-2xl"
        >
          <PlusCircle size={22} />

          <span>Submit an Issue</span>
        </button>

      </div>
    </section>
  );
}