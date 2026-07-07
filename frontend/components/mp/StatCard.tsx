"use client";

import { ReactNode } from "react";

interface StatCardProps {
  icon: string;
  iconBackground: string;
  iconColor: string;
  title: string;
  value: string;
  badge?: string;
  badgeClassName?: string;
  children?: ReactNode;
}

export default function StatCard({
  icon,
  iconBackground,
  iconColor,
  title,
  value,
  badge,
  badgeClassName,
  children,
}: StatCardProps) {
  return (
    <div className="glass-card bento-item rounded-[24px] p-6">
      <div className="mb-4 flex items-start justify-between">
        <span
          className={`material-symbols-outlined rounded-xl p-2 ${iconBackground} ${iconColor}`}
        >
          {icon}
        </span>

        {badge ? (
          <span className={badgeClassName}>{badge}</span>
        ) : (
          children
        )}
      </div>

      <p className="text-sm font-medium text-[#43474B]">
        {title}
      </p>

      <h3 className="mt-1 text-[40px] font-extrabold leading-none tracking-[-0.02em] text-black">
        {value}
      </h3>
    </div>
  );
}