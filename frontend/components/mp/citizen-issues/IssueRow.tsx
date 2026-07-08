"use client";

import type { CitizenIssue } from "./types";

interface IssueRowProps {
  issue: CitizenIssue;
  onView: (issue: CitizenIssue) => void;
  onAssign: (issue: CitizenIssue) => void;
  onResolve: (issue: CitizenIssue) => void;
}

export default function IssueRow({
  issue,
  onView,
  onAssign,
  onResolve,
}: IssueRowProps) {
  const priorityColor = {
    Low: "bg-[#ECEEF1] text-[#43474B]",
    Medium: "bg-[#D5E3FF] text-[#455F87]",
    High: "bg-[#FFDEA9] text-[#AD7B00]",
    Critical: "bg-[#FFDAD6] text-[#BA1A1A]",
  };

  const statusColor = {
    Open: "bg-[#FFDAD6] text-[#BA1A1A]",
    Assigned: "bg-[#D5E3FF] text-[#455F87]",
    "In Progress": "bg-[#FFDEA9] text-[#AD7B00]",
    Resolved: "bg-[#DCEFE1] text-[#1C7C33]",
  };

  const categoryDot = {
    "Water Supply": "bg-blue-500",
    Roads: "bg-orange-500",
    Electricity: "bg-yellow-500",
    Healthcare: "bg-violet-500",
    Sanitation: "bg-green-500",
    Education: "bg-pink-500",
    Drainage: "bg-cyan-500",
    "Public Transport": "bg-indigo-500",
  };

  return (
    <tr className="border-b border-[#ECEEF1] transition-colors hover:bg-[#F7F9FC]">
      {/* Issue ID */}
      <td className="px-6 py-5 font-bold text-[#455F87]">
        {issue.id}
      </td>

      {/* Citizen */}
      <td className="px-6 py-5">
        <p className="font-semibold text-black">
          {issue.citizen.name}
        </p>
      </td>

      {/* Ward */}
      <td className="px-6 py-5 text-[#43474B]">
        {issue.ward}
      </td>

      {/* Category */}
      <td className="px-6 py-5">
        <div className="flex items-center gap-2">
          <span
            className={`h-2.5 w-2.5 rounded-full ${
              categoryDot[issue.category]
            }`}
          />

          <span className="text-sm font-medium text-black">
            {issue.category}
          </span>
        </div>
      </td>

      {/* Priority */}
      <td className="px-6 py-5">
        <span
          className={`rounded-full px-3 py-1 text-xs font-bold ${
            priorityColor[issue.priority]
          }`}
        >
          {issue.priority}
        </span>
      </td>

      {/* Status */}
      <td className="px-6 py-5">
        <span
          className={`rounded-full px-3 py-1 text-xs font-bold ${
            statusColor[issue.status]
          }`}
        >
          {issue.status}
        </span>
      </td>

      {/* Date */}
      <td className="px-6 py-5 text-[#43474B]">
        {issue.submittedAt}
      </td>

      {/* Actions */}
      <td className="px-6 py-5">
        <div className="flex justify-end gap-2">
          <button
            onClick={() => onView(issue)}
            className="rounded-xl bg-[#ECEEF1] px-3 py-2 text-sm font-bold transition-all hover:bg-black hover:text-white"
          >
            View
          </button>

          <button
            disabled={issue.assigned || issue.status === "Resolved"}
            onClick={() => onAssign(issue)}
            className="rounded-xl bg-[#D5E3FF] px-3 py-2 text-sm font-bold text-[#455F87] transition-all hover:bg-[#455F87] hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
          >
            {issue.assigned ? "Assigned" : "Assign"}
          </button>

          <button
            disabled={issue.status === "Resolved"}
            onClick={() => onResolve(issue)}
            className="rounded-xl bg-[#B5D0FD] px-3 py-2 text-sm font-bold text-[#0B1D2A] transition-all hover:bg-black hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
          >
            Resolve
          </button>
        </div>
      </td>
    </tr>
  );
}