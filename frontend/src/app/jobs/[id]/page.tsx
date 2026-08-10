import { getJob } from "@/lib/api";
import { StatusBadge } from "@/components/StatusBadge";
import Link from "next/link";

export const dynamic = "force-dynamic";

export default async function JobDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const job = await getJob(Number(id));

  return (
    <div>
      <div className="flex items-center gap-3 mb-4">
        <Link href="/jobs" className="text-ed-orange hover:underline text-sm">&larr; Jobs</Link>
        <h1 className="text-2xl font-bold text-white mr-auto">Job #{job.id}</h1>
        <StatusBadge status={job.status} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        <div className="bg-ed-panel border border-ed-border rounded-lg p-4 min-w-0">
          <h2 className="text-sm font-semibold text-gray-400 uppercase mb-2">Details</h2>
          <dl className="space-y-2 text-sm">
            <div className="flex justify-between gap-4"><dt className="text-gray-500 shrink-0">Type</dt><dd className="text-white truncate">{job.job_type}</dd></div>
            <div className="flex justify-between gap-4"><dt className="text-gray-500 shrink-0">Target</dt><dd className="text-white truncate">{job.target_language}</dd></div>
            <div className="flex justify-between gap-4"><dt className="text-gray-500 shrink-0">Created</dt><dd className="text-white truncate">{new Date(job.created_at).toLocaleString()}</dd></div>
            {job.error_message && <div className="flex justify-between"><dt className="text-gray-500">Error</dt><dd className="text-red-400">{job.error_message}</dd></div>}
          </dl>
        </div>
        {job.article && (
          <div className="bg-ed-panel border border-ed-border rounded-lg p-4 min-w-0">
            <h2 className="text-sm font-semibold text-gray-400 uppercase mb-2">Article</h2>
            <Link href={`/articles/${job.article_id}`} className="text-ed-orange hover:underline text-sm block truncate">
              {job.article.source_title}
            </Link>
            <p className="text-gray-500 text-xs mt-1">Type: {job.article.source_type}</p>
          </div>
        )}
      </div>

      {job.translated_body && (
        <div className="bg-ed-panel border border-ed-border rounded-lg p-4 mb-6">
          <h2 className="text-sm font-semibold text-gray-400 uppercase mb-3">First-Pass Translation</h2>
          <h3 className="text-white font-medium mb-2">{job.translated_title}</h3>
          <p className="text-gray-300 text-sm whitespace-pre-wrap">{job.translated_body}</p>
        </div>
      )}

      {job.reviewed_body && (
        <div className="bg-ed-panel border border-ed-orange/30 rounded-lg p-4 mb-6">
          <div className="flex items-center gap-3 mb-3">
            <h2 className="text-sm font-semibold text-ed-orange uppercase">Reviewed Translation</h2>
            {job.confidence_score != null && (
              <span className="px-2 py-0.5 text-xs rounded bg-green-900/30 text-green-300 border border-green-700">
                Score: {job.confidence_score.toFixed(2)}
              </span>
            )}
          </div>
          <h3 className="text-white font-medium mb-2">{job.reviewed_title || job.translated_title}</h3>
          <p className="text-gray-300 text-sm whitespace-pre-wrap">{job.reviewed_body}</p>
          {job.review_notes && (
            <p className="text-gray-500 text-xs mt-3 border-t border-ed-border/30 pt-2">{job.review_notes}</p>
          )}
        </div>
      )}

      {job.tags && job.tags.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mb-6">
          {job.tags.map((tag) => (
            <span key={tag} className="inline-block px-2 py-1 text-xs rounded bg-ed-orange/10 text-ed-orange border border-ed-orange/30">
              {tag}
            </span>
          ))}
        </div>
      )}

      {job.logs.length > 0 && (
        <div className="bg-ed-panel border border-ed-border rounded-lg p-4">
          <h2 className="text-sm font-semibold text-gray-400 uppercase mb-3">Logs</h2>
          <div className="space-y-2">
            {job.logs.map((log) => (
              <div key={log.id} className="flex gap-3 text-sm border-b border-ed-border/30 pb-2">
                <span className="text-ed-orange font-mono text-xs w-24 shrink-0">{log.stage}</span>
                <span className="text-gray-300">{log.message}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
