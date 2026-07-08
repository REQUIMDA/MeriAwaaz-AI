"use client";

import type { CitizenIssue } from "./types";
import LocationPicker from "@/components/common/LocationPicker";

interface IssueDrawerProps {
  issue: CitizenIssue | null;
  open: boolean;
  onClose: () => void;
}

export default function IssueDrawer({
  issue,
  open,
  onClose,
}: IssueDrawerProps) {
  return (
    <>
      {/* Overlay */}

      <div
        onClick={onClose}
        className={`fixed inset-0 z-40 bg-black/30 backdrop-blur-sm transition-opacity duration-300 ${
          open
            ? "pointer-events-auto opacity-100"
            : "pointer-events-none opacity-0"
        }`}
      />

      {/* Drawer */}

      <aside
        className={`fixed right-0 top-0 z-50 flex h-screen w-full max-w-xl flex-col bg-[#F7F9FC] shadow-2xl transition-transform duration-300 ${
          open ? "translate-x-0" : "translate-x-full"
        }`}
      >
        {/* Header */}

        <div className="flex items-center justify-between border-b border-[#ECEEF1] px-8 py-6">
          <div>
            <h2 className="text-2xl font-bold text-black">
              Issue Details
            </h2>

            <p className="mt-1 text-sm text-[#43474B]">
              Complete issue information
            </p>
          </div>

          <button
            onClick={onClose}
            className="rounded-xl bg-[#ECEEF1] p-2 transition hover:bg-black hover:text-white"
          >
            <span className="material-symbols-outlined">
              close
            </span>
          </button>
        </div>

        {issue && (
          <div className="flex-1 space-y-8 overflow-y-auto p-8">
            {/* Basic Details */}

            <div className="glass-card rounded-[24px] p-6">
              <h3 className="mb-5 text-xl font-bold text-black">
                {issue.title}
              </h3>

              <div className="space-y-5">
                <InfoRow
                  label="Issue ID"
                  value={issue.id}
                />

                <InfoRow
                  label="Citizen"
                  value={issue.citizen.name}
                />

                <InfoRow
                  label="Ward"
                  value={issue.ward}
                />

                <InfoRow
                  label="Category"
                  value={issue.category}
                />

                <InfoRow
                  label="Priority"
                  value={issue.priority}
                />

                <InfoRow
                  label="Status"
                  value={issue.status}
                />

                <InfoRow
                  label="Submitted"
                  value={issue.submittedAt}
                />
              </div>
            </div>

            {/* Description */}

            <div className="glass-card rounded-[24px] p-6">
              <h3 className="mb-4 text-lg font-bold text-black">
                Description
              </h3>

              <p className="leading-7 text-[#43474B]">
                {issue.description}
              </p>
            </div>

            {/* Attached Image — only when the submission actually has one */}

            {issue.image ? (
              <div className="glass-card rounded-[24px] p-6">
                <h3 className="mb-4 text-lg font-bold text-black">
                  Attached Image
                </h3>

                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={issue.image}
                  alt="Citizen-attached photo"
                  className="max-h-96 w-full rounded-2xl bg-[#ECEEF1] object-contain"
                />
              </div>
            ) : null}

            {/* Attached Voice Note — only when present */}

            {issue.audioUrl ? (
              <div className="glass-card rounded-[24px] p-6">
                <h3 className="mb-4 text-lg font-bold text-black">
                  Voice Note
                </h3>

                <audio controls src={issue.audioUrl} className="w-full">
                  Your browser does not support audio playback.
                </audio>
              </div>
            ) : null}

            {/* Complaint Location — only when the citizen dropped a pin */}

            {issue.lat != null && issue.lng != null ? (
              <div className="glass-card rounded-[24px] p-6">
                <h3 className="mb-4 text-lg font-bold text-black">
                  Complaint Location
                </h3>

                <LocationPicker
                  interactive={false}
                  showRemove={false}
                  initialLat={issue.lat}
                  initialLng={issue.lng}
                  height="16rem"
                />
              </div>
            ) : null}

            {/* AI Summary */}

            <div className="rounded-[24px] bg-[#0B1D2A] p-6 text-white">
              <div className="mb-4 flex items-center gap-2">
                <span className="material-symbols-outlined text-[#FFDEA9]">
                  psychology
                </span>

                <h3 className="text-lg font-bold">
                  AI Summary
                </h3>
              </div>

              <p className="leading-7 text-[#D5E3FF]">
                {issue.aiSummary}
              </p>
            </div>

            {/* AI Action */}

            <div className="rounded-[24px] bg-[#455F87] p-6 text-white">
              <div className="mb-4 flex items-center gap-2">
                <span className="material-symbols-outlined">
                  tips_and_updates
                </span>

                <h3 className="text-lg font-bold">
                  Suggested Action
                </h3>
              </div>

              <p className="leading-7">
                {issue.aiSuggestedAction}
              </p>
            </div>
          </div>
        )}
      </aside>
    </>
  );
}

interface InfoRowProps {
  label: string;
  value: string;
}

function InfoRow({
  label,
  value,
}: InfoRowProps) {
  return (
    <div className="flex justify-between border-b border-[#ECEEF1] pb-3">
      <span className="font-medium text-[#43474B]">
        {label}
      </span>

      <span className="font-semibold text-black">
        {value}
      </span>
    </div>
  );
}