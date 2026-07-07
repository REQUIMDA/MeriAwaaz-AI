"use client";

export default function DashboardHeader() {
  return (
    <header className="mb-10 flex items-end justify-between">
      <div>
        <p className="mb-1 text-sm font-medium text-[#43474B]">
          Good Morning, Honorable Member
        </p>

        <h2 className="text-[32px] font-bold leading-10 tracking-[-0.01em] text-black">
          Constituency Overview
        </h2>
      </div>

      <div className="flex items-center gap-4">
        {/* Team Avatars */}

        <div className="flex -space-x-3 overflow-hidden">
          <img
            src="https://lh3.googleusercontent.com/aida-public/AB6AXuDGXoyYKoWzKYC7duQRm6y4iUBEpqeOjSS66grMnzt7Wa4jLXZ4zPA4kShtfLRYuIewns_QMpld1dWW72VJu1M1SJ_1b_eH61V5W5kXwv7zCxeVIwTSyrQvQ-M8sRy8A-1voIvM8l6eQfFtq984fuszWriLHV3vkpIrYJ65sVHRBhEP2WQbfjqYU8IXRxYPKWm5VT_rnV3FVw1spgvP1ucjmJnxC8_KKQ7QMOrhMw9v3tIN63qVmLA"
            alt="Administrative Assistant"
            className="inline-block h-10 w-10 rounded-full object-cover ring-2 ring-white"
          />

          <img
            src="https://lh3.googleusercontent.com/aida-public/AB6AXuCMcxAwInlHN1jozBeYGCmsYgNl937TpmebkGCoxmMji3Ze-fbMHy43t8dgSf9xFnb7brfOoORhL55Wz4xwGGsDGrlBcuErtpN1ZmP95ffneO52T09HI2mhT2RXczlZ3IsKS-Eo0_C6fEUZ-INwB5NWSYbBzapmp77KFL6Carinurl0hwXJy9HA_7YOEIiEpQh7sgMOoMQ3TR3GEV-C30ptVldVSlobG5PHn5I-Hg8t_fIWTSSKuaI"
            alt="Policy Advisor"
            className="inline-block h-10 w-10 rounded-full object-cover ring-2 ring-white"
          />

          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#E0E3E6] text-xs font-bold ring-2 ring-white">
            +12
          </div>
        </div>

        {/* Notifications */}

        <button className="flex h-12 w-12 items-center justify-center rounded-full border border-[#C3C7CC]/30 bg-white shadow-sm transition hover:bg-gray-50">
          <span className="material-symbols-outlined text-[#43474B]">
            notifications
          </span>
        </button>

        {/* CTA */}

        <button className="flex h-12 items-center gap-2 rounded-full bg-black px-6 font-bold text-white transition hover:opacity-90">
          <span className="material-symbols-outlined">
            add
          </span>

          New Initiative
        </button>
      </div>
    </header>
  );
}