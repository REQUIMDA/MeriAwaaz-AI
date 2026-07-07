"use client";

interface MapControlsProps {
  onZoomIn?: () => void;
  onZoomOut?: () => void;
  onToggleLayers?: () => void;
}

export default function MapControls({
  onZoomIn,
  onZoomOut,
  onToggleLayers,
}: MapControlsProps) {
  return (
    <div className="absolute bottom-8 right-8 z-30 flex flex-col gap-3">
      {/* Zoom Controls */}
      <div
        className="
          overflow-hidden
          rounded-2xl
          border
          border-white/40
          bg-white/70
          shadow-2xl
          backdrop-blur-2xl
        "
      >
        <button
          onClick={onZoomIn}
          className="
            flex
            h-12
            w-12
            items-center
            justify-center
            transition-colors
            hover:bg-slate-100
            active:scale-95
          "
          aria-label="Zoom In"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-5 w-5 text-slate-700"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M12 5v14m-7-7h14"
            />
          </svg>
        </button>

        <div className="mx-2 border-t border-slate-200" />

        <button
          onClick={onZoomOut}
          className="
            flex
            h-12
            w-12
            items-center
            justify-center
            transition-colors
            hover:bg-slate-100
            active:scale-95
          "
          aria-label="Zoom Out"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-5 w-5 text-slate-700"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M5 12h14"
            />
          </svg>
        </button>
      </div>

      {/* Layers Button */}
      <button
        onClick={onToggleLayers}
        aria-label="Toggle Layers"
        className="
          flex
          h-12
          w-12
          items-center
          justify-center
          rounded-2xl
          border
          border-white/40
          bg-white/70
          shadow-2xl
          backdrop-blur-2xl
          transition-all
          hover:bg-slate-100
          hover:scale-105
          active:scale-95
        "
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-5 w-5 text-slate-700"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M4 7l8-4 8 4-8 4-8-4zm0 5l8 4 8-4m-16 5l8 4 8-4"
          />
        </svg>
      </button>
    </div>
  );
}