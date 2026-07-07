"use client";

import { Hotspot } from "./types";

interface DrilldownPanelProps {
  hotspot: Hotspot | null;
  onClose: () => void;
}

const severityBadge = {
  high: "bg-red-100 text-red-700",
  medium: "bg-amber-100 text-amber-700",
  low: "bg-emerald-100 text-emerald-700",
};

const severityBar = {
  high: "bg-red-500",
  medium: "bg-amber-500",
  low: "bg-emerald-500",
};

const issueIcons: Record<string, string> = {
  "Water Contamination": "💧",
  "Power Fluctuations": "⚡",
  "Road Damage": "🛣️",
  "Traffic Congestion": "🚗",
  "Overflowing Bins": "🗑️",
  "Illegal Dumping": "♻️",
  "Street Light Failure": "💡",
  "Unsafe Crossings": "🚸",
};

export default function DrilldownPanel({
  hotspot,
  onClose,
}: DrilldownPanelProps) {
  return (
    <aside
      className={`
        absolute
        right-6
        top-6
        bottom-6
        z-40
        w-[380px]
        overflow-hidden
        rounded-3xl
        border
        border-white/40
        bg-white/75
        shadow-2xl
        backdrop-blur-2xl
        transition-all
        duration-500
        ${
          hotspot
            ? "translate-x-0 opacity-100"
            : "translate-x-[120%] opacity-0"
        }
      `}
    >
      {hotspot && (
        <>
          {/* Header */}
          <div className="flex items-start justify-between border-b border-slate-200 px-6 py-5">
            <div>
              <h2 className="text-xl font-bold text-slate-900">
                {hotspot.title}
              </h2>

              <div className="mt-2 flex items-center gap-2">
                <span className="text-sm text-slate-500">
                  {hotspot.ward}
                </span>

                <span
                  className={`rounded-full px-3 py-1 text-xs font-semibold ${
                    severityBadge[hotspot.severity]
                  }`}
                >
                  {hotspot.severity.toUpperCase()}
                </span>
              </div>
            </div>

            <button
              onClick={onClose}
              className="rounded-full p-2 transition hover:bg-slate-100"
            >
              ✕
            </button>
          </div>

          {/* Content */}
          <div className="h-[calc(100%-92px)] overflow-y-auto px-6 py-6">
            {/* Statistics */}
            <div className="grid grid-cols-2 gap-4">
              <StatCard
                title="Complaints"
                value={hotspot.complaints.toString()}
              />

              <StatCard
                title="Avg Resolution"
                value={`${hotspot.averageResolutionDays} days`}
              />

              <StatCard
                title="Priority Score"
                value={hotspot.priorityScore.toString()}
              />

              <StatCard
                title="Category"
                value={hotspot.dominantCategory}
              />
            </div>

            {/* Issue Clusters */}
            <div className="mt-8">
              <h3 className="mb-5 text-sm font-semibold uppercase tracking-wider text-slate-500">
                Top Issue Clusters
              </h3>

              <div className="space-y-5">
                {hotspot.issues.map((issue) => (
                  <div key={issue.id}>
                    <div className="mb-2 flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-slate-100 text-lg">
                          {issueIcons[issue.title] ?? "📍"}
                        </div>

                        <span className="font-medium text-slate-800">
                          {issue.title}
                        </span>
                      </div>

                      <span
                        className={`rounded-full px-2 py-1 text-xs font-semibold ${
                          severityBadge[issue.severity]
                        }`}
                      >
                        {issue.severity}
                      </span>
                    </div>

                    <div className="h-2 overflow-hidden rounded-full bg-slate-200">
                      <div
                        className={`h-full rounded-full ${
                          severityBar[issue.severity]
                        }`}
                        style={{
                          width: `${issue.percentage}%`,
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* AI Recommendation */}
            <div className="mt-8 overflow-hidden rounded-3xl bg-slate-900 p-6 text-white">
              <div className="mb-4 flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-white/10">
                  🧠
                </div>

                <div>
                  <p className="text-xs uppercase tracking-widest text-slate-300">
                    AI Recommendation
                  </p>

                  <h4 className="font-semibold">
                    Suggested Action
                  </h4>
                </div>
              </div>

              <p className="text-sm leading-7 text-slate-300">
                {hotspot.recommendation}
              </p>

              <button
                className="
                  mt-6
                  w-full
                  rounded-xl
                  bg-white
                  py-3
                  font-semibold
                  text-slate-900
                  transition
                  hover:bg-slate-100
                "
              >
                Initiate Feasibility Study
              </button>
            </div>
          </div>
        </>
      )}
    </aside>
  );
}

interface StatCardProps {
  title: string;
  value: string;
}

function StatCard({
  title,
  value,
}: StatCardProps) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4">
      <p className="text-xs uppercase tracking-wider text-slate-500">
        {title}
      </p>

      <p className="mt-2 text-xl font-bold text-slate-900">
        {value}
      </p>
    </div>
  );
}