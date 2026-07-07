"use client";

import { useState } from "react";
import {
  Camera,
  FileText,
  Mic,
  Plus,
  Droplets,
  Bolt,
  Stethoscope,
  Construction,
  ArrowRight,
} from "lucide-react";

const categories = [
  {
    icon: Construction,
    name: "Roads",
  },
  {
    icon: Droplets,
    name: "Water",
  },
  {
    icon: Bolt,
    name: "Electricity",
  },
  {
    icon: Stethoscope,
    name: "Health",
  },
];

export default function StepOne() {
  const [selected, setSelected] = useState("");

  return (
    <>
      <div className="mb-8">
        <h2 className="mb-2 text-4xl font-semibold">
          Tell us what&apos;s happening
        </h2>

        <p className="text-[#43474b]">
          Upload details about the issue in your preferred format.
        </p>
      </div>

      {/* Upload Cards */}

      <div className="mb-8 grid gap-4 md:grid-cols-2">

        {/* Description */}

        <div className="rounded-xl border bg-white p-6 md:col-span-2">

          <div className="mb-4 flex items-center gap-3">
            <FileText />
            <h3 className="text-xl font-semibold">
              Describe the issue
            </h3>
          </div>

          <textarea
            rows={6}
            placeholder="Briefly describe what needs attention..."
            className="w-full rounded-xl bg-[#f7f9fc] p-4 outline-none"
          />

        </div>

        {/* Voice */}

        <div className="rounded-xl border bg-white p-8 text-center">

          <div className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-full bg-[#eceef1]">
            <Mic size={34} />
          </div>

          <h3 className="mb-2 text-xl font-semibold">
            Voice Message
          </h3>

          <p className="mb-6 text-sm text-[#43474b]">
            Speak in any language.
          </p>

          <button className="rounded-full bg-black px-6 py-3 text-white">
            Start Recording
          </button>

        </div>

        {/* Camera */}

        <div className="rounded-xl border bg-white p-8 text-center">

          <div className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-full bg-[#eceef1]">
            <Camera size={34} />
          </div>

          <h3 className="mb-2 text-xl font-semibold">
            Upload Photo
          </h3>

          <p className="mb-6 text-sm text-[#43474b]">
            A picture helps us understand better.
          </p>

          <button className="rounded-full border border-black px-6 py-3">
            <span className="flex items-center gap-2">
              <Plus size={16} />
              Open Camera
            </span>
          </button>

        </div>

      </div>

      {/* Categories */}

      <h3 className="mb-6 text-2xl font-semibold">
        Select Category
      </h3>

      <div className="mb-12 grid grid-cols-2 gap-4 md:grid-cols-4">

        {categories.map((cat) => {
          const Icon = cat.icon;

          return (
            <button
              key={cat.name}
              onClick={() => setSelected(cat.name)}
              className={`rounded-xl border p-6 transition ${
                selected === cat.name
                  ? "border-[#FFB703] bg-[#ffdea9]"
                  : "bg-white hover:bg-[#ffdea9]/40"
              }`}
            >
              <Icon className="mx-auto mb-3" />

              <p>{cat.name}</p>
            </button>
          );
        })}

      </div>

      <div className="flex justify-end">
  <button className="flex items-center gap-2 rounded-full bg-black px-8 py-4 text-white">
    Next: Location
    <ArrowRight size={18} />
  </button>
</div>
    </>
  );
}