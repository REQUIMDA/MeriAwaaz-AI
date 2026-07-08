"use client";

import {
  Camera,
  FileText,
  Mic,
  Plus,
  Droplets,
  Bolt,
  Stethoscope,
  Construction,
} from "lucide-react";

import { useIssueStore } from "@/store/issueStore";

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
  const {
    category,
    description,
    photo,
    audio,
    setCategory,
    setDescription,
    setPhoto,
    setAudio,
  } = useIssueStore();

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

      {/* Description */}

      <div className="mb-8 grid gap-4 md:grid-cols-2">

        <div className="rounded-xl border bg-white p-6 md:col-span-2">

          <div className="mb-4 flex items-center gap-3">
            <FileText />
            <h3 className="text-xl font-semibold">
              Describe the issue
            </h3>
          </div>

          <textarea
            rows={6}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
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

          <label className="cursor-pointer rounded-full bg-black px-6 py-3 text-white">
            Upload Audio

            <input
              type="file"
              accept="audio/*"
              className="hidden"
              onChange={(e) =>
                setAudio(e.target.files?.[0] ?? null)
              }
            />
          </label>

          {audio && (
            <p className="mt-4 text-sm text-green-600">
              ✓ {audio.name}
            </p>
          )}

        </div>

        {/* Photo */}

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

          <label className="cursor-pointer rounded-full border border-black px-6 py-3">
            <span className="flex items-center gap-2">
              <Plus size={16} />
              Choose Photo
            </span>

            <input
              type="file"
              accept="image/*"
              className="hidden"
              onChange={(e) =>
                setPhoto(e.target.files?.[0] ?? null)
              }
            />
          </label>

          {photo && (
            <p className="mt-4 text-sm text-green-600">
              ✓ {photo.name}
            </p>
          )}

        </div>

      </div>

      {/* Categories */}

      <h3 className="mb-6 text-2xl font-semibold">
        Select Category
      </h3>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">

        {categories.map((cat) => {
          const Icon = cat.icon;

          return (
            <button
              key={cat.name}
              type="button"
              onClick={() => setCategory(cat.name)}
              className={`rounded-xl border p-6 transition ${
                category === cat.name
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
    </>
  );
}