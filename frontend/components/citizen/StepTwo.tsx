"use client";

import {
  MapPin,
  LocateFixed,
} from "lucide-react";

import { useIssueStore } from "@/store/issueStore";

export default function StepTwo() {
  const {
    location,
    setLocation,
  } = useIssueStore();

  return (
    <>
      <div className="mb-8">
        <h2 className="mb-2 text-4xl font-semibold">
          Pin the location
        </h2>

        <p className="text-[#43474b]">
          Where is this issue occurring?
        </p>
      </div>

      <div className="mb-8 overflow-hidden rounded-2xl border bg-white">

        {/* Map */}

        <div className="relative h-80">

          <img
            src="/images/map.jpg"
            alt="Map"
            className="h-full w-full object-cover"
          />

          <button
            type="button"
            className="absolute bottom-4 right-4 flex h-12 w-12 items-center justify-center rounded-full bg-white shadow-lg"
          >
            <LocateFixed />
          </button>

        </div>

        {/* Location */}

        <div className="bg-[#f2f4f7] p-6">

          <div className="mb-4 flex items-start gap-4">

            <MapPin
              className="mt-1 text-[#FFB703]"
              fill="#FFB703"
            />

            <div>
              <h3 className="text-xl font-semibold">
                Issue Location
              </h3>

              <p className="text-[#43474b]">
                Enter the address or landmark where the issue exists.
              </p>
            </div>

          </div>

          <input
            type="text"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="e.g. Near 4th Block Bus Stand, Kalyan Nagar, Bangalore"
            className="w-full rounded-xl border border-gray-200 bg-white p-4 outline-none focus:border-[#FFB703]"
          />

        </div>

      </div>
    </>
  );
}