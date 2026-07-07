interface IssueProgressProps {
  step: 1 | 2 | 3;
}

export default function IssueProgress({
  step,
}: IssueProgressProps) {
  const steps = [
    "Issue Type",
    "Location",
    "Review",
  ];

  return (
    <div className="mb-12">
      <div className="flex items-center justify-between">

        {steps.map((label, index) => {
          const current = index + 1;
          const completed = current < step;
          const active = current === step;

          return (
            <div
              key={label}
              className="flex flex-1 items-center"
            >
              <div className="flex flex-col items-center">

                <div
                  className={`flex h-10 w-10 items-center justify-center rounded-full font-bold transition-all ${
                    completed
                      ? "bg-black text-white"
                      : active
                      ? "bg-[#FFB703] text-black"
                      : "bg-[#e0e3e6] text-[#43474b]"
                  }`}
                >
                  {completed ? "✓" : current}
                </div>

                <span
                  className={`mt-2 text-xs font-semibold uppercase tracking-wide ${
                    active
                      ? "text-black"
                      : "text-[#43474b]"
                  }`}
                >
                  {label}
                </span>

              </div>

              {current !== 3 && (
                <div className="mx-4 mb-6 h-[2px] flex-1 bg-[#c3c7cc]" />
              )}
            </div>
          );
        })}

      </div>
    </div>
  );
}