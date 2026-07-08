"use client";

/**
 * MP Constituency Heatmap.
 *
 * The interactive map is the self-contained Leaflet + OpenStreetMap page served
 * by the backend at `${API_BASE}/heatmap`. It reads live data from
 * `GET /api/heatmap` (same-origin inside the iframe, so no CORS needed) and
 * auto-refreshes as new submissions arrive. We embed it here so it lives inside
 * the MP portal shell (the sidebar comes from app/mp/layout.tsx).
 */
import { HEATMAP_URL } from "@/services/api";

export default function HeatmapPage() {
  return (
    <div className="flex flex-col gap-6">
      <header className="flex items-end justify-between">
        <div>
          <h1 className="text-[32px] font-bold leading-10 tracking-[-0.01em] text-black">
            Constituency Heatmap
          </h1>
          <p className="mt-1 text-sm text-[#43474B]">
            One marker per town — click a marker to browse its clustered projects.
            Colour reflects severity; the map syncs with new submissions.
          </p>
        </div>

        <a
          href={HEATMAP_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="flex h-11 items-center gap-2 rounded-full bg-black px-5 text-sm font-bold text-white transition hover:opacity-90"
        >
          <span className="material-symbols-outlined text-[18px]">open_in_new</span>
          Open full screen
        </a>
      </header>

      <div className="overflow-hidden rounded-[24px] border border-[#e6edf3] bg-white shadow-sm">
        <iframe
          src={HEATMAP_URL}
          title="Constituency Heatmap"
          className="w-full"
          style={{ height: "82vh", border: "0" }}
        />
      </div>
    </div>
  );
}
