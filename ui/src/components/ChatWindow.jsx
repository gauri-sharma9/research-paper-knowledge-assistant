import { useState, useRef, useEffect } from "react";
import { queryQuestion } from "../api";
import MessageBubble from "./MessageBubble";

export default function ChatWindow({ uploadedFiles, messages, setMessages }) {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef();
  const hasDocuments = uploadedFiles.length > 0;

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleSubmit(e) {
    e.preventDefault();
    const q = input.trim();
    if (!q || loading || !hasDocuments) return;

    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: q }]);
    setLoading(true);

    // Add thinking placeholder
    setMessages((prev) => [...prev, { role: "assistant", loading: true, content: "" }]);

    try {
      const data = await queryQuestion(q);
      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          role: "assistant",
          content: data.answer,
          sources: data.sources,
          loading: false,
        };
        return updated;
      });
    } catch (e) {
      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          role: "assistant",
          content: e?.response?.data?.detail || "Something went wrong. Please try again.",
          sources: [],
          loading: false,
          error: true,
        };
        return updated;
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto px-6 py-6 scrollbar-thin">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center gap-3 select-none">
            <div className="w-12 h-12 rounded-full border border-white/10 flex items-center justify-center">
              <svg className="w-5 h-5 text-white/20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                  d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                />
              </svg>
            </div>
            <p className="text-white/20 text-sm font-mono tracking-wider">
              {hasDocuments ? "Ask a question about your papers" : "Upload a paper to begin"}
            </p>
          </div>
        ) : (
          messages.map((msg, i) => <MessageBubble key={i} message={msg} />)
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input area */}
      <div className="border-t border-white/8 px-6 py-4">
        <form onSubmit={handleSubmit} className="relative">
          <div className="relative group">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={!hasDocuments || loading}
              placeholder={hasDocuments ? "Ask anything about your papers..." : "Upload a paper first"}
              title={!hasDocuments ? "Upload a paper first" : ""}
              className={`w-full bg-white/[0.04] border rounded-xl px-5 py-3.5 pr-14 text-sm text-[#F5F5F5] placeholder:text-white/25 outline-none transition-all duration-200
                ${hasDocuments
                  ? "border-white/10 focus:border-[#6C63FF]/50 focus:bg-white/[0.06]"
                  : "border-white/5 cursor-not-allowed opacity-50"
                }`}
            />
            <button
              type="submit"
              disabled={!hasDocuments || loading || !input.trim()}
              className="absolute right-3 top-1/2 -translate-y-1/2 w-8 h-8 rounded-lg bg-[#6C63FF]/80 hover:bg-[#6C63FF] disabled:bg-white/10 disabled:cursor-not-allowed flex items-center justify-center transition-all duration-200"
            >
              <svg className="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M12 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
