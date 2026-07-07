"use client";

import StatCard from "@/components/mp/StatCard";

import type { IssueStats } from "./types";

interface CitizenIssuesHeaderProps {
  stats: IssueStats;
}

export default function CitizenIssuesHeader({
  stats,
}: CitizenIssuesHeaderProps) {
  return (
    <>
      {/* =========================
          Header
      ========================== */}

      <div className="mb-8">
        <h1 className="text-[44px] font-extrabold tracking-[-0.03em] text-black">
          Citizen Issues
        </h1>

        <p className="mt-2 text-base text-[#43474B]">
          View, prioritize and manage constituency issues
        </p>
      </div>

      {/* =========================
          Stats
      ========================== */}

      <div className="mb-8 grid grid-cols-1 gap-6 md:grid-cols-12">
        <div className="col-span-12 md:col-span-3">
          <StatCard
            icon="forum"
            iconBackground="bg-[#D5E3FF]"
            iconColor="text-[#3E5980]"
            title="Total Issues"
            value={stats.total.toString()}
            badge="+12%"
            badgeClassName="rounded-full bg-green-100 px-2 py-1 text-xs font-bold text-green-600"
          />
        </div>

        <div className="col-span-12 md:col-span-3">
          <StatCard
            icon="error"
            iconBackground="bg-[#FFDAD6]"
            iconColor="text-[#BA1A1A]"
            title="Open"
            value={stats.open.toString()}
          >
            <span className="text-xs font-bold text-[#43474B]">
              Needs Attention
            </span>
          </StatCard>
        </div>

        <div className="col-span-12 md:col-span-3">
          <StatCard
            icon="hourglass_top"
            iconBackground="bg-[#FFDEA9]"
            iconColor="text-[#AD7B00]"
            title="In Progress"
            value={stats.inProgress.toString()}
          >
            <span className="text-xs font-bold text-[#43474B]">
              Active
            </span>
          </StatCard>
        </div>

        <div className="col-span-12 md:col-span-3">
          <StatCard
            icon="check_circle"
            iconBackground="bg-[#B5D0FD]"
            iconColor="text-[#455F87]"
            title="Resolved"
            value={stats.resolved.toString()}
          >
            <span className="text-xs font-bold text-[#43474B]">
              Completed
            </span>
          </StatCard>
        </div>
      </div>
    </>
  );
}