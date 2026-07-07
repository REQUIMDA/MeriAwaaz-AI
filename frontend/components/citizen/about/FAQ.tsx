"use client";

import { useState } from "react";
import { ChevronDown } from "lucide-react";

const faqs = [
  {
    question:
      "How do I know my voice recording was heard?",
    answer:
      "Every submission generates a unique Tracking Hash. You can see the status of your issue—from 'Clustered' to 'Presented to MP'—directly in your personal dashboard.",
  },
  {
    question:
      "Is MeriAwaaz AI available in my regional language?",
    answer:
      "Yes, the platform currently supports 22 official Indian languages including Hindi, Tamil, Bengali, Marathi and Kannada. The AI transcribes and translates in real-time.",
  },
  {
    question:
      "Who has access to the raw data?",
    answer:
      "Raw recordings are anonymized immediately after processing. Only aggregated thematic data is shared with government offices to prevent any individual identification.",
  },
];

export default function FAQ() {
  const [open, setOpen] = useState<number | null>(0);

  return (
    <section className="px-6 py-24">
      <div className="mx-auto max-w-3xl">

        <h2 className="mb-12 text-center text-4xl font-bold">
          Frequently Asked Questions
        </h2>

        <div className="space-y-4">

          {faqs.map((faq, index) => (
            <div
              key={faq.question}
              className="overflow-hidden rounded-2xl border bg-white"
            >
              <button
                onClick={() =>
                  setOpen(open === index ? null : index)
                }
                className="flex w-full items-center justify-between p-6 text-left transition hover:bg-[#f7f9fc]"
              >
                <span className="font-medium">
                  {faq.question}
                </span>

                <ChevronDown
                  size={22}
                  className={`transition-transform ${
                    open === index ? "rotate-180" : ""
                  }`}
                />
              </button>

              <div
                className={`overflow-hidden transition-all duration-300 ${
                  open === index
                    ? "max-h-40 border-t"
                    : "max-h-0"
                }`}
              >
                <p className="p-6 pt-5 leading-7 text-[#43474b]">
                  {faq.answer}
                </p>
              </div>
            </div>
          ))}

        </div>

      </div>
    </section>
  );
}