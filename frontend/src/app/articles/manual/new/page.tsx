import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

export const dynamic = "force-dynamic";

async function submitArticle(formData: FormData) {
  "use server";
  const title = formData.get("title") as string;
  const source_url = formData.get("source_url") as string;
  const source_text = formData.get("source_text") as string;
  const target_language = (formData.get("target_language") as string) || "zh-CN";

  if (!source_text) {
    return { error: "Source text is required." };
  }

  const res = await fetch("http://localhost:3312/articles/manual", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title: title || null, source_url: source_url || null, source_text, target_language }),
  });

  if (!res.ok) {
    const detail = await res.text();
    return { error: detail };
  }

  const data = await res.json();
  revalidatePath("/");
  revalidatePath("/jobs");
  redirect(`/jobs/${data.job.id}`);
}

export default function ManualSubmitPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-4">Manual Lore Submission</h1>
      <form action={submitArticle} className="max-w-2xl space-y-4">
        <div>
          <label className="block text-sm text-gray-400 mb-1">Title</label>
          <input
            name="title"
            className="w-full px-3 py-2 bg-ed-panel border border-ed-border rounded text-white text-sm focus:outline-none focus:border-ed-orange"
            placeholder="Optional — derived from first line if empty"
          />
        </div>
        <div>
          <label className="block text-sm text-gray-400 mb-1">Source URL</label>
          <input
            name="source_url"
            className="w-full px-3 py-2 bg-ed-panel border border-ed-border rounded text-white text-sm focus:outline-none focus:border-ed-orange"
            placeholder="Optional"
          />
        </div>
        <div>
          <label className="block text-sm text-gray-400 mb-1">Source Text *</label>
          <textarea
            name="source_text"
            rows={8}
            required
            className="w-full px-3 py-2 bg-ed-panel border border-ed-border rounded text-white text-sm focus:outline-none focus:border-ed-orange"
            placeholder="Paste Elite Dangerous lore text here..."
          />
        </div>
        <div>
          <label className="block text-sm text-gray-400 mb-1">Target Language</label>
          <input
            name="target_language"
            defaultValue="zh-CN"
            className="w-32 px-3 py-2 bg-ed-panel border border-ed-border rounded text-white text-sm focus:outline-none focus:border-ed-orange"
          />
        </div>
        <button
          type="submit"
          className="px-5 py-2 bg-ed-orange text-white rounded text-sm font-medium hover:bg-orange-600 transition-colors"
        >
          Submit
        </button>
      </form>
    </div>
  );
}
