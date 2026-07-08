"use client";

/**
 * LocationPicker — an interactive map (Leaflet + OpenStreetMap, loaded from the
 * same free CDN as the constituency heatmap; no npm dependency, no API key).
 *
 * Interactive mode (default): click the map to drop / move a red 📍 marker. The
 * clicked point is reverse-geocoded (Nominatim) and returned via onChange so the
 * caller can fill an address box. A "Remove marker" button clears it.
 *
 * Read-only mode (interactive={false}): shows a fixed marker at the given
 * coordinates. The map still zooms/pans, but the marker can't be moved.
 */
import { useEffect, useRef, useState } from "react";

// Leaflet is loaded once from the CDN and shared across all instances.
let leafletPromise: Promise<unknown> | null = null;

function loadLeaflet(): Promise<unknown> {
  if (typeof window === "undefined") return Promise.reject(new Error("no window"));
  const w = window as unknown as { L?: unknown };
  if (w.L) return Promise.resolve(w.L);
  if (leafletPromise) return leafletPromise;

  leafletPromise = new Promise((resolve, reject) => {
    if (!document.querySelector("link[data-leaflet]")) {
      const link = document.createElement("link");
      link.rel = "stylesheet";
      link.href = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css";
      link.setAttribute("data-leaflet", "1");
      document.head.appendChild(link);
    }
    const script = document.createElement("script");
    script.src = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js";
    script.async = true;
    script.onload = () => resolve((window as unknown as { L: unknown }).L);
    script.onerror = () => reject(new Error("Leaflet failed to load"));
    document.body.appendChild(script);
  });
  return leafletPromise;
}

const PIN_SVG = `
<svg width="30" height="42" viewBox="0 0 30 42" xmlns="http://www.w3.org/2000/svg">
  <path d="M15 0C7 0 0.5 6.5 0.5 14.5 0.5 25 15 42 15 42S29.5 25 29.5 14.5C29.5 6.5 23 0 15 0Z"
        fill="#e11d2a" stroke="#ffffff" stroke-width="2"/>
  <circle cx="15" cy="14.5" r="5" fill="#ffffff"/>
</svg>`;

async function reverseGeocode(lat: number, lng: number): Promise<string> {
  const fallback = `${lat.toFixed(5)}, ${lng.toFixed(5)}`;
  try {
    const r = await fetch(
      `https://nominatim.openstreetmap.org/reverse?format=json&zoom=16&addressdetails=1&lat=${lat}&lon=${lng}`
    );
    const j = await r.json();
    return j.display_name || fallback;
  } catch {
    return fallback;
  }
}

export interface LocationPickerProps {
  initialLat?: number | null;
  initialLng?: number | null;
  interactive?: boolean;
  showRemove?: boolean;
  height?: string;
  className?: string;
  onChange?: (lat: number, lng: number, address: string) => void;
  onRemove?: () => void;
}

export default function LocationPicker({
  initialLat,
  initialLng,
  interactive = true,
  showRemove = true,
  height = "20rem",
  className = "",
  onChange,
  onRemove,
}: LocationPickerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const mapRef = useRef<any>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const markerRef = useRef<any>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const LRef = useRef<any>(null);

  const [hasMarker, setHasMarker] = useState(initialLat != null && initialLng != null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    let cancelled = false;

    loadLeaflet()
      .then((L) => {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const LL = L as any;
        if (cancelled || !containerRef.current || mapRef.current) return;
        LRef.current = LL;

        const hasStart = initialLat != null && initialLng != null;
        const start: [number, number] = hasStart
          ? [initialLat as number, initialLng as number]
          : [21.1458, 79.0882]; // Nagpur, Maharashtra
        const zoom = hasStart ? 15 : 5;

        const map = LL.map(containerRef.current, {
          zoomControl: true,
          scrollWheelZoom: true,
        }).setView(start, zoom);

        LL.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
          maxZoom: 19,
          attribution:
            '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        }).addTo(map);

        mapRef.current = map;

        if (hasStart) placeMarker(initialLat as number, initialLng as number, false);

        if (interactive) {
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          map.on("click", (e: any) => {
            placeMarker(e.latlng.lat, e.latlng.lng, true);
          });
        }

        // Maps inside cards/hidden panels need a size recalculation.
        setTimeout(() => mapRef.current && mapRef.current.invalidateSize(), 250);
      })
      .catch(() => !cancelled && setFailed(true));

    return () => {
      cancelled = true;
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
        markerRef.current = null;
      }
    };
    // Init once; the marker is then driven imperatively.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function icon() {
    return LRef.current.divIcon({
      className: "",
      iconSize: [30, 42],
      iconAnchor: [15, 42],
      html: PIN_SVG,
    });
  }

  async function placeMarker(lat: number, lng: number, notify: boolean) {
    const LL = LRef.current;
    const map = mapRef.current;
    if (!LL || !map) return;

    if (markerRef.current) markerRef.current.setLatLng([lat, lng]);
    else markerRef.current = LL.marker([lat, lng], { icon: icon() }).addTo(map);

    setHasMarker(true);

    if (notify && onChange) {
      const address = await reverseGeocode(lat, lng);
      onChange(lat, lng, address);
    }
  }

  function removeMarker() {
    if (markerRef.current && mapRef.current) mapRef.current.removeLayer(markerRef.current);
    markerRef.current = null;
    setHasMarker(false);
    onRemove?.();
  }

  if (failed) {
    return (
      <div
        className={`flex items-center justify-center rounded-2xl bg-[#ECEEF1] text-sm text-[#43474B] ${className}`}
        style={{ height }}
      >
        Map could not load (check your internet connection).
      </div>
    );
  }

  return (
    <div className={`relative ${className}`} style={{ height }}>
      <div ref={containerRef} className="h-full w-full rounded-2xl" style={{ zIndex: 0 }} />

      {interactive && (
        <div className="pointer-events-none absolute left-1/2 top-3 z-[500] -translate-x-1/2 rounded-full bg-white/90 px-3 py-1 text-xs font-semibold text-[#43474B] shadow">
          {hasMarker ? "Tap the map to move the pin" : "Tap the map to drop a pin"}
        </div>
      )}

      {interactive && showRemove && hasMarker && (
        <button
          type="button"
          onClick={removeMarker}
          className="absolute right-3 top-3 z-[500] rounded-full bg-white px-3 py-1 text-xs font-bold text-[#BA1A1A] shadow transition hover:bg-[#BA1A1A] hover:text-white"
        >
          Remove marker
        </button>
      )}
    </div>
  );
}
