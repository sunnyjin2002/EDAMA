import Link from "next/link";

export default function ChatPage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
      <h1 className="text-3xl font-bold text-white mb-3">Chat</h1>
      <p className="text-gray-400 max-w-md mb-6">
        Ask anything about the Elite Dangerous universe.
        Powered by RAG and custom tools — coming soon.
      </p>
      <div className="flex gap-4">
        <Link
          href="/translator"
          className="px-4 py-2 bg-ed-panel border border-ed-border rounded text-sm text-gray-400 hover:text-white hover:border-ed-orange transition-colors"
        >
          Go to ED Translator
        </Link>
        <Link
          href="/tools"
          className="px-4 py-2 bg-ed-panel border border-ed-border rounded text-sm text-gray-400 hover:text-white hover:border-ed-orange transition-colors"
        >
          Tools and Guides
        </Link>
      </div>
    </div>
  );
}
