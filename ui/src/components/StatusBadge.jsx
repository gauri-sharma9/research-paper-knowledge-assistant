export default function StatusBadge({ health }) {
  const isOk = health?.status === "ok";

  return (
    <div className="flex items-center gap-2 px-3 py-1.5 rounded-full border border-white/10 bg-white/5 backdrop-blur-sm">
      <span
        className={`w-2 h-2 rounded-full ${
          isOk ? "bg-[#4ADE80] shadow-[0_0_6px_#4ADE80]" : "bg-red-500 shadow-[0_0_6px_#ef4444]"
        }`}
        style={{ animation: isOk ? "pulse 2s infinite" : "none" }}
      />
      <span className="text-xs text-white/50 font-mono tracking-wider">
        {isOk ? "BACKEND LIVE" : "UNREACHABLE"}
      </span>
      {isOk && health?.indexed_chunks > 0 && (
        <>
          <span className="text-white/20 text-xs">·</span>
          <span className="text-xs text-[#6C63FF] font-mono">
            {health.indexed_chunks} chunks
          </span>
        </>
      )}
    </div>
  );
}
