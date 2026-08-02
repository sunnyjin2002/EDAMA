"use client";

import { getSettings, updateSettings, type SettingsResponse } from "@/lib/api";
import { useEffect, useState } from "react";

const PROVIDERS = ["openai", "deepseek", "gemini", "qwen", "anthropic"] as const;

const PROVIDER_MODELS: Record<string, string[]> = {
  openai: ["gpt-4o-mini", "gpt-4o", "gpt-4.1"],
  deepseek: ["deepseek-chat", "deepseek-reasoner"],
  deepseek: ["deepseek-v4-flash", "deepseek-v4-pro"],
  gemini: ["gemini-2.5-flash", "gemini-2.5-pro"],
  qwen: ["qwen-max", "qwen-plus", "qwen-turbo"],
  anthropic: ["claude-3.5-sonnet", "claude-3.5-haiku", "claude-4-sonnet"],
};

function getModels(provider: string): string[] {
  return PROVIDER_MODELS[provider] ?? [];
}

interface SelectFieldProps {
  label: string;
  value: string;
  options: string[];
  onChange: (v: string) => void;
}

function SelectField({ label, value, options, onChange }: SelectFieldProps) {
  return (
    <div>
      <label className="block text-sm text-gray-400 mb-1">{label}</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full px-3 py-2 bg-ed-panel border border-ed-border rounded text-white text-sm focus:outline-none focus:border-ed-orange"
      >
        {options.map((opt) => (
          <option key={opt} value={opt}>{opt}</option>
        ))}
      </select>
    </div>
  );
}

export default function SettingsPage() {
  const [settings, setSettings] = useState<SettingsResponse | null>(null);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState("");

  useEffect(() => {
    getSettings().then(setSettings).catch(() => setMsg("Failed to load settings"));
  }, []);

  if (!settings) return <p className="text-gray-400">Loading…</p>;

  const set = (key: keyof SettingsResponse, val: string | number | boolean) => {
    setSettings({ ...settings, [key]: val });
  };

  const handleSave = async () => {
    setSaving(true);
    setMsg("");
    try {
      const updated = await updateSettings(settings);
      setSettings(updated);
      setMsg("Saved.");
    } catch {
      setMsg("Save failed.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-4">Settings</h1>
      <div className="max-w-2xl space-y-6">
        {/* Provider selection */}
        <section className="bg-ed-panel border border-ed-border rounded-lg p-4">
          <h2 className="text-sm font-semibold text-gray-400 uppercase mb-3">LLM Providers</h2>
          <div className="grid grid-cols-2 gap-4">
            <SelectField label="Translation Provider" value={settings.translation_provider} options={PROVIDERS} onChange={(v) => set("translation_provider", v)} />
            <SelectField label="Translation Model" value={settings.translation_model} options={getModels(settings.translation_provider)} onChange={(v) => set("translation_model", v)} />
            <SelectField label="Review Provider" value={settings.review_provider} options={PROVIDERS} onChange={(v) => set("review_provider", v)} />
            <SelectField label="Review Model" value={settings.review_model} options={getModels(settings.review_provider)} onChange={(v) => set("review_model", v)} />
            <SelectField label="Tagging Provider" value={settings.tagging_provider} options={PROVIDERS} onChange={(v) => set("tagging_provider", v)} />
            <SelectField label="Tagging Model" value={settings.tagging_model} options={getModels(settings.tagging_provider)} onChange={(v) => set("tagging_model", v)} />
          </div>
        </section>

        {/* Polling */}
        {/* Polling section — bring back InputField inline since it was removed */}
        <section className="bg-ed-panel border border-ed-border rounded-lg p-4">
          <h2 className="text-sm font-semibold text-gray-400 uppercase mb-3">Source Polling</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1">Source Poll URL</label>
              <input
                type="text"
                value={settings.source_poll_url ?? ""}
                onChange={(e) => set("source_poll_url", e.target.value || null as unknown as string)}
                className="w-full px-3 py-2 bg-ed-panel border border-ed-border rounded text-white text-sm focus:outline-none focus:border-ed-orange"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Poll Interval (minutes)</label>
              <input
                type="text"
                value={String(settings.source_poll_interval_minutes)}
                onChange={(e) => set("source_poll_interval_minutes", Number(e.target.value) || 30)}
                className="w-full px-3 py-2 bg-ed-panel border border-ed-border rounded text-white text-sm focus:outline-none focus:border-ed-orange"
              />
            </div>
          </div>
          <div className="mt-3">
            <label className="flex items-center gap-2 text-sm text-gray-400">
              <input
                type="checkbox"
                checked={settings.auto_publish_official_news}
                onChange={(e) => set("auto_publish_official_news", e.target.checked)}
                className="rounded bg-ed-panel border-ed-border"
              />
              Auto-publish official news
            </label>
          </div>
        </section>

        {/* Translator */}
        <section className="bg-ed-panel border border-ed-border rounded-lg p-4">
          <h2 className="text-sm font-semibold text-gray-400 uppercase mb-3">Translator</h2>
          <label className="flex items-center gap-2 text-sm text-gray-400">
            <input
              type="checkbox"
              checked={settings.translation_review_enabled}
              onChange={(e) => set("translation_review_enabled", e.target.checked)}
              className="rounded bg-ed-panel border-ed-border"
            />
            LLM Translation Review Service
          </label>
        </section>

        <div className="flex items-center gap-3">
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-5 py-2 bg-ed-orange text-white rounded text-sm font-medium hover:bg-orange-600 disabled:opacity-50 transition-colors"
          >
            {saving ? "Saving…" : "Save"}
          </button>
          {msg && <span className={`text-sm ${msg === "Saved." ? "text-green-400" : "text-red-400"}`}>{msg}</span>}
        </div>
      </div>
    </div>
  );
}
