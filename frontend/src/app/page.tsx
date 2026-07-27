import { getDashboard } from "@/lib/api";
import { StatusBadge } from "@/components/StatusBadge";
import Link from "next/link";

export const dynamic = "force-dynamic";

export default async function DashboardPage() {
  const data = await getDashboard();

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-2">{data.app_name}</h1>
      <p className="text-gray-400 mb-6">Elite Dangerous lore translation & knowledge system</p>

      <div className="grid grid-cols-3 gap-4 mb-8">
        {[
          { label: "Manual Submit", href: "/articles/manual/new" },
          { label: "Jobs", href: "/jobs" },
          { label: "Glossary", href: "/glossary" },
          { label: "Translation Memory", href: "/translation-memory" },
          { label: "Settings", href: "/settings" },
        ].map((tile) => (
          <Link
            key={tile.href}
            href={tile.href}
            className="block p-4 bg-ed-panel border border-ed-border rounded-lg text-gray-300 hover:border-ed-orange hover:text-white transition-colors"
          >
            {tile.label}
          </Link>
        ))}
      </div>

      <div className="bg-ed-panel border border-ed-border rounded-lg p-4">
        <div className="flex justify-between items-center mb-3">
          <h2 className="text-lg font-semibold text-white">Recent Jobs</h2>
          <Link href="/jobs" className="text-sm text-ed-orange hover:underline">View all</Link>
        </div>
        {data.recent_jobs.length === 0 ? (
          <p className="text-gray-500">No jobs yet. Submit a lore draft to get started.</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b border-ed-border">
                <th className="pb-2">Job</th>
                <th className="pb-2">Article</th>
                <th className="pb-2">Status</th>
                <th className="pb-2">Target</th>
              </tr>
            </thead>
            <tbody>
              {data.recent_jobs.map((job) => (
                <tr key={job.id} className="border-b border-ed-border/50">
                  <td className="py-2">
                    <Link href={`/jobs/${job.id}`} className="text-ed-orange hover:underline">
                      #{job.id} {job.job_type}
                    </Link>
                  </td>
                  <td className="py-2 text-gray-400">{job.article?.source_title || "-"}</td>
                  <td className="py-2"><StatusBadge status={job.status} /></td>
                  <td className="py-2 text-gray-500">{job.target_language}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
