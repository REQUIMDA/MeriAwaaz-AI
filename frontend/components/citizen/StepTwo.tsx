"use client";

import { MapPin } from "lucide-react";

import { useIssueStore } from "@/store/issueStore";
import LocationPicker from "@/components/common/LocationPicker";

export default function StepTwo() {
  const {
    location,
    locationLat,
    locationLng,
    setLocation,
    setLocationCoords,
  } = useIssueStore();

  return (
    <>
      <div className="mb-8">
        <h2 className="mb-2 text-4xl font-semibold">
          Pin the location
        </h2>

        <p className="text-[#43474b]">
          Zoom into the map and tap where the issue is. The address fills in
          automatically — you can then edit it. The address is required.
        </p>
      </div>

      <div className="mb-8 overflow-hidden rounded-2xl border bg-white">
        {/* Interactive map — click to drop / move the pin */}
        <LocationPicker
          height="20rem"
          initialLat={locationLat}
          initialLng={locationLng}
          onChange={(lat, lng, address) => {
            setLocationCoords(lat, lng);
            setLocation(address);
          }}
          onRemove={() => setLocationCoords(null, null)}
        />

        {/* Address (compulsory) */}
        <div className="bg-[#f2f4f7] p-6">
          <div className="mb-4 flex items-start gap-4">
            <MapPin className="mt-1 text-[#FFB703]" fill="#FFB703" />

            <div>
              <h3 className="text-xl font-semibold">
                Issue Location <span className="text-[#BA1A1A]">*</span>
              </h3>

              <p className="text-[#43474b]">
                Enter the address or landmark where the issue exists.
                {locationLat != null && (
                  <span className="ml-1 font-medium text-green-600">
                    Pin placed ✓
                  </span>
                )}
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
