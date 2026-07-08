"use client";

import type { CitizenIssue } from "./types";
import IssueRow from "./IssueRow";

interface IssuesTableProps {
  issues: CitizenIssue[];

  onView: (issue: CitizenIssue) => void;
  onAssign: (issue: CitizenIssue) => void;
  onResolve: (issue: CitizenIssue) => void;
}

export default function IssuesTable({
  issues,
  onView,
  onAssign,
  onResolve,
}: IssuesTableProps) {
  return (
    <div className="glass-card bento-item rounded-[24px] overflow-hidden">

      {/* Header */}

      <div className="flex items-center justify-between border-b border-[#ECEEF1] px-8 py-6">
        <div>
          <h3 className="text-2xl font-semibold text-black">
            Citizen Issues
          </h3>

          <p className="mt-1 text-sm text-[#43474B]">
            Browse and manage all reported constituency issues
          </p>
        </div>

        <button className="flex items-center gap-2 rounded-2xl bg-[#ECEEF1] px-4 py-3 text-sm font-bold transition-all hover:bg-black hover:text-white">
          <span className="material-symbols-outlined">
            download
          </span>

          Export
        </button>
      </div>

      {/* Table */}

      <div className="overflow-x-auto">

        <table className="min-w-full">

          <thead className="bg-[#F7F9FC]">

            <tr>

              <th className="px-6 py-4 text-left text-xs font-bold uppercase tracking-wider text-[#43474B]">
                Issue ID
              </th>

              <th className="px-6 py-4 text-left text-xs font-bold uppercase tracking-wider text-[#43474B]">
                Citizen
              </th>

              <th className="px-6 py-4 text-left text-xs font-bold uppercase tracking-wider text-[#43474B]">
                Ward
              </th>

              <th className="px-6 py-4 text-left text-xs font-bold uppercase tracking-wider text-[#43474B]">
                Category
              </th>

              <th className="px-6 py-4 text-left text-xs font-bold uppercase tracking-wider text-[#43474B]">
                Priority
              </th>

              <th className="px-6 py-4 text-left text-xs font-bold uppercase tracking-wider text-[#43474B]">
                Status
              </th>

              <th className="px-6 py-4 text-left text-xs font-bold uppercase tracking-wider text-[#43474B]">
                Date
              </th>

              <th className="px-6 py-4 text-right text-xs font-bold uppercase tracking-wider text-[#43474B]">
                Actions
              </th>

            </tr>

          </thead>

          <tbody className="bg-white">

            {issues.map((issue) => (
              <IssueRow
                key={issue.id}
                issue={issue}
                onView={onView}
                onAssign={onAssign}
                onResolve={onResolve}
              />
            ))}

          </tbody>

        </table>

      </div>

      {/* Footer */}

      <div className="flex items-center justify-between border-t border-[#ECEEF1] bg-[#F7F9FC] px-8 py-5">

        <p className="text-sm text-[#43474B]">
          Showing{" "}
          <span className="font-bold text-black">
            {issues.length}
          </span>{" "}
          issues
        </p>

        <div className="flex gap-2">

          <button className="rounded-xl border border-[#C3C7CC]/40 bg-white px-4 py-2 text-sm font-semibold transition hover:bg-[#ECEEF1]">
            Previous
          </button>

          <button className="rounded-xl bg-black px-4 py-2 text-sm font-bold text-white">
            1
          </button>

          <button className="rounded-xl border border-[#C3C7CC]/40 bg-white px-4 py-2 text-sm font-semibold transition hover:bg-[#ECEEF1]">
            2
          </button>

          <button className="rounded-xl border border-[#C3C7CC]/40 bg-white px-4 py-2 text-sm font-semibold transition hover:bg-[#ECEEF1]">
            Next
          </button>

        </div>

      </div>

    </div>
  );
}