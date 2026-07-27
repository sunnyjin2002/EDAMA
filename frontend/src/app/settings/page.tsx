import { getSettings } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function SettingsPage() {
  const settings = await getSettings();

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-4">Settings</h1>
      <div className="bg-ed-panel border border-ed-border rounded-lg p-4 max-w-xl">
        <p className="text-gray-400 text-sm">{settings.status === "ok" ? "Settings configuration will be available in a future update." : settings.status}</p>
      </div>
    </div>
  );
}
