import { getTranslationMemory } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function TranslationMemoryPage({ searchParams }: { searchParams: Promise<{ q?: string }> }) {
  const { q } = await searchParams;
  const data = await getTranslationMemory(q);

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-4">Translation Memory</h1>
      <form className="mb-4">
        <input
          name="q"
          defaultValue={q || ""}
          placeholder="Search source text..."
          className="w-full max-w-md px-3 py-2 bg-ed-panel border border-ed-border rounded text-white text-sm focus:outline-none focus:border-ed-orange"
        />
      </form>
      {data.entries.length === 0 ? (
        <p className="text-gray-500">{q ? "No results." : "No translation memory entries yet."}</p>
      ) : (
        <div className="space-y-3">
          {data.entries.map((entry) => (
            <div key={entry.id} className="bg-ed-panel border border-ed-border rounded-lg p-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-500 text-xs uppercase mb-1">Source</p>
                  <p className="text-gray-300">{entry.source_text}</p>
                </div>
                <div>
                  <p className="text-gray-500 text-xs uppercase mb-1">Translated</p>
                  <p className="text-ed-orange">{entry.translated_text}</p>
                </div>
              </div>
              {entry.source_reference && <p className="text-gray-600 text-xs mt-2">Ref: {entry.source_reference}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
