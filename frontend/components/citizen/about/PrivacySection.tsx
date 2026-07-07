import { Lock, ShieldCheck } from "lucide-react";

export default function PrivacySection() {
  return (
    <section className="px-6 py-24">
      <div className="mx-auto grid max-w-7xl gap-8 md:grid-cols-2">

        {/* Left Card */}

        <div className="flex flex-col justify-between rounded-[2.5rem] border border-[#c3c7cc]/30 bg-[#f2f4f7] p-10">

          <div>

            <h2 className="mb-6 text-4xl font-bold">
              Zero-knowledge Identity
            </h2>

            <p className="mb-8 leading-8 text-[#43474b]">
              Privacy is the bedrock of democracy. MeriAwaaz AI uses
              state-of-the-art cryptographic proofs to verify your
              citizenship and residency without storing your biometric
              or identity data on our servers.
            </p>

          </div>

          <div className="flex items-center gap-4 rounded-2xl border bg-white p-5">

            <Lock
              size={34}
              className="text-black"
            />

            <div>

              <h3 className="font-semibold">
                AES-256 Protocol
              </h3>

              <p className="text-sm text-[#43474b]">
                End-to-end encrypted voice packets
              </p>

            </div>

          </div>

        </div>

        {/* Right Card */}

        <div className="flex flex-col justify-between rounded-[2.5rem] border border-[#c3c7cc]/30 bg-[#d5e3ff] p-10">

          <div>

            <h2 className="mb-6 text-4xl font-bold">
              Unbiased Recommendations
            </h2>

            <p className="mb-8 leading-8 text-[#384957]">
              Our algorithms are audited monthly by independent
              third-party panels to ensure zero political or demographic
              bias. We prioritize the intensity of the need over the
              volume of the noise.
            </p>

          </div>

          <div className="grid grid-cols-2 gap-4">

            <div className="rounded-2xl bg-white/50 p-5">

              <p className="text-4xl font-bold">
                0.00%
              </p>

              <p className="mt-2 text-xs uppercase tracking-widest">
                Bias Tolerance
              </p>

            </div>

            <div className="rounded-2xl bg-white/50 p-5">

              <ShieldCheck
                size={32}
                className="mb-3"
              />

              <p className="text-xl font-semibold">
                Open
              </p>

              <p className="mt-2 text-xs uppercase tracking-widest">
                Source Logic
              </p>

            </div>

          </div>

        </div>

      </div>
    </section>
  );
}