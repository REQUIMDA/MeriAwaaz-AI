import {
  Brain,
  Network,
  CheckCircle,
  GitBranch,
} from "lucide-react";

const cards = [
  {
    title: "Issue Clustering",
    description:
      "Natural Language Processing (NLP) identifies common themes across thousands of voice recordings, grouping hyper-local issues into significant regional trends.",
    icon: Network,
    bg: "bg-white",
    iconBg: "bg-[#b5d0fd]/20",
    iconColor: "text-[#2d486d]",
    dark: false,
    bullets: [
      "Semantic Mapping",
      "Dialect Normalization",
    ],
  },
  {
    title: "Data Fusion",
    description:
      "Citizen inputs are correlated with existing geospatial data, infrastructure reports and budget allocations to provide context for every reported issue.",
    icon: GitBranch,
    bg: "bg-[#0b1d2a]",
    iconBg: "bg-white/10",
    iconColor: "text-white",
    dark: true,
  },
  {
    title: "Recommendation Engine",
    description:
      "AI generates neutral, evidence-based policy suggestions for Members of Parliament, ranking actions based on urgency, impact and feasibility.",
    icon: Brain,
    bg: "bg-white",
    iconBg: "bg-[#ffdea9]/30",
    iconColor: "text-[#ad7b00]",
    dark: false,
  },
];

export default function AIWorkflow() {
  return (
    <section className="px-6 py-24">
      <div className="mx-auto max-w-7xl">

        <div className="mb-16 text-center">
          <h2 className="mb-4 text-4xl font-bold">
            How AI Powers Your Voice
          </h2>

          <p className="mx-auto max-w-2xl text-lg text-[#43474b]">
            Our proprietary engine ensures that no issue goes unheard
            by using three layers of intelligent processing.
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-3">

          {cards.map((card) => {
            const Icon = card.icon;

            return (
              <div
                key={card.title}
                className={`${card.bg} rounded-3xl border p-8 shadow-sm transition hover:-translate-y-1 hover:shadow-xl`}
              >
                <div
                  className={`mb-6 flex h-14 w-14 items-center justify-center rounded-2xl ${card.iconBg}`}
                >
                  <Icon
                    size={30}
                    className={card.iconColor}
                  />
                </div>

                <h3
                  className={`mb-4 text-2xl font-semibold ${
                    card.dark ? "text-white" : "text-black"
                  }`}
                >
                  {card.title}
                </h3>

                <p
                  className={`leading-7 ${
                    card.dark
                      ? "text-gray-300"
                      : "text-[#43474b]"
                  }`}
                >
                  {card.description}
                </p>

                {card.bullets && (
                  <div className="mt-8 space-y-2">
                    {card.bullets.map((item) => (
                      <div
                        key={item}
                        className="flex items-center gap-2 text-sm"
                      >
                        <CheckCircle
                          size={16}
                          className="text-green-600"
                        />

                        <span>{item}</span>
                      </div>
                    ))}
                  </div>
                )}

                {card.dark && (
                  <div className="mt-10 border-t border-white/10 pt-6">
                    <p className="text-xs uppercase tracking-[0.2em] text-gray-400">
                      Multi-source Sync
                    </p>
                  </div>
                )}

                {!card.dark &&
                  card.title === "Recommendation Engine" && (
                    <>
                      <div className="mt-8 h-2 rounded-full bg-gray-200">
                        <div className="h-2 w-3/4 rounded-full bg-[#ad7b00]" />
                      </div>

                      <p className="mt-2 text-xs font-bold uppercase text-[#ad7b00]">
                        Confidence Score: 92%
                      </p>
                    </>
                  )}
              </div>
            );
          })}

        </div>
      </div>
    </section>
  );
}