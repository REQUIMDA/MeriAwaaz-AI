"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Sidebar() {
  const pathname = usePathname();

  const navItems = [
    {
      label: "Dashboard",
      href: "/mp/dashboard",
      icon: "dashboard",
    },
    {
      label: "Citizen Issues",
      href: "/mp/citizen-issues",
      icon: "forum",
    },
    {
      label: "Heatmap",
      href: "/mp/heatmap",
      icon: "map",
    },
    {
      label: "Settings",
      href: "#",
      icon: "settings",
    },
  ];

  return (
    <aside className="fixed left-0 top-0 z-50 hidden h-screen w-[280px] flex-col border-r border-white/10 bg-[#0B1D2A] md:flex">
      {/* Logo */}

      <div className="flex items-center gap-4 p-8">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-white">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="/images/logo.svg"
            alt="MeriAwaaz AI"
            className="h-8 w-8 object-contain"
          />
        </div>

        <div>
          <h1 className="text-lg font-bold text-white">
            MP Portal
          </h1>

          <p className="text-xs font-semibold uppercase tracking-[0.25em] text-[#748696]">
            Govt. of India
          </p>
        </div>
      </div>

      {/* Navigation */}

      <nav className="mt-4 flex-1">
        {navItems.map((item) => {
          const active = pathname === item.href;

          return (
            <Link
              key={item.label}
              href={item.href}
              className={`flex items-center gap-3 px-6 py-3 transition-all duration-200 ${
                active
                  ? "border-l-4 border-[#FFDEA9] bg-white/10 text-white"
                  : "text-[#748696] hover:bg-white/5 hover:text-white"
              }`}
            >
              <span className="material-symbols-outlined">
                {item.icon}
              </span>

              <span className="text-sm font-medium">
                {item.label}
              </span>
            </Link>
          );
        })}
      </nav>

      {/* Footer */}

      <div className="border-t border-white/10 px-6 py-8">
        <div className="flex flex-col gap-2">
          <Link
            href="#"
            className="flex items-center gap-3 text-sm text-[#748696] transition-colors hover:text-white"
          >
            <span className="material-symbols-outlined text-[18px]">
              help
            </span>

            Help Center
          </Link>

          <Link
            href="/"
            className="flex items-center gap-3 text-sm text-[#748696] transition-colors hover:text-red-400"
          >
            <span className="material-symbols-outlined text-[18px]">
              logout
            </span>

            Logout
          </Link>
        </div>
      </div>
    </aside>
  );
}