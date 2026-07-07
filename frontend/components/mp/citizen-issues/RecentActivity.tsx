"use client";

import type { ActivityItem } from "./types";

interface RecentActivityProps {
  activities: ActivityItem[];
}

export default function RecentActivity({
  activities,
}: RecentActivityProps) {
  const getIcon = (title: string) => {
    switch (title) {
      case "Issue Created":
        return {
          icon: "add_circle",
          bg: "bg-[#D5E3FF]",
          color: "text-[#455F87]",
        };

      case "Assigned":
        return {
          icon: "assignment_ind",
          bg: "bg-[#FFDEA9]",
          color: "text-[#AD7B00]",
        };

      case "Status Updated":
        return {
          icon: "sync",
          bg: "bg-[#ECEEF1]",
          color: "text-[#43474B]",
        };

      case "Issue Resolved":
        return {
          icon: "check_circle",
          bg: "bg-[#B5D0FD]",
          color: "text-[#455F87]",
        };

      default:
        return {
          icon: "notifications",
          bg: "bg-[#ECEEF1]",
          color: "text-[#43474B]",
        };
    }
  };

  return (
    <div className="glass-card bento-item rounded-[24px] p-8">
      {/* Header */}

      <div className="mb-8 flex items-center justify-between">
        <div>
          <h3 className="text-2xl font-semibold text-black">
            Recent Activity
          </h3>

          <p className="mt-1 text-sm text-[#43474B]">
            Latest updates from constituency issues
          </p>
        </div>

        <span className="rounded-full bg-[#ECEEF1] px-3 py-1 text-xs font-bold text-[#43474B]">
          {activities.length} Updates
        </span>
      </div>

      {/* Timeline */}

      <div className="relative">

        <div className="absolute left-6 top-2 bottom-2 w-[2px] bg-[#ECEEF1]" />

        <div className="space-y-6">

          {activities.map((activity) => {
            const style = getIcon(activity.title);

            return (
              <div
                key={activity.id}
                className="relative flex gap-5"
              >
                {/* Icon */}

                <div
                  className={`relative z-10 flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl ${style.bg}`}
                >
                  <span
                    className={`material-symbols-outlined ${style.color}`}
                    style={{
                      fontVariationSettings: '"FILL" 1',
                    }}
                  >
                    {style.icon}
                  </span>
                </div>

                {/* Content */}

                <div className="flex-1 rounded-2xl border border-[#C3C7CC]/30 bg-[#F7F9FC] p-5 transition-all hover:border-[#455F87]">

                  <div className="flex items-start justify-between">

                    <div>

                      <h4 className="font-bold text-black">
                        {activity.title}
                      </h4>

                      <p className="mt-1 text-sm text-[#43474B]">
                        {activity.description}
                      </p>

                      <p className="mt-2 text-xs font-semibold text-[#455F87]">
                        {activity.issueId}
                      </p>

                    </div>

                    <span className="text-xs font-medium text-[#74777C]">
                      {activity.timestamp}
                    </span>

                  </div>

                </div>
              </div>
            );
          })}

        </div>

      </div>
    </div>
  );
}