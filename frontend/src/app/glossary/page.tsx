import { getGlossary } from "@/lib/api";
import { revalidatePath } from "next/cache";

export const dynamic = "force-dynamic";

async function handleReload() {
  "use server";
  await fetch("http://localhost:3312/glossary/reload", { method: "POST" });
  revalidatePath("/glossary");
}

export default async function GlossaryPage({ searchParams }: { searchParams: Promise<{ q?: string }> }) {
  const { q } = await searchParams;
  const data = await getGlossary(q);

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold text-white">Glossary</h1>
        <form action={handleReload}>
          <button
            type="submit"
            className="px-3 py-1.5 text-xs bg-ed-border text-gray-400 rounded hover:bg-gray-700 hover:text-white transition-colors"
          >
            Reload from files
          </button>
        </form>
      </div>
      <form className="mb-4">
        <input
          name="q"
          defaultValue={q || ""}
          placeholder="Search terms..."
          className="w-full max-w-md px-3 py-2 bg-ed-panel border border-ed-border rounded text-white text-sm focus:outline-none focus:border-ed-orange"
        />
      </form>
      {data.entries.length === 0 ? (
        <p className="text-gray-500">{q ? "No results." : "No glossary entries yet."}</p>
      ) : (
        <div className="bg-ed-panel border border-ed-border rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b border-ed-border">
                <th className="p-3">English</th>
                <th className="p-3">中文</th>
                <th className="p-3">Type</th>
                <th className="p-3">Status</th>
              </tr>
            </thead>
            <tbody>
              {data.entries.map((entry) => (
                <tr key={entry.id} className="border-b border-ed-border/50">
                  <td className="p-3 text-white">{entry.source_term_en}</td>
                  <td className="p-3 text-ed-orange">{entry.approved_term_zh}</td>
                  <td className="p-3 text-gray-500">{entry.entity_type || "-"}</td>
                  <td className="p-3 text-gray-500 text-xs">{entry.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
