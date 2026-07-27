export function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    pending: "bg-yellow-900/50 text-yellow-300 border-yellow-700",
    queued: "bg-blue-900/50 text-blue-300 border-blue-700",
    ready_for_translation: "bg-indigo-900/50 text-indigo-300 border-indigo-700",
    running: "bg-cyan-900/50 text-cyan-300 border-cyan-700",
    succeeded: "bg-green-900/50 text-green-300 border-green-700",
    failed: "bg-red-900/50 text-red-300 border-red-700",
    cancelled: "bg-gray-800 text-gray-400 border-gray-600",
  };

  return (
    <span className={`inline-block px-2 py-0.5 text-xs font-medium rounded border ${colors[status] || colors.pending}`}>
      {status}
    </span>
  );
}
