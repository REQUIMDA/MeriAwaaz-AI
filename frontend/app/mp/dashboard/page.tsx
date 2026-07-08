"use client";

import Link from "next/link";

import DashboardHeader from "@/components/mp/DashboardHeader";
import StatCard from "@/components/mp/StatCard";

export default function DashboardPage() {
  return (
    <>
      <DashboardHeader />

      <div className="grid grid-cols-1 gap-6 md:grid-cols-12">
        {/* =========================
            Metrics Row
        ========================== */}

        <div className="md:col-span-3 col-span-12">
          <StatCard
            icon="inbox"
            iconBackground="bg-[#B5D0FD]"
            iconColor="text-[#455F87]"
            title="Total Citizen Submissions"
            value="12,482"
            badge="+12%"
            badgeClassName="rounded-full bg-green-100 px-2 py-1 text-xs font-bold text-green-600"
          />
        </div>

        <div className="md:col-span-3 col-span-12">
          <StatCard
            icon="priority_high"
            iconBackground="bg-[#FFDAD6]"
            iconColor="text-[#BA1A1A]"
            title="High Priority Clusters"
            value="42"
          >
            <span className="text-xs font-bold text-[#43474B]">
              Last 24h
            </span>
          </StatCard>
        </div>

        <div className="md:col-span-3 col-span-12">
          <StatCard
            icon="construction"
            iconBackground="bg-[#FFDEA9]"
            iconColor="text-[#AD7B00]"
            title="Infrastructure Gaps Identified"
            value="158"
          />
        </div>

        <div className="md:col-span-3 col-span-12">
          <StatCard
            icon="payments"
            iconBackground="bg-[#D5E3FF]"
            iconColor="text-[#3E5980]"
            title="Estimated Budget Needed"
            value="₹42.8Cr"
          />
        </div>

        {/* =========================
            AI Summary
        ========================== */}

        <div className="relative col-span-12 overflow-hidden rounded-[24px] bg-[#0B1D2A] p-8 text-white md:col-span-8">
          <div className="relative z-10">
            <div className="mb-6 flex items-center gap-2">
              <span className="material-symbols-outlined text-[#FFDEA9]">
                psychology
              </span>

              <h4 className="text-xs font-semibold uppercase tracking-[0.25em] text-[#FFDEA9]">
                AI Constituency Summary
              </h4>
            </div>

            <p className="max-w-2xl text-2xl font-medium leading-8">
              Current citizen sentiment in{" "}
              <span className="text-[#FFDEA9]">
                West Zone
              </span>{" "}
              has shifted towards urgent water infrastructure needs
              following the monsoon delays.

              AI analysis identifies a 38% increase in mentions of
              "clogged drainage" and "pipeline repairs" near the
              industrial corridor.

              Urgent intervention is recommended in Wards 14 &amp; 22
              before the next forecast.
            </p>
          </div>
        </div>

        {/* =========================
            Quick Navigation
        ========================== */}

        <div className="glass-card bento-item col-span-12 flex flex-col justify-between rounded-[24px] p-8 md:col-span-4">
          <h4 className="mb-6 text-xs font-semibold uppercase tracking-[0.25em] text-[#43474B]">
            Quick Navigation
          </h4>

          <div className="grid gap-3">

            <Link
  href="/heatmap"
  className="group flex items-center justify-between rounded-2xl bg-[#ECEEF1] p-4 transition-all hover:bg-black hover:text-white"
>
  <div className="flex items-center gap-3">
    <span className="material-symbols-outlined">
      map
    </span>

    <span className="text-sm font-bold">
      Heatmap Analysis
    </span>
  </div>

  <span className="material-symbols-outlined opacity-0 transition-opacity group-hover:opacity-100">
    arrow_forward
  </span>
</Link>

            <button className="group flex items-center justify-between rounded-2xl bg-[#ECEEF1] p-4 transition-all hover:bg-black hover:text-white">

              <div className="flex items-center gap-3">

                <span className="material-symbols-outlined">
                  account_tree
                </span>

                <span className="text-sm font-bold">
                  Active Projects
                </span>

              </div>

              <span className="material-symbols-outlined opacity-0 transition-opacity group-hover:opacity-100">
                arrow_forward
              </span>

            </button>

            <button
              onClick={() =>
                alert("Quarterly reporting module coming soon.")
              }
              className="group flex items-center justify-between rounded-2xl bg-[#ECEEF1] p-4 text-left transition-all hover:bg-black hover:text-white"
            >

              <div className="flex items-center gap-3">

                <span className="material-symbols-outlined">
                  summarize
                </span>

                <span className="text-sm font-bold">
                  Quarterly Reports
                </span>

              </div>

              <span className="material-symbols-outlined opacity-0 transition-opacity group-hover:opacity-100">
                arrow_forward
              </span>

            </button>

          </div>
        </div>
                {/* =========================
            Top Recommendations
        ========================== */}

        <div className="glass-card bento-item col-span-12 rounded-[24px] p-8 md:col-span-5">
          <div className="mb-6 flex items-center justify-between">
            <h4 className="text-2xl font-semibold text-black">
              Top Recommendations
            </h4>

            <button className="flex items-center gap-1 text-sm font-semibold text-[#455F87] transition-colors hover:text-black">
              View All

              <span className="material-symbols-outlined text-[18px]">
                open_in_new
              </span>
            </button>
          </div>

          <div className="space-y-4">
            {/* Recommendation 1 */}

            <div className="cursor-pointer rounded-2xl border border-[#C3C7CC]/30 p-4 transition-colors hover:border-[#455F87]">
              <div className="flex items-center gap-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-[#B5D0FD]/30 text-[#455F87]">
                  <span
                    className="material-symbols-outlined"
                    style={{ fontVariationSettings: '"FILL" 1' }}
                  >
                    bolt
                  </span>
                </div>

                <div className="flex-1">
                  <h5 className="text-sm font-bold text-black">
                    Solar Grid Expansion
                  </h5>

                  <p className="text-xs text-[#43474B]">
                    Ward 5 • Impact: 12,000 Citizens
                  </p>
                </div>

                <div className="text-right">
                  <span className="text-xs font-bold text-green-600">
                    98% Match
                  </span>
                </div>
              </div>
            </div>

            {/* Recommendation 2 */}

            <div className="cursor-pointer rounded-2xl border border-[#C3C7CC]/30 p-4 transition-colors hover:border-[#455F87]">
              <div className="flex items-center gap-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-[#FFDEA9]/30 text-[#AD7B00]">
                  <span
                    className="material-symbols-outlined"
                    style={{ fontVariationSettings: '"FILL" 1' }}
                  >
                    water_drop
                  </span>
                </div>

                <div className="flex-1">
                  <h5 className="text-sm font-bold text-black">
                    Drainage Desilting
                  </h5>

                  <p className="text-xs text-[#43474B]">
                    North Cluster • Priority: High
                  </p>
                </div>

                <div className="text-right">
                  <span className="text-xs font-bold text-green-600">
                    92% Match
                  </span>
                </div>
              </div>
            </div>

            {/* Recommendation 3 */}

            <div className="cursor-pointer rounded-2xl border border-[#C3C7CC]/30 p-4 transition-colors hover:border-[#455F87]">
              <div className="flex items-center gap-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-[#B5D0FD]/30 text-[#455F87]">
                  <span
                    className="material-symbols-outlined"
                    style={{ fontVariationSettings: '"FILL" 1' }}
                  >
                    school
                  </span>
                </div>

                <div className="flex-1">
                  <h5 className="text-sm font-bold text-black">
                    Smart Classroom Pilot
                  </h5>

                  <p className="text-xs text-[#43474B]">
                    East Zone • Impact: 4 Schools
                  </p>
                </div>

                <div className="text-right">
                  <span className="text-xs font-bold text-green-600">
                    85% Match
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* =========================
            Urgent Issue Feed
        ========================== */}

        <div className="glass-card bento-item col-span-12 flex flex-col rounded-[24px] p-8 md:col-span-7">
          <div className="mb-6 flex items-center justify-between">
            <h4 className="text-2xl font-semibold text-black">
              Urgent Issue Feed
            </h4>

            <div className="flex gap-2">
              <span className="rounded-full bg-[#ECEEF1] px-3 py-1 text-xs font-bold text-[#43474B]">
                Recent
              </span>

              <span className="rounded-full bg-black px-3 py-1 text-xs font-bold text-white">
                Priority High
              </span>
            </div>
          </div>

          <div className="max-h-[360px] flex-1 space-y-2 overflow-y-auto pr-2">
                      {/* Feed Item 1 */}

            <div className="flex items-start gap-4 rounded-2xl border-l-4 border-[#BA1A1A] bg-[#F2F4F7] p-5">
              <img
                src="https://lh3.googleusercontent.com/aida-public/AB6AXuC9FgjYJpEF6N5WfYx9fxn7fNaUAwPsrm4vfmfIQtaaJ0_pjvxk0cVxHpnFo-if-f3yAJV3pjC5a8yYe1GKjZ0Gv-hcvzedrXnCTBxgY8yFKIddmI8_6mqtuZ_UHyLIU0uikzUMIW3su_dNzSBbM6ro8dNBCQ8LG4Bt20RSGZufwFLCYZem_z0IpAPoxLd3TrutB4NmAm0X19HyxuUSxcWPorRCoWRagu2jiccGIYguEFzqe93PY6U"
                alt="Road damage"
                className="h-16 w-16 rounded-lg object-cover"
              />

              <div className="flex-1">
                <div className="flex justify-between">
                  <span className="text-xs font-extrabold uppercase text-[#BA1A1A]">
                    Critical • Ward 12
                  </span>

                  <span className="text-xs text-[#43474B]">
                    2 mins ago
                  </span>
                </div>

                <h5 className="mt-1 text-sm font-bold text-black">
                  Severe road subsidence reported near Metro St.
                </h5>

                <p className="mt-1 line-clamp-1 text-sm text-[#43474B]">
                  Multiple citizens reported large fissure affecting
                  traffic flow...
                </p>
              </div>

              <div className="flex min-w-[60px] flex-col items-center justify-center rounded-xl border border-[#C3C7CC]/30 bg-white p-2">
                <span className="text-xs text-[#43474B]">
                  Score
                </span>

                <span className="text-lg font-black text-black">
                  9.8
                </span>
              </div>
            </div>

            {/* Feed Item 2 */}

            <div className="flex items-start gap-4 rounded-2xl border-l-4 border-[#FFBA27] bg-[#F2F4F7] p-5">
              <img
                src="https://lh3.googleusercontent.com/aida-public/AB6AXuDOrfzXgWS4U4b8k9nhg0bZaO6qf9gAnUoTR84ahXsSub4ltf-dgiI9BDbGojgiFX4Ml5Te-CwsZj5n551Xz5e1BWnOJEB001m5lMu6EOAqtF-CO1jq_s8EIbsnQaLP-nyjAw-ouLMVEufMj18Bb-tKrsNhv_8vuQZES8HpG2Xl1NZ054U4esQxus-p95pz8RTxPjkzsImYlwDI6opwzK0RJIr411gHOZ4Z_3_d_ebRSEUBtUApzSg"
                alt="Medical supply shortage"
                className="h-16 w-16 rounded-lg object-cover"
              />

              <div className="flex-1">
                <div className="flex justify-between">
                  <span className="text-xs font-extrabold uppercase text-[#AD7B00]">
                    High • Ward 4
                  </span>

                  <span className="text-xs text-[#43474B]">
                    14 mins ago
                  </span>
                </div>

                <h5 className="mt-1 text-sm font-bold text-black">
                  Medical supply shortage at Civil Dispensary
                </h5>

                <p className="mt-1 line-clamp-1 text-sm text-[#43474B]">
                  Vaccine stock exhausted for 3 consecutive days...
                </p>
              </div>

              <div className="flex min-w-[60px] flex-col items-center justify-center rounded-xl border border-[#C3C7CC]/30 bg-white p-2">
                <span className="text-xs text-[#43474B]">
                  Score
                </span>

                <span className="text-lg font-black text-black">
                  8.2
                </span>
              </div>
            </div>

            {/* Feed Item 3 */}

            <div className="flex items-start gap-4 rounded-2xl border-l-4 border-[#455F87] bg-[#F2F4F7] p-5">
              <img
                src="https://lh3.googleusercontent.com/aida-public/AB6AXuAOZaQshnnVMtq9q7-3mfSs_JugjMFrh9VQJ6Soqswqt4ciX38O2SEdvHPftGkIQN3TTFVN-gAjxwosSBvkLIMz2lVs7ltGndkjL8RMNI95JZVbnnpBuPcEWrIohEFNvhtjN9JgcHhA_HOIoMCO6q2fNQ_df9RScCxiyz2Hm1J5jUNqYcEnonuCTX6xHwKFE5cPLqRToXiBovrk9iZhU7jLz8rm2FJgKkr-KiXIaXONH81klHS-TGE"
                alt="Streetlight issue"
                className="h-16 w-16 rounded-lg object-cover"
              />

              <div className="flex-1">
                <div className="flex justify-between">
                  <span className="text-xs font-extrabold uppercase text-[#455F87]">
                    Medium • Ward 21
                  </span>

                  <span className="text-xs text-[#43474B]">
                    1h ago
                  </span>
                </div>

                <h5 className="mt-1 text-sm font-bold text-black">
                  Streetlight malfunction in Community Park
                </h5>

                <p className="mt-1 line-clamp-1 text-sm text-[#43474B]">
                  Area is completely dark after 7PM, raising safety
                  concerns...
                </p>
              </div>

              <div className="flex min-w-[60px] flex-col items-center justify-center rounded-xl border border-[#C3C7CC]/30 bg-white p-2">
                <span className="text-xs text-[#43474B]">
                  Score
                </span>

                <span className="text-lg font-black text-black">
                  6.5
                </span>
              </div>
            </div>

          </div>
        </div>
              </div>

      {/* =========================
          Trend Chart
      ========================== */}

      <div className="glass-card bento-item mt-8 rounded-[24px] p-8">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h4 className="text-2xl font-semibold text-black">
              Issue Trends by Category
            </h4>

            <p className="text-sm text-[#43474B]">
              Distribution across primary governance departments
            </p>
          </div>

          <div className="flex gap-4">
            <div className="flex items-center gap-2">
              <div className="h-3 w-3 rounded-full bg-black" />
              <span className="text-xs font-bold">
                Infrastructure
              </span>
            </div>

            <div className="flex items-center gap-2">
              <div className="h-3 w-3 rounded-full bg-[#455F87]" />
              <span className="text-xs font-bold">
                Healthcare
              </span>
            </div>

            <div className="flex items-center gap-2">
              <div className="h-3 w-3 rounded-full bg-[#FFBA27]" />
              <span className="text-xs font-bold">
                Sanitation
              </span>
            </div>
          </div>
        </div>

        <div className="flex h-64 w-full items-end justify-between gap-4 px-4">

          {[
            ["Jan", 60],
            ["Feb", 75],
            ["Mar", 45],
            ["Apr", 90],
            ["May", 65],
            ["Jun", 80],
            ["Jul", 95],
          ].map(([month, value]) => (
            <div
              key={month}
              className="flex flex-1 flex-col items-center gap-2"
            >
              <div
                className="relative flex w-full flex-col justify-end overflow-hidden rounded-t-lg bg-[#E6E8EB]"
                style={{ height: "100%" }}
              >
                <div
                  className="w-full bg-black"
                  style={{
                    height: `${value}%`,
                  }}
                />
              </div>

              <span className="text-[10px] font-bold text-[#43474B]">
                {month}
              </span>
            </div>
          ))}

        </div>
      </div>
    </>
  );
}