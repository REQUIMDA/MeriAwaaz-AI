"use client";

import Link from "next/link";

export default function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 z-50 hidden h-screen w-[280px] flex-col border-r border-white/10 bg-[#0B1D2A] md:flex">
      {/* Logo */}
      <div className="flex items-center gap-4 p-8">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-white">
          <img
            src="https://lh3.googleusercontent.com/aida-public/AB6AXuDbT41SeAXjoqUs3J1GbOPFwpPmc6o2cQfgvvmgkJzuIWqYC3-Fz2T8yNxwsZ3Htpzha3hzzw2BYwEKqrfLOCP48JISx2Uhavc71lH58qRB2k4J9pklLesYOvn5N_njlDUUQ5YTA9sDOrIvacR8o9fVWj4GePjT7Fzig4J4yDK8DQ7jy-sT1Hgg-qdnmt4HaKz2yLaArqbuBi7IC5dP3nrIZUDteIdl_NkXezBCMs26dvbIf9UEZMA"
            alt="Government of India"
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
        <Link
          href="/dashboard"
          className="translate-x-1 flex items-center gap-3 border-l-4 border-[#FFDEA9] bg-white/10 px-6 py-3 text-white transition-all duration-200"
        >
          <span className="material-symbols-outlined">
            dashboard
          </span>

          <span className="text-sm font-medium">
            Dashboard
          </span>
        </Link>

        <Link
  href="/citizen-issues"
  className="flex items-center gap-3 px-6 py-3 text-[#748696] transition-all hover:bg-white/5 hover:text-white"
>
  <span className="material-symbols-outlined">
    forum
  </span>

  <span className="text-sm font-medium">
    Citizen Issues
  </span>
</Link>

        <Link
          href="#"
          className="flex items-center gap-3 px-6 py-3 text-[#748696] transition-all hover:bg-white/5 hover:text-white"
        >
          <span className="material-symbols-outlined">
            settings
          </span>

          <span className="text-sm font-medium">
            Settings
          </span>
        </Link>
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
            href="#"
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