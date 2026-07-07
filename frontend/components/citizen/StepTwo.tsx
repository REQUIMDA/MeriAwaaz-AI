import {
  ArrowLeft,
  ArrowRight,
  MapPin,
  LocateFixed,
} from "lucide-react";

export default function StepTwo() {
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

          <button className="absolute bottom-4 right-4 flex h-12 w-12 items-center justify-center rounded-full bg-white shadow-lg">
            <LocateFixed />
          </button>

        </div>

        {/* Location */}

        <div className="flex items-start gap-4 bg-[#f2f4f7] p-6">

          <MapPin
            className="mt-1 text-[#FFB703]"
            fill="#FFB703"
          />

          <div>
            <h3 className="text-xl font-semibold">
              Kalyan Nagar, Bangalore
            </h3>

            <p className="text-[#43474b]">
              Near 4th Block Bus Stand, Pin: 560043
            </p>
          </div>

        </div>

      </div>

      <div className="flex justify-between">

  <button className="flex items-center gap-2">
    <ArrowLeft />
    Back
  </button>

  <button className="flex items-center gap-2 rounded-full bg-black px-8 py-4 text-white">
    Next: Review
    <ArrowRight />
  </button>

</div>
    </>
  );
}