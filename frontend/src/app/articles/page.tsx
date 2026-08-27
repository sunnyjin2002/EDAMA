import { getArticles } from "@/lib/api";
import Link from "next/link";

export const dynamic = "force-dynamic";

function typeLabel(sourceType: string) {
  if (sourceType === "official_news") return "GalNet";
  if (sourceType === "community_goal") return "Community Goal";
  return sourceType;
}

function formatEliteDate(value: string | null) {
  if (!value) return "Unknown Date";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  const month = date.toLocaleString("en-GB", { month: "short", timeZone: "UTC" }).toUpperCase();
  const day = String(date.getUTCDate()).padStart(2, "0");
  const year = date.getUTCFullYear();
  return `${year} ${month} ${day}`;
}

export default async function ArticleArchivePage({ searchParams }: { searchParams: Promise<{ type?: string }> }) {
  const { type } = await searchParams;
  const data = await getArticles(type);

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-2">Article Archive</h1>
      <p className="text-gray-400 mb-6">Browse all source articles, newest first.</p>

      <div className="flex gap-3 mb-6">
        <Link
          href="/articles?type=galnet"
          className={`px-4 py-2 rounded text-sm border transition-colors ${
            type === "galnet"
              ? "bg-ed-orange/10 text-ed-orange border-ed-orange/40"
              : "bg-ed-panel text-gray-400 border-ed-border hover:text-white hover:border-gray-600"
          }`}
        >
          GalNet Articles
        </Link>
        <Link
          href="/articles?type=community_goal"
          className={`px-4 py-2 rounded text-sm border transition-colors ${
            type === "community_goal"
              ? "bg-ed-orange/10 text-ed-orange border-ed-orange/40"
              : "bg-ed-panel text-gray-400 border-ed-border hover:text-white hover:border-gray-600"
          }`}
        >
          Community Goals
        </Link>
      </div>

      {data.articles.length === 0 ? (
        <p className="text-gray-500">No articles found.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {data.articles.map((article) => (
            <Link
              key={article.id}
              href={`/articles/${article.slug || article.id}`}
              className="block bg-ed-panel border border-ed-border rounded-lg p-4 hover:border-ed-orange transition-colors min-w-0"
            >
              <div className="flex items-start justify-between gap-4">
                <h2 className="text-white font-semibold text-sm leading-snug">{article.source_title}</h2>
                <span className="text-xs px-2 py-0.5 rounded border bg-blue-900/30 text-blue-300 border-blue-700 shrink-0">
                  {typeLabel(article.source_type)}
                </span>
              </div>
              <p className="text-gray-500 text-xs mt-2">{formatEliteDate(article.published_at_source)}</p>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
