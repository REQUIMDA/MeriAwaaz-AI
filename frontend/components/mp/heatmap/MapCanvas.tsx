"use client";

import { Hotspot } from "./types";
import HeatmapMarker from "./HeatmapMarker";

interface MapCanvasProps {
  hotspots: Hotspot[];
  selectedHotspot: Hotspot | null;
  onSelectHotspot: (hotspot: Hotspot) => void;
}

const severityStyles = {
  high: {
    size: 180,
    color: "rgba(220,38,38,0.28)",
  },
  medium: {
    size: 140,
    color: "rgba(251,191,36,0.28)",
  },
  low: {
    size: 120,
    color: "rgba(34,197,94,0.25)",
  },
};

export default function MapCanvas({
  hotspots,
  selectedHotspot,
  onSelectHotspot,
}: MapCanvasProps) {
  return (
    <div className="relative h-full w-full overflow-hidden rounded-3xl bg-slate-100">
      {/* Background Map */}
      <img
        src="/images/heatmap/map.png"
        alt="Constituency Map"
        className="absolute inset-0 h-full w-full object-cover select-none"
        draggable={false}
      />

      {/* Dark Overlay */}
      <div className="absolute inset-0 bg-gradient-to-b from-black/5 via-transparent to-black/10" />

      {/* Heat Circles */}
      {hotspots.map((hotspot) => {
        const style = severityStyles[hotspot.severity];

        return (
          <div
            key={`heat-${hotspot.id}`}
            className="pointer-events-none absolute -translate-x-1/2 -translate-y-1/2"
            style={{
              left: `${hotspot.x}%`,
              top: `${hotspot.y}%`,
              width: style.size,
              height: style.size,
            }}
          >
            <div
              className="h-full w-full animate-pulse rounded-full blur-3xl"
              style={{
                background: `radial-gradient(circle, ${style.color} 0%, transparent 70%)`,
              }}
            />
          </div>
        );
      })}

      {/* Markers */}
      {hotspots.map((hotspot) => (
        <HeatmapMarker
          key={hotspot.id}
          hotspot={hotspot}
          selected={selectedHotspot?.id === hotspot.id}
          onClick={onSelectHotspot}
        />
      ))}

      {/* Compass */}
      <div className="absolute right-6 top-6 rounded-2xl border border-white/40 bg-white/70 p-3 backdrop-blur-xl shadow-xl">
        <div className="flex h-12 w-12 items-center justify-center rounded-full border border-slate-200 bg-white text-lg font-bold text-slate-700">
          N
        </div>
      </div>
    </div>
  );
}