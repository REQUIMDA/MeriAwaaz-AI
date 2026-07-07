import { ArrowUpRight, BadgeCheck } from "lucide-react";

const schemes = [
  {
    title: "PM Awas Yojana",
    description: "Affordable housing assistance for eligible families.",
  },
  {
    title: "Ayushman Bharat",
    description: "Health insurance coverage for eligible beneficiaries.",
  },
  {
    title: "PM Vishwakarma",
    description: "Financial assistance and skill support for artisans.",
  },
];

export default function GovernmentSchemes() {
  return (
    <section className="bg-white px-6 py-16">
      <div className="mx-auto max-w-7xl">

        <div className="mb-10 flex items-center justify-between">
          <h2 className="text-3xl font-bold">
            Recommended Government Schemes
          </h2>

          <button className="flex items-center gap-2 text-sm font-semibold">
            View All
            <ArrowUpRight size={16} />
          </button>
        </div>

        <div className="grid gap-6 md:grid-cols-3">
          {schemes.map((scheme) => (
            <div
              key={scheme.title}
              className="rounded-2xl border bg-[#f7f9fc] p-6 shadow-sm transition hover:-translate-y-1 hover:shadow-lg"
            >
              <BadgeCheck
                size={34}
                className="mb-5 text-blue-700"
              />

              <h3 className="mb-3 text-xl font-semibold">
                {scheme.title}
              </h3>

              <p className="text-gray-600">
                {scheme.description}
              </p>

              <button className="mt-6 font-semibold text-blue-700">
                Learn More →
              </button>
            </div>
          ))}
        </div>

      </div>
    </section>
  );
}