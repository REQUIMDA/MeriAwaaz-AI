"use client";

import { Brain, MapPin, Paperclip } from "lucide-react";

import { useIssueStore } from "@/store/issueStore";

export default function StepThree() {
  const { category, description, location, photo, audio } = useIssueStore();

  const attachments = [
    photo ? `Photo: ${photo.name}` : null,
    audio ? `Audio: ${audio.name}` : null,
  ].filter(Boolean) as string[];

  return (
    <>
      <div className="mb-8">
        <h2 className="mb-2 text-4xl font-semibold">
          Review &amp; Submit
        </h2>

        <p className="text-[#43474b]">
          Confirm your report below. Our AI will analyse it after you submit.
        </p>
      </div>

      {/* Report preview */}

      <div className="mb-8 rounded-2xl bg-[#0b1d2a] p-1">
        <div className="relative rounded-2xl bg-white p-6">
          <Brain
            className="absolute right-6 top-6 text-[#FFB703]"
            size={30}
          />

          <p className="mb-4 text-xs font-semibold uppercase tracking-[0.2em] text-[#FFB703]">
            YOUR REPORT
          </p>

          <p className="text-lg italic leading-8 text-[#191c1e]">
            {description?.trim()
              ? `“${description.trim()}”`
              : "No description typed. If you attached a photo or voice note, our AI will read it after you submit."}
          </p>

          {location?.trim() ? (
            <div className="mt-4 flex items-center gap-2 text-sm text-[#43474b]">
              <MapPin size={16} className="text-[#FFB703]" />
              {location.trim()}
            </div>
          ) : null}

          {attachments.length > 0 && (
            <div className="mt-4 flex flex-wrap gap-2">
              {attachments.map((a) => (
                <span
                  key={a}
                  className="flex items-center gap-1 rounded-full bg-[#eceef1] px-3 py-1 text-sm"
                >
                  <Paperclip size={14} />
                  {a}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Details */}

      <div className="mb-10 grid gap-6 md:grid-cols-2">
        <div className="rounded-xl bg-[#f2f4f7] p-5">
          <p className="mb-2 text-xs uppercase text-[#43474b]">
            Category
          </p>

          <h3 className="text-xl font-semibold">
            {category?.trim() || "Auto-detected by AI"}
          </h3>
        </div>

        <div className="rounded-xl bg-[#f2f4f7] p-5">
          <p className="mb-2 text-xs uppercase text-[#43474b]">
            Location
          </p>

          <h3 className="text-xl font-semibold">
            {location?.trim() || "Not specified"}
          </h3>
        </div>
      </div>
    </>
  );
}
