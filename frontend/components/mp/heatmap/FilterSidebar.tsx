"use client";

import { HeatmapFilterState, IssueCategory, Severity } from "./types";

interface FilterSidebarProps {
  filters: HeatmapFilterState;
  onFiltersChange: (filters: HeatmapFilterState) => void;
}

const categories: IssueCategory[] = [
  "Water Supply",
  "Road Quality",
  "Public Lighting",
  "Waste Management",
];

const categoryColors: Record<IssueCategory, string> = {
  "Water Supply": "bg-blue-500",
  "Road Quality": "bg-orange-500",
  "Public Lighting": "bg-green-500",
  "Waste Management": "bg-purple-500",
};

const wards = [
  "All Wards",
  "Ward 14",
  "Ward 18",
  "Ward 9",
  "Ward 6",
];

export default function FilterSidebar({
  filters,
  onFiltersChange,
}: FilterSidebarProps) {
  const toggleCategory = (category: IssueCategory) => {
    const exists = filters.categories.includes(category);

    const updated = exists
      ? filters.categories.filter((c) => c !== category)
      : [...filters.categories, category];

    onFiltersChange({
      ...filters,
      categories: updated,
    });
  };

  return (
    <aside
      className="
        absolute
        left-6
        top-6
        bottom-6
        z-30
        flex
        w-80
        flex-col
        overflow-hidden
        rounded-3xl
        border
        border-white/40
        bg-white/70
        shadow-2xl
        backdrop-blur-2xl
      "
    >
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-200/70 px-6 py-5">
        <div>
          <h2 className="text-lg font-semibold text-slate-900">
            Map Filters
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            Refine hotspot analysis
          </p>
        </div>

        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-5 w-5 text-slate-500"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M3 4h18M7 12h10M10 20h4"
          />
        </svg>
      </div>

      {/* Scrollable */}
      <div className="flex-1 space-y-8 overflow-y-auto px-6 py-6">
        {/* Categories */}
        <section>
          <h3 className="mb-4 text-xs font-bold uppercase tracking-widest text-slate-500">
            Issue Categories
          </h3>

          <div className="space-y-4">
            {categories.map((category) => (
              <label
                key={category}
                className="flex cursor-pointer items-center justify-between"
              >
                <div className="flex items-center gap-3">
                  <span
                    className={`h-2.5 w-2.5 rounded-full ${
                      categoryColors[category]
                    }`}
                  />

                  <span className="text-sm font-medium text-slate-700">
                    {category}
                  </span>
                </div>

                <input
                  type="checkbox"
                  checked={filters.categories.includes(category)}
                  onChange={() => toggleCategory(category)}
                  className="
                    h-4
                    w-4
                    rounded
                    border-slate-300
                    text-slate-900
                    focus:ring-slate-900
                  "
                />
              </label>
            ))}
          </div>
        </section>

        {/* Ward */}
        <section>
          <h3 className="mb-4 text-xs font-bold uppercase tracking-widest text-slate-500">
            Ward
          </h3>

          <select
            value={filters.ward}
            onChange={(e) =>
              onFiltersChange({
                ...filters,
                ward: e.target.value,
              })
            }
            className="
              w-full
              rounded-xl
              border
              border-slate-200
              bg-white
              px-4
              py-3
              text-sm
              outline-none
              transition
              focus:border-slate-900
            "
          >
            {wards.map((ward) => (
              <option key={ward}>{ward}</option>
            ))}
          </select>
        </section>

        {/* Time Range */}
        <section>
          <h3 className="mb-4 text-xs font-bold uppercase tracking-widest text-slate-500">
            Time Range
          </h3>

          <div className="grid grid-cols-2 gap-3">
            <button
              onClick={() =>
                onFiltersChange({
                  ...filters,
                  timeRange: "30days",
                })
              }
              className={`rounded-xl py-3 text-sm font-medium transition ${
                filters.timeRange === "30days"
                  ? "bg-slate-900 text-white"
                  : "bg-slate-100 hover:bg-slate-200"
              }`}
            >
              Last 30 Days
            </button>

            <button
              onClick={() =>
                onFiltersChange({
                  ...filters,
                  timeRange: "quarter",
                })
              }
              className={`rounded-xl py-3 text-sm font-medium transition ${
                filters.timeRange === "quarter"
                  ? "bg-slate-900 text-white"
                  : "bg-slate-100 hover:bg-slate-200"
              }`}
            >
              Last Quarter
            </button>
          </div>
        </section>

        {/* Severity */}
        <section>
          <h3 className="mb-4 text-xs font-bold uppercase tracking-widest text-slate-500">
            Minimum Severity
          </h3>

          <select
            value={filters.severity}
            onChange={(e) =>
              onFiltersChange({
                ...filters,
                severity: e.target.value as Severity | "all",
              })
            }
            className="
              w-full
              rounded-xl
              border
              border-slate-200
              bg-white
              px-4
              py-3
              text-sm
              outline-none
              transition
              focus:border-slate-900
            "
          >
            <option value="all">All</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </section>
      </div>

      {/* Footer */}
      <div className="border-t border-slate-200/70 p-6">
        <button
          className="
            w-full
            rounded-xl
            bg-slate-900
            py-3
            text-sm
            font-semibold
            text-white
            transition
            hover:bg-slate-800
          "
        >
          Apply Filters
        </button>
      </div>
    </aside>
  );
}