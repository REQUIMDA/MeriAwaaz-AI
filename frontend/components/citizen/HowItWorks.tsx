import {
  FileText,
  Brain,
  CheckCircle2,
} from "lucide-react";

const steps = [
  {
    title: "1. Submit Issue",
    description:
      "Record a voice note or type out the problem you see in your area. Add photos for clarity.",
    icon: FileText,
    bg: "bg-[#0b1d2a]",
    color: "text-white",
  },
  {
    title: "2. AI Analysis",
    description:
      "Our AI categorizes, prioritizes and routes your concern to the right government department automatically.",
    icon: Brain,
    bg: "bg-[#b5d0fd]",
    color: "text-[#2d486d]",
  },
  {
    title: "3. Evidence Action",
    description:
      "Authorities receive a data-backed report and act. You receive real-time updates on progress.",
    icon: CheckCircle2,
    bg: "bg-[#ffdea9]",
    color: "text-[#5e4100]",
  },
];

export default function HowItWorks() {
  return (
    <section className="bg-[#f2f4f7] px-6 py-24">
      <div className="mx-auto max-w-7xl">

        <h2 className="mb-16 text-center text-[32px] font-semibold text-black">
          Simple Steps to Better Governance
        </h2>

        <div className="grid gap-12 md:grid-cols-3">
          {steps.map((step) => {
            const Icon = step.icon;

            return (
              <div
                key={step.title}
                className="group flex flex-col items-center text-center transition-all duration-700"
              >
                <div
                  className={`mb-6 flex h-20 w-20 items-center justify-center rounded-full transition-transform duration-300 group-hover:scale-110 ${step.bg}`}
                >
                  <Icon
                    size={36}
                    className={step.color}
                  />
                </div>

                <h3 className="mb-4 text-2xl font-semibold">
                  {step.title}
                </h3>

                <p className="leading-7 text-[#43474b]">
                  {step.description}
                </p>
              </div>
            );
          })}
        </div>

      </div>
    </section>
  );
}