const API_BASE = "http://localhost:3312";

async function fetchJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) {
    throw new Error(`API error ${res.status}: ${res.statusText}`);
  }
  return res.json();
}

export interface JobSummary {
  id: number;
  article_id: number;
  job_type: string;
  status: string;
  target_language: string;
  error_message: string | null;
  created_at: string;
  article: { id: number; source_title: string; source_type: string } | null;
}

export interface JobDetail extends JobSummary {
  logs: { id: number; stage: string; message: string; created_at: string }[];
}

export interface DashboardResponse {
  app_name: string;
  recent_jobs: JobSummary[];
}

export interface ArticleDetail {
  id: number;
  source_type: string;
  source_url: string | null;
  source_title: string;
  source_body: string;
  created_at: string;
  jobs: JobDetail[];
}

export interface GlossaryEntry {
  id: number;
  source_term_en: string;
  approved_term_zh: string;
  aliases_en: string | null;
  entity_type: string | null;
  notes: string | null;
  status: string;
  created_at: string;
}

export interface GlossaryListResponse {
  entries: GlossaryEntry[];
  query: string;
}

export interface TranslationMemoryEntry {
  id: number;
  source_text: string;
  translated_text: string;
  source_reference: string | null;
  tags: string | null;
  created_at: string;
}

export interface TranslationMemoryListResponse {
  entries: TranslationMemoryEntry[];
  matches: TranslationMemoryEntry[];
  query: string;
}

export async function getDashboard(): Promise<DashboardResponse> {
  return fetchJSON<DashboardResponse>("/");
}

export async function getJobs(): Promise<JobSummary[]> {
  return fetchJSON<JobSummary[]>("/jobs");
}

export async function getJob(id: number): Promise<JobDetail> {
  return fetchJSON<JobDetail>(`/jobs/${id}`);
}

export async function getGlossary(query?: string): Promise<GlossaryListResponse> {
  const qs = query ? `?q=${encodeURIComponent(query)}` : "";
  return fetchJSON<GlossaryListResponse>(`/glossary${qs}`);
}

export async function getTranslationMemory(query?: string): Promise<TranslationMemoryListResponse> {
  const qs = query ? `?q=${encodeURIComponent(query)}` : "";
  return fetchJSON<TranslationMemoryListResponse>(`/translation-memory${qs}`);
}

export async function getArticle(id: number): Promise<ArticleDetail> {
  return fetchJSON<ArticleDetail>(`/articles/${id}`);
}

export async function getSettings(): Promise<{ status: string }> {
  return fetchJSON<{ status: string }>("/settings");
}

export async function reloadGlossary(): Promise<{ message: string; inserted: number; updated: number }> {
  const res = await fetch(`${API_BASE}/glossary/reload`, { method: "POST" });
  if (!res.ok) {
    throw new Error(`Reload failed: ${res.status}`);
  }
  return res.json();
}
