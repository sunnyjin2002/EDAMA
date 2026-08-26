"use client";

import { useActionState } from "react";
import { submitArticle, type ManualSubmissionState } from "./actions";

const initialState: ManualSubmissionState = {};

export default function ManualSubmitPage() {
  const [state, formAction, isPending] = useActionState(submitArticle, initialState);

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-4">Manual Lore Submission</h1>
      <form action={formAction} className="max-w-2xl space-y-4">
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

        {state.error && <p className="text-sm text-red-400">{state.error}</p>}

        <button
          type="submit"
          disabled={isPending}
          className="px-5 py-2 bg-ed-orange text-white rounded text-sm font-medium hover:bg-orange-600 disabled:opacity-50 transition-colors"
        >
          {isPending ? "Submitting..." : "Submit"}
        </button>
      </form>
    </div>
  );
}
