"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Home,
  PlusCircle,
  MessageSquare,
  User,
} from "lucide-react";

export default function BottomNav() {
  const pathname = usePathname();

  const items = [
    {
      name: "Home",
      href: "/citizen/dashboard",
      icon: Home,
    },
    {
      name: "New Issue",
      href: "/citizen/new-issue",
      icon: PlusCircle,
    },
    {
      name: "Feedback",
      href: "/citizen/feedback",
      icon: MessageSquare,
    },
    {
      name: "Profile",
      href: "/citizen/profile",
      icon: User,
    },
  ];

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 border-t border-gray-200 bg-white/95 backdrop-blur-xl md:hidden">
      <div className="grid grid-cols-4">

        {items.map((item) => {
          const Icon = item.icon;
          const active = pathname === item.href;

          return (
            <Link
              key={item.name}
              href={item.href}
              className="flex flex-col items-center justify-center py-3"
            >
              <div
                className={`rounded-full p-2 transition-all ${
                  active
                    ? "bg-[#b5d0fd] text-[#2d486d]"
                    : "text-gray-500"
                }`}
              >
                <Icon size={20} />
              </div>

              <span
                className={`mt-1 text-[11px] ${
                  active
                    ? "font-semibold text-[#2d486d]"
                    : "text-gray-500"
                }`}
              >
                {item.name}
              </span>
            </Link>
          );
        })}

      </div>
    </nav>
  );
}