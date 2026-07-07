"use client";

export default function VoiceFAB() {
  return (
    <div className="fixed bottom-8 right-8 z-[60]">
      <button className="group pulse-animation relative flex h-16 w-16 items-center justify-center rounded-full bg-[#FF9933] shadow-lg transition-transform hover:scale-110 active:scale-95">
        <span className="material-symbols-outlined text-3xl text-white">
          mic
        </span>

        <span className="absolute -top-12 right-0 whitespace-nowrap rounded-lg border border-[#C3C7CC]/30 bg-white px-3 py-1 text-xs font-bold shadow-sm opacity-0 transition-opacity group-hover:opacity-100">
          Voice Command
        </span>
      </button>
    </div>
  );
}