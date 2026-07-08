"use client";

import { useMemo, useState } from "react";

import Sidebar from "@/components/mp/Sidebar";
import VoiceFAB from "@/components/mp/VoiceFAB";

import HeatmapHeader from "@/components/mp/heatmap/HeatmapHeader";
import FilterSidebar from "@/components/mp/heatmap/FilterSidebar";
import MapCanvas from "@/components/mp/heatmap/MapCanvas";
import MapControls from "@/components/mp/heatmap/MapControls";
import HeatmapLegend from "@/components/mp/heatmap/HeatmapLegend";
import DrilldownPanel from "@/components/mp/heatmap/DrilldownPanel";

import { hotspots } from "@/components/mp/heatmap/mockData";
import {
  HeatmapFilterState,
  Hotspot,
} from "@/components/mp/heatmap/types";

export default function HeatmapPage() {
  const [selectedHotspot, setSelectedHotspot] =
    useState<Hotspot | null>(hotspots[0]);

  const [filters, setFilters] =
    useState<HeatmapFilterState>({
      categories: [
        "Water Supply",
        "Road Quality",
        "Public Lighting",
        "Waste Management",
      ],
      ward: "All Wards",
      timeRange: "30days",
      severity: "all",
    });

  const filteredHotspots = useMemo(() => {
    return hotspots.filter((hotspot) => {
      const wardMatch =
        filters.ward === "All Wards" ||
        hotspot.ward === filters.ward;

      const severityMatch =
        filters.severity === "all"
          ? true
          : hotspot.severity === filters.severity;

      const categoryMatch =
        filters.categories.includes(
          hotspot.dominantCategory
        );

      return wardMatch && severityMatch && categoryMatch;
    });
  }, [filters]);

  return (
    <div className="flex h-screen overflow-hidden bg-slate-100">
      {/* Sidebar */}
      <Sidebar />

      {/* Main */}
      <main className="relative ml-[280px] flex flex-1 flex-col">
        <HeatmapHeader />

        <div className="relative flex-1 overflow-hidden">
          <MapCanvas
            hotspots={filteredHotspots}
            selectedHotspot={selectedHotspot}
            onSelectHotspot={setSelectedHotspot}
          />

          <FilterSidebar
            filters={filters}
            onFiltersChange={setFilters}
          />

          <MapControls
            onZoomIn={() => {}}
            onZoomOut={() => {}}
            onToggleLayers={() => {}}
          />

          <HeatmapLegend />

          <DrilldownPanel
            hotspot={selectedHotspot}
            onClose={() => setSelectedHotspot(null)}
          />
        </div>
      </main>

      <VoiceFAB />
    </div>
  );
}