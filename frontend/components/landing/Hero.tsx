export default function Hero({
  hidden,
}: {
  hidden: boolean;
}) {
  return (
    <section
      className={`text-center transition-all duration-500 ${
        hidden
          ? "pointer-events-none -translate-y-6 opacity-0 h-0 overflow-hidden mb-0"
          : "mb-20 translate-y-0 opacity-100"
      }`}
    >
      <div className="mb-6 flex justify-center">
        <img
          src="/images/emblem.png"
          alt="National Emblem"
          className="mx-auto h-20 w-auto opacity-90"
        />
      </div>

      <h1 className="text-[56px] font-bold text-slate-900">
        People&apos;s Voice.
      </h1>

      <h2 className="-mt-2 text-[34px] font-semibold text-[#455F87]">
        AI-Powered Decisions.
      </h2>

      <p className="mx-auto mt-6 max-w-2xl text-lg leading-8 text-slate-600">
        A bridge between citizens and policy makers, powered by advanced
        linguistic intelligence to ensure every voice counts.
      </p>
    </section>
  );
}