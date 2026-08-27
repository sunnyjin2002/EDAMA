"use client";

import { useState } from "react";
import type { ArticleTranslation } from "@/lib/api";

function formatEliteDate(value: string | null) {
  if (!value) return "Unknown Date";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  const month = date.toLocaleString("en-GB", { month: "short", timeZone: "UTC" }).toUpperCase();
  const day = String(date.getUTCDate()).padStart(2, "0");
  const year = date.getUTCFullYear();
  return `${year} ${month} ${day}`;
}

export default function ArticleTranslations({ translations }: { translations: ArticleTranslation[] }) {
  const [language, setLanguage] = useState(translations[0]?.language || "zh-CN");
  const current = translations.find((t) => t.language === language) || translations[0];

  if (!current) {
    return <p className="text-gray-500 text-sm">No translations yet.</p>;
  }

  return (
    <div className="bg-ed-panel border border-ed-border rounded-lg p-4">
      <div className="flex items-center justify-between gap-4 mb-3">
        <h2 className="text-lg font-semibold text-white">Translations</h2>
        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          className="px-3 py-2 bg-ed-panel border border-ed-border rounded text-white text-sm focus:outline-none focus:border-ed-orange"
        >
          {translations.map((t) => (
            <option key={t.language} value={t.language}>{t.language}</option>
          ))}
        </select>
      </div>
      <div className="bg-ed-panel border border-ed-border rounded-lg p-3 mb-3">
        <h3 className="text-white font-medium mb-1">{current.translated_title || "Translation"}</h3>
        <p className="text-gray-300 text-sm whitespace-pre-wrap">{current.translated_body || "No translated passage yet."}</p>
      </div>
      {current.reviewed_body && (
        <div className="bg-ed-panel border border-ed-orange/30 rounded-lg p-3">
          <h4 className="text-ed-orange text-sm font-semibold uppercase mb-2">Reviewed Translation</h4>
          <h3 className="text-white font-medium mb-1">{current.reviewed_title || current.translated_title}</h3>
          <p className="text-gray-300 text-sm whitespace-pre-wrap">{current.reviewed_body}</p>
          {current.confidence_score != null && (
            <p className="text-green-300 text-xs mt-2">Score: {current.confidence_score.toFixed(2)}</p>
          )}
        </div>
      )}
    </div>
  );
}
