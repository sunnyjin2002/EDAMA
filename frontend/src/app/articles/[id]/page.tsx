import { getArticle } from "@/lib/api";
import { StatusBadge } from "@/components/StatusBadge";
import Link from "next/link";

export const dynamic = "force-dynamic";

export default async function ArticleDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const article = await getArticle(Number(id));

  return (
    <div>
      <Link href="/" className="text-ed-orange hover:underline text-sm">&larr; Dashboard</Link>
      <h1 className="text-2xl font-bold text-white mt-2 mb-1">{article.source_title}</h1>
      <p className="text-gray-500 text-sm mb-4">Type: {article.source_type} | Created: {new Date(article.created_at).toLocaleString()}</p>
      {article.source_url && (
        <p className="text-gray-500 text-sm mb-4">Source: <a href={article.source_url} className="text-ed-orange hover:underline">{article.source_url}</a></p>
      )}

      <div className="bg-ed-panel border border-ed-border rounded-lg p-4 mb-6">
        <h2 className="text-sm font-semibold text-gray-400 uppercase mb-2">Source Text</h2>
        <pre className="text-sm text-gray-300 whitespace-pre-wrap font-sans">{article.source_body}</pre>
      </div>

      {article.jobs.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold text-white mb-3">Jobs</h2>
          <div className="space-y-2">
            {article.jobs.map((job) => (
              <Link key={job.id} href={`/jobs/${job.id}`} className="block bg-ed-panel border border-ed-border rounded-lg p-3 hover:border-ed-orange transition-colors">
                <div className="flex items-center gap-3">
                  <span className="text-ed-orange text-sm">#{job.id}</span>
                  <span className="text-gray-300 text-sm">{job.job_type}</span>
                  <StatusBadge status={job.status} />
                  <span className="text-gray-500 text-xs ml-auto">{job.target_language}</span>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
