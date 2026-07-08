import {
  ArrowLeft,
  Brain,
  Send,
} from "lucide-react";

export default function StepThree() {
  return (
    <>
      <div className="mb-8">
        <h2 className="mb-2 text-4xl font-semibold">
          Review & Submit
        </h2>

        <p className="text-[#43474b]">
          Our AI has drafted a summary of your report.
        </p>
      </div>

      {/* AI Summary */}

      <div className="mb-8 rounded-2xl bg-[#0b1d2a] p-1">

        <div className="relative rounded-2xl bg-white p-6">

          <Brain
            className="absolute right-6 top-6 text-[#FFB703]"
            size={30}
          />

          <p className="mb-4 text-xs font-semibold uppercase tracking-[0.2em] text-[#FFB703]">
            AI GENERATED SUMMARY
          </p>

          <p className="text-lg italic leading-8 text-[#191c1e]">
            &quot;A significant pothole has formed on the main road of
            Kalyan Nagar near the 4th Block Bus Stand. The damage
            poses a risk to motorists and requires immediate
            repair.&quot;
          </p>

          <div className="mt-6 flex flex-wrap gap-2">

            <span className="rounded-full bg-[#eceef1] px-3 py-1 text-sm">
              #RoadSafety
            </span>

            <span className="rounded-full bg-[#eceef1] px-3 py-1 text-sm">
              #UrgentRepair
            </span>

            <span className="rounded-full bg-[#eceef1] px-3 py-1 text-sm">
              #BangaloreEast
            </span>

          </div>

        </div>

      </div>

      {/* Details */}

      <div className="mb-10 grid gap-6 md:grid-cols-2">

        <div className="rounded-xl bg-[#f2f4f7] p-5">

          <p className="mb-2 text-xs uppercase text-[#43474b]">
            Category
          </p>

          <h3 className="text-xl font-semibold">
            Roads & Infrastructure
          </h3>

        </div>

        <div className="rounded-xl bg-[#f2f4f7] p-5">

          <p className="mb-2 text-xs uppercase text-[#43474b]">
            Priority
          </p>

          <div className="flex items-center gap-2">

            <div className="h-3 w-3 rounded-full bg-[#FFB703]" />

            <h3 className="text-xl font-semibold">
              High Priority
            </h3>

          </div>

        </div>

      </div>

      {/* Buttons */}

    </>
  );
}