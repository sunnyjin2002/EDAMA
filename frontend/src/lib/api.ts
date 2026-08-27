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
  article: {
    id: number;
    slug: string | null;
    article_header: string | null;
    source_title: string;
    source_type: string;
  } | null;
}

export interface JobDetail extends JobSummary {
  logs: { id: number; stage: string; message: string; created_at: string }[];
  translated_title: string | null;
  translated_body: string | null;
  reviewed_title: string | null;
  reviewed_body: string | null;
  review_notes: string | null;
  confidence_score: number | null;
  tags: string[];
}

export interface DashboardResponse {
  app_name: string;
  recent_jobs: JobSummary[];
}

export interface ArticleTranslation {
  language: string;
  translated_title: string | null;
  translated_body: string | null;
  reviewed_title: string | null;
  reviewed_body: string | null;
  review_notes: string | null;
  confidence_score: number | null;
}

export interface ArticleDetail {
  id: number;
  slug: string | null;
  article_header: string | null;
  source_type: string;
  source_url: string | null;
  source_title: string;
  source_body: string;
  published_at_source: string | null;
  created_at: string;
  jobs: JobDetail[];
  translations: ArticleTranslation[];
}

export interface ArticleArchiveItem {
  id: number;
  slug: string | null;
  article_header: string | null;
  source_type: string;
  source_url: string | null;
  source_title: string;
  published_at_source: string | null;
}

export interface ArticleListResponse {
  articles: ArticleArchiveItem[];
  type: string;
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

export async function translateJob(id: number): Promise<JobDetail> {
  const res = await fetch(`${API_BASE}/jobs/${id}/translate`, { method: "POST" });
  if (!res.ok) throw new Error(`Translate failed: ${res.status}`);
  return res.json();
}

export async function getGlossary(query?: string): Promise<GlossaryListResponse> {
  const qs = query ? `?q=${encodeURIComponent(query)}` : "";
  return fetchJSON<GlossaryListResponse>(`/glossary${qs}`);
}

export async function getTranslationMemory(query?: string): Promise<TranslationMemoryListResponse> {
  const qs = query ? `?q=${encodeURIComponent(query)}` : "";
  return fetchJSON<TranslationMemoryListResponse>(`/translation-memory${qs}`);
}

export async function getArticle(identifier: string): Promise<ArticleDetail> {
  return fetchJSON<ArticleDetail>(`/articles/${encodeURIComponent(identifier)}`);
}

export async function getArticles(type?: string): Promise<ArticleListResponse> {
  const qs = type ? `?type=${encodeURIComponent(type)}` : "";
  return fetchJSON<ArticleListResponse>(`/articles${qs}`);
}

export async function getSettings(): Promise<SettingsResponse> {
  return fetchJSON<SettingsResponse>("/settings");
}

export interface SettingsResponse {
  translation_provider: string;
  translation_model: string;
  review_provider: string;
  review_model: string;
  tagging_provider: string;
  tagging_model: string;
  translation_review_enabled: boolean;
  news_source_type: string;
  news_polling_enabled: boolean;
  source_poll_url: string | null;
  source_poll_interval_minutes: number;
  auto_publish_official_news: boolean;
}

export async function updateSettings(body: Partial<SettingsResponse>): Promise<SettingsResponse> {
  const res = await fetch(`${API_BASE}/settings`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`Settings update failed: ${res.status}`);
  return res.json();
}

export async function reloadGlossary(): Promise<{ message: string; inserted: number; updated: number }> {
  const res = await fetch(`${API_BASE}/glossary/reload`, { method: "POST" });
  if (!res.ok) {
    throw new Error(`Reload failed: ${res.status}`);
  }
  return res.json();
}
