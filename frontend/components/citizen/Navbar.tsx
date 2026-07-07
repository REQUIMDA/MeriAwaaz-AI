"use client";

import { useState, useRef, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  Landmark,
  Bell,
  UserCircle,
  LogOut,
  ChevronDown,
} from "lucide-react";

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();

  const [open, setOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);

    return () => {
      document.removeEventListener(
        "mousedown",
        handleClickOutside
      );
    };
  }, []);

  const navItems = [
    {
      label: "Home",
      href: "/citizen/dashboard",
    },
    {
      label: "About",
      href: "/citizen/about",
    },
  ];

  return (
    <header className="sticky top-0 z-50 border-b border-gray-200/70 bg-white/80 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">

        {/* Logo */}

        <Link
          href="/citizen/dashboard"
          className="flex items-center gap-3"
        >
          <Landmark
            size={28}
            className="text-black"
          />

          <span className="text-xl font-semibold tracking-tight">
            MeriAwaaz AI
          </span>
        </Link>

        {/* Navigation */}

        <nav className="hidden items-center gap-10 md:flex">
          {navItems.map((item) => {
            const active = pathname === item.href;

            return (
              <Link
                key={item.href}
                href={item.href}
                className={`relative pb-1 text-sm font-medium transition ${
                  active
                    ? "text-black"
                    : "text-gray-500 hover:text-black"
                }`}
              >
                {item.label}

                {active && (
                  <span className="absolute bottom-0 left-0 h-[2px] w-full rounded-full bg-black" />
                )}
              </Link>
            );
          })}
        </nav>

        {/* Right */}

        <div className="flex items-center gap-5">

          <button className="transition hover:scale-110">
            <Bell
              size={20}
              className="text-gray-600"
            />
          </button>

          {/* Profile Dropdown */}

          <div
            className="relative"
            ref={dropdownRef}
          >
            <button
              onClick={() => setOpen(!open)}
              className="flex items-center gap-1 rounded-full transition hover:scale-105"
            >
              <UserCircle
                size={32}
                className="text-gray-700"
              />

              <ChevronDown
                size={16}
                className={`transition-transform ${
                  open ? "rotate-180" : ""
                }`}
              />
            </button>

            {open && (
              <div className="absolute right-0 mt-3 w-52 overflow-hidden rounded-xl border border-gray-200 bg-white shadow-xl">

                <button
                  onClick={() => {
                    setOpen(false);
                    router.push("/");
                  }}
                  className="flex w-full items-center gap-3 px-5 py-4 text-left transition hover:bg-red-50 hover:text-red-600"
                >
                  <LogOut size={18} />

                  <span className="font-medium">
                    Logout
                  </span>
                </button>

              </div>
            )}

          </div>

        </div>

      </div>
    </header>
  );
}