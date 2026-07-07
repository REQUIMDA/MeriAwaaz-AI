import { CheckCircle2, ShieldCheck } from "lucide-react";

export default function Privacy() {
  return (
    <section className="bg-white px-6 py-24">
      <div className="mx-auto flex max-w-7xl flex-col items-center gap-16 md:flex-row">

        {/* Image */}
        <div className="w-full md:w-1/2">
          <div className="overflow-hidden rounded-3xl border border-[#c3c7cc]/20 bg-[#e6e8eb] p-1 shadow-2xl">
            <img
              src="/images/privacy.jpg"
              alt="Privacy"
              className="h-80 w-full rounded-2xl object-cover"
            />
          </div>
        </div>

        {/* Content */}
        <div className="w-full md:w-1/2">

          <div className="mb-6 flex items-center gap-3">
            <ShieldCheck
              size={34}
              className="text-[#ad7b00]"
            />

            <h2 className="text-[32px] font-semibold text-black">
              Your Data, Protected.
            </h2>
          </div>

          <p className="mb-8 text-lg leading-8 text-[#43474b]">
            MeriAwaaz AI is built on the pillars of transparency and
            absolute privacy. We use end-to-end encryption for your
            personal details and provide a clear dashboard to see how
            your data is being used for public benefit.
          </p>

          <div className="space-y-5">

            <div className="flex items-start gap-3">
              <CheckCircle2
                size={20}
                className="mt-1 text-green-600"
              />

              <p>
                GDPR & Digital Personal Data Protection Act compliant.
              </p>
            </div>

            <div className="flex items-start gap-3">
              <CheckCircle2
                size={20}
                className="mt-1 text-green-600"
              />

              <p>
                Anonymized data contribution to city planning.
              </p>
            </div>

            <div className="flex items-start gap-3">
              <CheckCircle2
                size={20}
                className="mt-1 text-green-600"
              />

              <p>
                Zero-knowledge identity verification systems.
              </p>
            </div>

          </div>

        </div>
      </div>
    </section>
  );
}