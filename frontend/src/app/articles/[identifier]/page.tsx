import { getArticle } from "@/lib/api";
import ArticleTranslations from "@/components/ArticleTranslations";

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

export default async function ArticleDetailPage({ params }: { params: Promise<{ identifier: string }> }) {
  const { identifier } = await params;
  const article = await getArticle(identifier);

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mt-2 mb-1">{article.source_title}</h1>
      <p className="text-gray-500 text-sm mb-4">
        {typeLabel(article.source_type)} | {formatEliteDate(article.published_at_source)}
      </p>
      {article.source_url && (
        <p className="text-gray-500 text-sm mb-4">
          Source: <a href={article.source_url} className="text-ed-orange hover:underline">{article.source_url}</a>
        </p>
      )}

      <div className="bg-ed-panel border border-ed-border rounded-lg p-4 mb-6">
        <h2 className="text-sm font-semibold text-gray-400 uppercase mb-2">Source Text</h2>
        <pre className="text-sm text-gray-300 whitespace-pre-wrap font-sans">{article.source_body}</pre>
      </div>

      <ArticleTranslations translations={article.translations} />
    </div>
  );
}