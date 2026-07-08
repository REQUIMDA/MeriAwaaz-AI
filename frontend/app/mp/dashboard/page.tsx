"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import DashboardHeader from "@/components/mp/DashboardHeader";
import StatCard from "@/components/mp/StatCard";
import { API_BASE, getDashboard } from "@/services/api";
import type { DashboardData, ProjectCard } from "@/types/api";

const CATEGORY_ICON: Record<string, string> = {
  Healthcare: "medical_services",
  Roads: "construction",
  Water: "water_drop",
  Sanitation: "cleaning_services",
  Electricity: "bolt",
  Education: "school",
  Vocational: "engineering",
  Other: "category",
};

function scoreBadgeColor(score: number) {
  if (score >= 55) return "border-[#BA1A1A]";
  if (score >= 40) return "border-[#FFBA27]";
  return "border-[#455F87]";
}

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let alive = true;
    getDashboard()
      .then((d) => alive && setData(d))
      .catch((e) => alive && setError(String(e.message || e)))
      .finally(() => alive && setLoading(false));
    return () => {
      alive = false;
    };
  }, []);

  const projects: ProjectCard[] = data?.projects ?? [];
  const totalSubmissions = data?.total_submissions ?? 0;

  const highPriority = projects.filter((p) => p.priority_score >= 40).length;
  const topScore = projects.length
    ? Math.round(Math.max(...projects.map((p) => p.priority_score)))
    : 0;

  const top = projects[0];

  return (
    <>
      <DashboardHeader />

      {error && (
        <div className="mb-6 rounded-2xl border border-[#FFDAD6] bg-[#FFF3F2] p-4 text-sm text-[#BA1A1A]">
          Could not reach the backend. {error}
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 md:grid-cols-12">
        {/* Metrics */}
        <div className="md:col-span-3 col-span-12">
          <StatCard
            icon="inbox"
            iconBackground="bg-[#B5D0FD]"
            iconColor="text-[#455F87]"
            title="Total Citizen Submissions"
            value={loading ? "…" : totalSubmissions.toLocaleString("en-IN")}
          >
            <span className="text-xs font-bold text-[#43474B]">Live</span>
          </StatCard>
        </div>

        <div className="md:col-span-3 col-span-12">
          <StatCard
            icon="priority_high"
            iconBackground="bg-[#FFDAD6]"
            iconColor="text-[#BA1A1A]"
            title="High Priority Clusters"
            value={loading ? "…" : String(highPriority)}
          >
            <span className="text-xs font-bold text-[#43474B]">Score ≥ 40</span>
          </StatCard>
        </div>

        <div className="md:col-span-3 col-span-12">
          <StatCard
            icon="account_tree"
            iconBackground="bg-[#FFDEA9]"
            iconColor="text-[#AD7B00]"
            title="Ranked Projects"
            value={loading ? "…" : String(projects.length)}
          />
        </div>

        <div className="md:col-span-3 col-span-12">
          <StatCard
            icon="trending_up"
            iconBackground="bg-[#D5E3FF]"
            iconColor="text-[#3E5980]"
            title="Top Priority Score"
            value={loading ? "…" : `${topScore}/100`}
          />
        </div>

        {/* AI Summary */}
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
              {top ? (
                <>
                  The highest-priority need right now is{" "}
                  <span className="text-[#FFDEA9]">{top.title}</span> (
                  {top.category}), scoring{" "}
                  <span className="text-[#FFDEA9]">
                    {Math.round(top.priority_score)}/100
                  </span>
                  . Across {projects.length} ranked projects and{" "}
                  {totalSubmissions.toLocaleString("en-IN")} citizen submissions,{" "}
                  {highPriority} cluster{highPriority === 1 ? "" : "s"} exceed the
                  high-priority threshold and warrant intervention.
                </>
              ) : loading ? (
                "Loading constituency intelligence…"
              ) : (
                "No ranked projects yet. Submit citizen issues to populate the dashboard."
              )}
            </p>
          </div>
        </div>

        {/* Quick Navigation */}
        <div className="glass-card bento-item col-span-12 flex flex-col justify-between rounded-[24px] p-8 md:col-span-4">
          <h4 className="mb-6 text-xs font-semibold uppercase tracking-[0.25em] text-[#43474B]">
            Quick Navigation
          </h4>

          <div className="grid gap-3">
            <Link
              href="/mp/heatmap"
              className="group flex items-center justify-between rounded-2xl bg-[#ECEEF1] p-4 transition-all hover:bg-black hover:text-white"
            >
              <div className="flex items-center gap-3">
                <span className="material-symbols-outlined">map</span>
                <span className="text-sm font-bold">Heatmap Analysis</span>
              </div>
              <span className="material-symbols-outlined opacity-0 transition-opacity group-hover:opacity-100">
                arrow_forward
              </span>
            </Link>

            <Link
              href="/mp/citizen-issues"
              className="group flex items-center justify-between rounded-2xl bg-[#ECEEF1] p-4 transition-all hover:bg-black hover:text-white"
            >
              <div className="flex items-center gap-3">
                <span className="material-symbols-outlined">forum</span>
                <span className="text-sm font-bold">Citizen Issues</span>
              </div>
              <span className="material-symbols-outlined opacity-0 transition-opacity group-hover:opacity-100">
                arrow_forward
              </span>
            </Link>

            <a
              href={`${API_BASE}/docs`}
              target="_blank"
              rel="noopener noreferrer"
              className="group flex items-center justify-between rounded-2xl bg-[#ECEEF1] p-4 transition-all hover:bg-black hover:text-white"
            >
              <div className="flex items-center gap-3">
                <span className="material-symbols-outlined">api</span>
                <span className="text-sm font-bold">API Explorer</span>
              </div>
              <span className="material-symbols-outlined opacity-0 transition-opacity group-hover:opacity-100">
                arrow_forward
              </span>
            </a>
          </div>
        </div>

        {/* Top Recommendations */}
        <div className="glass-card bento-item col-span-12 rounded-[24px] p-8 md:col-span-5">
          <div className="mb-6 flex items-center justify-between">
            <h4 className="text-2xl font-semibold text-black">
              Top Recommendations
            </h4>
            <Link
              href="/mp/heatmap"
              className="flex items-center gap-1 text-sm font-semibold text-[#455F87] transition-colors hover:text-black"
            >
              View on map
              <span className="material-symbols-outlined text-[18px]">
                open_in_new
              </span>
            </Link>
          </div>

          <div className="space-y-4">
            {(loading ? [] : projects.slice(0, 3)).map((p) => (
              <div
                key={p.id}
                className="cursor-pointer rounded-2xl border border-[#C3C7CC]/30 p-4 transition-colors hover:border-[#455F87]"
              >
                <div className="flex items-center gap-4">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-[#B5D0FD]/30 text-[#455F87]">
                    <span className="material-symbols-outlined">
                      {CATEGORY_ICON[p.category] || "category"}
                    </span>
                  </div>
                  <div className="flex-1">
                    <h5 className="text-sm font-bold text-black">{p.title}</h5>
                    <p className="text-xs text-[#43474B]">
                      {p.category}
                      {p.is_existing_plan_project ? " • Plan project" : " • Citizen-raised"}
                    </p>
                  </div>
                  <div className="text-right">
                    <span className="text-xs font-bold text-green-600">
                      {Math.round(p.priority_score)}/100
                    </span>
                  </div>
                </div>
              </div>
            ))}
            {!loading && projects.length === 0 && (
              <p className="text-sm text-[#43474B]">No recommendations yet.</p>
            )}
          </div>
        </div>

        {/* Urgent Issue Feed */}
        <div className="glass-card bento-item col-span-12 flex flex-col rounded-[24px] p-8 md:col-span-7">
          <div className="mb-6 flex items-center justify-between">
            <h4 className="text-2xl font-semibold text-black">
              Priority Project Feed
            </h4>
            <span className="rounded-full bg-black px-3 py-1 text-xs font-bold text-white">
              Ranked by AI
            </span>
          </div>

          <div className="max-h-[360px] flex-1 space-y-2 overflow-y-auto pr-2">
            {(loading ? [] : projects.slice(0, 6)).map((p) => (
              <div
                key={p.id}
                className={`flex items-start gap-4 rounded-2xl border-l-4 ${scoreBadgeColor(
                  p.priority_score
                )} bg-[#F2F4F7] p-5`}
              >
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-white text-[#455F87]">
                  <span className="material-symbols-outlined">
                    {CATEGORY_ICON[p.category] || "category"}
                  </span>
                </div>
                <div className="flex-1">
                  <span className="text-xs font-extrabold uppercase text-[#455F87]">
                    {p.category}
                  </span>
                  <h5 className="mt-1 text-sm font-bold text-black">{p.title}</h5>
                  <p className="mt-1 text-xs text-[#43474B]">
                    Demand {Math.round(p.breakdown.citizen_demand)}/40 · Severity{" "}
                    {Math.round(p.breakdown.severity)}/30 · Population{" "}
                    {Math.round(p.breakdown.population_impact)}/20
                  </p>
                </div>
                <div className="flex min-w-[60px] flex-col items-center justify-center rounded-xl border border-[#C3C7CC]/30 bg-white p-2">
                  <span className="text-xs text-[#43474B]">Score</span>
                  <span className="text-lg font-black text-black">
                    {Math.round(p.priority_score)}
                  </span>
                </div>
              </div>
            ))}
            {!loading && projects.length === 0 && (
              <p className="text-sm text-[#43474B]">
                No projects to show yet.
              </p>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
