"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

export type ManualSubmissionState = {
  error?: string;
};

export async function submitArticle(
  _previousState: ManualSubmissionState,
  formData: FormData,
): Promise<ManualSubmissionState> {
  const title = formData.get("title") as string;
  const source_url = formData.get("source_url") as string;
  const source_text = formData.get("source_text") as string;
  const target_language = (formData.get("target_language") as string) || "zh-CN";

  if (!source_text.trim()) {
    return { error: "Source text is required." };
  }

  const res = await fetch("http://localhost:3312/articles/manual", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      title: title.trim() || null,
      source_url: source_url.trim() || null,
      source_text: source_text.trim(),
      target_language,
    }),
  });

  if (!res.ok) {
    const detail = await res.text();
    return { error: detail || `Backend request failed with status ${res.status}.` };
  }

  const data = await res.json();
  revalidatePath("/");
  revalidatePath("/jobs");
  redirect(`/jobs/${data.job.id}`);
}
