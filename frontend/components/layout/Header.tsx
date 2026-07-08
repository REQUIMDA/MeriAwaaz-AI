import { CircleHelp } from "lucide-react";

export default function Header() {
  return (
    <header className="sticky top-0 z-50 h-16 border-b border-gray-200/60 bg-white/80 backdrop-blur-xl">
      <div className="mx-auto flex h-full max-w-7xl items-center justify-between px-6">
        <div className="flex items-center gap-3">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="/images/logo.svg"
            alt="MeriAwaaz AI"
            className="h-8 w-8"
          />

          <h1 className="text-2xl font-semibold tracking-tight">
            MeriAwaaz AI
          </h1>
        </div>

        <button className="rounded-full p-2 transition hover:bg-slate-100">
          <CircleHelp
            size={22}
            className="text-slate-600"
          />
        </button>
      </div>
    </header>
  );
}