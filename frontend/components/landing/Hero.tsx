export default function Hero() {
  return (
    <section className="mb-20 text-center">
      <div className="mb-6 flex justify-center">
        <img
          src="/images/emblem.png"
          alt="National Emblem"
          className="mx-auto mb-2 h-20 w-auto opacity-90"
        />
      </div>

      <h1 className="text-[56px] font-bold text-slate-900">
        People&apos;s Voice.
      </h1>

      <h2 className="-mt-2 text-[32px] font-semibold text-[#455F87]">
        AI-Powered Decisions.
      </h2>

      <p className="mx-auto mt-6 max-w-2xl text-lg leading-8 text-slate-600">
        A bridge between citizens and policy makers, powered by advanced
        linguistic intelligence to ensure every voice counts.
      </p>
    </section>
  );
}