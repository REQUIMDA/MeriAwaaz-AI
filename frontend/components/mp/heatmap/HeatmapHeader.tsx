"use client";

interface HeatmapHeaderProps {
  title?: string;
  subtitle?: string;
}

export default function HeatmapHeader({
  title = "Heatmap Analysis",
  subtitle = "AI-powered constituency hotspot analysis",
}: HeatmapHeaderProps) {
  return (
    <header className="sticky top-0 z-40 border-b border-slate-200/70 bg-white/80 backdrop-blur-xl">
      <div className="flex h-20 items-center justify-between px-8">
        {/* Left */}
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">
            {title}
          </h1>

          <p className="mt-1 text-sm text-slate-500">
            {subtitle}
          </p>
        </div>

        {/* Right */}
        <div className="flex items-center gap-3">
          {/* Notifications */}
          <button
            className="
              flex
              h-11
              w-11
              items-center
              justify-center
              rounded-xl
              border
              border-slate-200
              bg-white
              shadow-sm
              transition-all
              hover:-translate-y-0.5
              hover:bg-slate-50
            "
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5 text-slate-700"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M15 17h5l-1.4-1.4A2 2 0 0118 14.17V11a6 6 0 10-12 0v3.17a2 2 0 01-.6 1.43L4 17h5m6 0a3 3 0 11-6 0h6z"
              />
            </svg>
          </button>

          {/* Help */}
          <button
            className="
              flex
              h-11
              w-11
              items-center
              justify-center
              rounded-xl
              border
              border-slate-200
              bg-white
              shadow-sm
              transition-all
              hover:-translate-y-0.5
              hover:bg-slate-50
            "
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5 text-slate-700"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M8.25 9a3.75 3.75 0 117.5 0c0 1.83-1.24 2.79-2.4 3.54-.94.61-1.35 1.02-1.35 1.96m.01 3h.01"
              />
            </svg>
          </button>

          {/* Profile */}
          <button
            className="
              flex
              items-center
              gap-3
              rounded-2xl
              border
              border-slate-200
              bg-white
              px-3
              py-2
              shadow-sm
              transition-all
              hover:-translate-y-0.5
            "
          >
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-slate-900 font-semibold text-white">
              MP
            </div>

            <div className="hidden text-left lg:block">
              <p className="text-sm font-semibold text-slate-900">
                Member of Parliament
              </p>

              <p className="text-xs text-slate-500">
                Constituency Dashboard
              </p>
            </div>
          </button>
        </div>
      </div>
    </header>
  );
}