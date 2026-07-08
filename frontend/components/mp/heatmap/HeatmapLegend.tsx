"use client";

export default function HeatmapLegend() {
  return (
    <div
      className="
        absolute
        bottom-8
        left-8
        z-30
        flex
        items-center
        gap-6
        rounded-2xl
        border
        border-white/40
        bg-white/70
        px-5
        py-4
        shadow-2xl
        backdrop-blur-2xl
      "
    >
      <LegendItem
        color="bg-red-500"
        title="High Priority"
        subtitle="Immediate Attention"
      />

      <LegendItem
        color="bg-amber-400"
        title="Medium Priority"
        subtitle="Monitor Closely"
      />

      <LegendItem
        color="bg-emerald-500"
        title="Low Priority"
        subtitle="Stable"
      />
    </div>
  );
}

interface LegendItemProps {
  color: string;
  title: string;
  subtitle: string;
}

function LegendItem({
  color,
  title,
  subtitle,
}: LegendItemProps) {
  return (
    <div className="flex items-center gap-3">
      {/* Color Indicator */}
      <div className="relative flex h-4 w-4 items-center justify-center">
        <span
          className={`absolute h-4 w-4 rounded-full ${color} opacity-25`}
        />

        <span
          className={`relative h-3 w-3 rounded-full ${color}`}
        />
      </div>

      {/* Text */}
      <div>
        <p className="text-sm font-semibold text-slate-800">
          {title}
        </p>

        <p className="text-xs text-slate-500">
          {subtitle}
        </p>
      </div>
    </div>
  );
}