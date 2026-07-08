"use client";

interface AIInsightsProps {
  title: string;
  description: string;
}

export default function AIInsights({
  title,
  description,
}: AIInsightsProps) {
  return (
    <div className="relative overflow-hidden rounded-[24px] bg-[#0B1D2A] p-8 text-white">

      {/* Background Decoration */}

      <div className="absolute -right-16 -top-16 h-56 w-56 rounded-full bg-[#455F87]/20 blur-3xl" />

      <div className="absolute -bottom-24 left-0 h-72 w-72 rounded-full bg-[#FFBA27]/10 blur-3xl" />

      <div className="relative z-10">

        {/* Header */}

        <div className="mb-6 flex items-center gap-3">

          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-[#FFDEA9]/20">

            <span
              className="material-symbols-outlined text-[#FFBA27]"
              style={{
                fontVariationSettings: '"FILL" 1',
              }}
            >
              psychology
            </span>

          </div>

          <div>

            <p className="text-xs font-semibold uppercase tracking-[0.25em] text-[#FFDEA9]">
              AI INSIGHTS
            </p>

            <h3 className="mt-1 text-2xl font-bold">
              Constituency Intelligence
            </h3>

          </div>

        </div>

        {/* Insight */}

        <div className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm">

          <h4 className="mb-3 text-xl font-semibold">
            {title}
          </h4>

          <p className="leading-8 text-[#D5E3FF]">
            {description}
          </p>

        </div>

        {/* AI Recommendation */}

        <div className="mt-6 flex flex-col gap-4 rounded-2xl border border-[#FFBA27]/20 bg-[#12293B] p-6 md:flex-row md:items-center md:justify-between">

          <div>

            <div className="mb-2 flex items-center gap-2">

              <span className="material-symbols-outlined text-[#FFBA27]">
                lightbulb
              </span>

              <span className="text-sm font-bold uppercase tracking-wider text-[#FFDEA9]">
                Recommended Action
              </span>

            </div>

            <p className="text-[#D5E3FF]">
              Prioritize infrastructure inspection in affected wards
              and assign engineering teams for field verification.
            </p>

          </div>

          <button className="flex items-center justify-center gap-2 rounded-2xl bg-[#FFBA27] px-6 py-3 font-bold text-black transition-all hover:scale-[1.03] hover:bg-[#FFD46B] active:scale-95">

            View Analysis

            <span className="material-symbols-outlined">
              arrow_forward
            </span>

          </button>

        </div>

      </div>

    </div>
  );
}