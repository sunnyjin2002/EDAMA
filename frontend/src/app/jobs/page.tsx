import { getJobs } from "@/lib/api";
import { StatusBadge } from "@/components/StatusBadge";
import Link from "next/link";

export const dynamic = "force-dynamic";

export default async function JobsPage() {
  const jobs = await getJobs();

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-4">Jobs</h1>
      {jobs.length === 0 ? (
        <p className="text-gray-500">No jobs found.</p>
      ) : (
        <div className="bg-ed-panel border border-ed-border rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b border-ed-border">
                <th className="p-3">Job</th>
                <th className="p-3">Article</th>
                <th className="p-3">Status</th>
                <th className="p-3">Target</th>
              </tr>
            </thead>
            <tbody>
              {jobs.map((job) => (
                <tr key={job.id} className="border-b border-ed-border/50">
                  <td className="p-3">
                    <Link href={`/jobs/${job.id}`} className="text-ed-orange hover:underline">
                      #{job.id} {job.job_type}
                    </Link>
                  </td>
                  <td className="p-3 text-gray-400">{job.article?.source_title || "-"}</td>
                  <td className="p-3"><StatusBadge status={job.status} /></td>
                  <td className="p-3 text-gray-500">{job.target_language}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
