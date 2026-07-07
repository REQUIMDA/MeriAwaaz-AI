import { Info, Share2, ShieldCheck } from "lucide-react";

export default function Footer() {
  return (
    <footer className="border-t border-[#c3c7cc]/20 bg-white px-6 py-12">
      <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-8 md:flex-row">

        <div className="flex items-center gap-6">

          <img
            src="/images/emblem.png"
            alt="Government of India"
            className="h-16 w-auto opacity-80"
          />

          <div className="h-12 w-px bg-[#c3c7cc]/50" />

          <div>
            <p className="text-xs uppercase tracking-[0.25em] text-[#43474b]">
              Powered by
            </p>

            <h3 className="text-2xl font-semibold text-black">
              Digital India
            </h3>
          </div>

        </div>

        <div className="flex gap-4">

          <button className="rounded-full bg-[#eceef1] p-3 transition hover:bg-[#e0e3e6]">
            <Share2 size={20} />
          </button>

          <button className="rounded-full bg-[#eceef1] p-3 transition hover:bg-[#e0e3e6]">
            <Info size={20} />
          </button>

          <button className="rounded-full bg-[#eceef1] p-3 transition hover:bg-[#e0e3e6]">
            <ShieldCheck size={20} />
          </button>

        </div>

      </div>
    </footer>
  );
}