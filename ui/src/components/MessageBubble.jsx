export default function MessageBubble({ message }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex w-full ${isUser ? "justify-end" : "justify-start"} mb-6`}>
      <div className={`max-w-[72%] ${isUser ? "items-end" : "items-start"} flex flex-col gap-2`}>
        {/* Label */}
        <span className="text-[10px] tracking-[0.2em] uppercase text-white/25 font-mono px-1">
          {isUser ? "You" : "Assistant"}
        </span>

        {/* Bubble */}
        <div
          className={`px-5 py-4 rounded-2xl text-sm leading-relaxed ${
            isUser
              ? "bg-[#6C63FF]/20 border border-[#6C63FF]/30 text-[#F5F5F5] rounded-tr-sm"
              : "bg-white/5 border border-white/10 text-[#E0E0E0] rounded-tl-sm"
          }`}
        >
          {message.loading ? (
            <div className="flex items-center gap-1.5 py-1">
              <span className="w-1.5 h-1.5 rounded-full bg-white/40" style={{ animation: "bounce 1.2s infinite 0s" }} />
              <span className="w-1.5 h-1.5 rounded-full bg-white/40" style={{ animation: "bounce 1.2s infinite 0.2s" }} />
              <span className="w-1.5 h-1.5 rounded-full bg-white/40" style={{ animation: "bounce 1.2s infinite 0.4s" }} />
            </div>
          ) : (
            <p className="whitespace-pre-wrap">{message.content}</p>
          )}
        </div>

        {/* Source tags */}
        {message.sources && message.sources.length > 0 && (
          <div className="flex flex-wrap gap-1.5 px-1">
            {message.sources.map((src, i) => (
              <span
                key={i}
                className="text-[10px] px-2 py-0.5 rounded-full bg-[#4ADE80]/10 border border-[#4ADE80]/25 text-[#4ADE80] font-mono tracking-wide"
              >
                {src}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
