import type { Metadata } from "next";
import "./globals.css";
import Link from "next/link";

export const metadata: Metadata = {
  title: "EDAMA",
  description: "Elite Dangerous Ask Me Anything",
};

const navLinks = [
  { href: "/", label: "Dashboard" },
  { href: "/jobs", label: "Jobs" },
  { href: "/glossary", label: "Glossary" },
  { href: "/translation-memory", label: "Translation Memory" },
  { href: "/articles/manual/new", label: "Submit" },
  { href: "/settings", label: "Settings" },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body suppressHydrationWarning>
        <nav className="bg-ed-panel border-b border-ed-border">
          <div className="max-w-7xl mx-auto px-4 py-3 flex gap-6 items-center">
            <Link href="/" className="text-ed-orange font-bold text-lg tracking-tight">
              EDAMA
            </Link>
            <div className="flex gap-4 text-sm text-gray-400">
              {navLinks.map((link) => (
                <Link key={link.href} href={link.href} className="hover:text-white transition-colors">
                  {link.label}
                </Link>
              ))}
            </div>
          </div>
        </nav>
        <main className="max-w-7xl mx-auto px-4 py-6">{children}</main>
      </body>
    </html>
  );
}
