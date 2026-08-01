"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, useRef, type ReactNode } from "react";

interface DropdownItem {
  href: string;
  label: string;
}

interface NavDropdownProps {
  href: string;
  label: string;
  items: DropdownItem[];
}

export function NavDropdown({ href, label, items }: NavDropdownProps) {
  const [open, setOpen] = useState(false);
  const pathname = usePathname();
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const isActive = pathname === href || pathname.startsWith(href + "/");

  const handleEnter = () => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
    setOpen(true);
  };

  const handleLeave = () => {
    timerRef.current = setTimeout(() => setOpen(false), 150);
  };

  return (
    <div
      className="relative"
      onMouseEnter={handleEnter}
      onMouseLeave={handleLeave}
    >
      <Link
        href={href}
        className={`block px-3 py-2 rounded text-sm transition-colors ${
          isActive
            ? "text-ed-orange bg-ed-orange/10"
            : "text-gray-400 hover:text-white"
        }`}
      >
        {label}
      </Link>
      {open && (
        <div className="absolute top-full left-0 mt-1 w-48 bg-ed-panel border border-ed-border rounded-lg shadow-lg z-50 py-1">
          {items.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="block px-4 py-2 text-sm text-gray-400 hover:text-white hover:bg-ed-border/30 transition-colors"
            >
              {item.label}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
