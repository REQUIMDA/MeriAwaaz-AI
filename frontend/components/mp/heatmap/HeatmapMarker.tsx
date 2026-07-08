"use client";

import { Hotspot } from "./types";

interface HeatmapMarkerProps {
  hotspot: Hotspot;
  selected: boolean;
  onClick: (hotspot: Hotspot) => void;
}

const severityClasses = {
  high: {
    pulse: "bg-red-500/30",
    marker: "bg-red-600",
  },
  medium: {
    pulse: "bg-amber-400/30",
    marker: "bg-amber-400",
  },
  low: {
    pulse: "bg-emerald-500/30",
    marker: "bg-emerald-500",
  },
};

export default function HeatmapMarker({
  hotspot,
  selected,
  onClick,
}: HeatmapMarkerProps) {
  const colors = severityClasses[hotspot.severity];

  return (
    <button
      type="button"
      aria-label={hotspot.title}
      onClick={() => onClick(hotspot)}
      className="group absolute -translate-x-1/2 -translate-y-1/2 cursor-pointer"
      style={{
        left: `${hotspot.x}%`,
        top: `${hotspot.y}%`,
      }}
    >
      {/* Heat Pulse */}
      <span
        className={`
          absolute left-1/2 top-1/2
          h-16 w-16 -translate-x-1/2 -translate-y-1/2
          rounded-full blur-xl
          animate-pulse
          transition-all duration-300
          ${colors.pulse}
          ${selected ? "scale-125 opacity-100" : "opacity-80"}
        `}
      />

      {/* Marker */}
      <span
        className={`
          relative z-10 block
          h-4 w-4 rounded-full border-2 border-white shadow-xl
          transition-all duration-200
          ${colors.marker}
          ${
            selected
              ? "scale-150 ring-4 ring-white/40"
              : "group-hover:scale-125"
          }
        `}
      />

      {/* Tooltip */}
      <span
        className="
          pointer-events-none
          absolute left-1/2 top-6
          -translate-x-1/2
          whitespace-nowrap
          rounded-lg
          bg-slate-900/95
          px-3
          py-1.5
          text-xs
          font-medium
          text-white
          opacity-0
          shadow-xl
          transition-all
          duration-200
          group-hover:translate-y-1
          group-hover:opacity-100
        "
      >
        {hotspot.title}
      </span>
    </button>
  );
}