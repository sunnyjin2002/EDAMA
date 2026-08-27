import type { Metadata } from "next";
import "./globals.css";
import Link from "next/link";
import { NavDropdown } from "@/components/NavDropdown";

export const metadata: Metadata = {
  title: "EDAMA",
  description: "Elite Dangerous Ask Me Anything",
};

const translatorItems = [
  { href: "/jobs", label: "Jobs" },
  { href: "/glossary", label: "Glossary" },
  { href: "/translation-memory", label: "Translation Memory" },
  { href: "/articles/manual/new", label: "Submit" },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body suppressHydrationWarning>
        <nav className="bg-ed-panel border-b border-ed-border">
          <div className="max-w-7xl mx-auto px-4 py-3 flex gap-1 items-center">
            <Link
              href="/"
              className="text-ed-orange font-bold text-lg tracking-tight mr-4"
            >
              EDAMA
            </Link>
            <Link
              href="/"
              className="px-3 py-2 rounded text-sm text-gray-400 hover:text-white transition-colors"
            >
              Chat
            </Link>
            <NavDropdown
              href="/translator"
              label="ED Translator"
              items={translatorItems}
            />
            <Link
              href="/articles"
              className="px-3 py-2 rounded text-sm text-gray-400 hover:text-white transition-colors"
            >
              Article Archive
            </Link>
            <Link
              href="/tools"
              className="px-3 py-2 rounded text-sm text-gray-400 hover:text-white transition-colors"
            >
              Tools and Guides
            </Link>
            <Link
              href="/settings"
              className="px-3 py-2 rounded text-sm text-gray-400 hover:text-white transition-colors"
            >
              Settings
            </Link>
          </div>
        </nav>
        <main className="max-w-7xl mx-auto px-4 py-6">{children}</main>
      </body>
    </html>
  );
}
