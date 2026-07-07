export default function Stats() {
  const stats = [
    {
      value: "15,000+",
      label: "Issues Resolved",
    },
    {
      value: "500",
      label: "Projects Completed",
    },
    {
      value: "2.4M",
      label: "Citizens Engaged",
    },
  ];

  return (
    <section className="bg-[#f7f9fc] px-6 pb-20">
      <div className="mx-auto grid max-w-7xl gap-6 md:grid-cols-3">
        {stats.map((stat, index) => (
          <div
            key={stat.label}
            className="translate-y-0 rounded-xl border border-[#c3c7cc]/30 bg-white p-8 text-center opacity-100 transition-all duration-700"
            style={{
              transitionDelay: `${index * 120}ms`,
            }}
          >
            <h2 className="mb-2 text-[32px] font-bold text-black">
              {stat.value}
            </h2>

            <p className="text-sm font-medium text-[#43474b]">
              {stat.label}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}