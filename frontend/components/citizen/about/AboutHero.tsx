import { ArrowRight, ShieldCheck } from "lucide-react";

export default function AboutHero() {
  return (
    <section className="mx-auto grid max-w-7xl grid-cols-1 items-center gap-12 px-6 py-20 md:grid-cols-12">

      {/* Left */}

      <div className="space-y-6 md:col-span-7">

        <div className="inline-flex items-center gap-2 rounded-full bg-[#b5d0fd]/30 px-4 py-2">
          <ShieldCheck
            size={18}
            className="text-[#2d486d]"
          />

          <span className="text-sm font-semibold uppercase tracking-wider text-[#2d486d]">
            Official Government Initiative
          </span>
        </div>

        <h1 className="max-w-2xl text-5xl font-bold leading-tight text-black md:text-6xl">
          Transforming voices into
          <br />
          evidence-based decisions.
        </h1>

        <p className="max-w-xl text-lg leading-8 text-[#43474b]">
          MeriAwaaz AI bridges the gap between citizen concerns and
          legislative action. We utilize advanced neural processing
          to distill thousands of community voices into actionable
          intelligence for policy makers.
        </p>

        <button className="flex items-center gap-2 rounded-full bg-black px-8 py-4 font-medium text-white transition hover:scale-105">
          Read Whitepaper
          <ArrowRight size={18} />
        </button>

      </div>

      {/* Right */}

      <div className="relative md:col-span-5">

        <div className="overflow-hidden rounded-4xl shadow-2xl">

          <img
            src="/images/about-government.jpg"
            alt="Government Building"
            className="aspect-square w-full object-cover"
          />

          <div className="absolute inset-0 bg-gradient-to-t from-black/40 to-transparent" />

          <div className="absolute bottom-8 left-8 right-8 rounded-2xl border border-white/20 bg-white/70 p-6 backdrop-blur-xl">

            <h3 className="mb-2 text-xl font-bold text-black">
              Empowering Democracy
            </h3>

            <p className="text-sm text-gray-700">
              Direct participation through secure AI fusion.
            </p>

          </div>

        </div>

      </div>

    </section>
  );
}