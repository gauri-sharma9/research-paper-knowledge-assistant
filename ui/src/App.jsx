import { useState, useEffect } from "react";
import { checkHealth } from "./api";
import StatusBadge from "./components/StatusBadge";
import UploadPanel from "./components/UploadPanel";
import ChatWindow from "./components/ChatWindow";

const TYPING_TEXT = "Welcome, Researcher.";
const TYPING_SPEED = 80; // ms per character — slow and deliberate

export default function App() {
  const [typedText, setTypedText] = useState("");
  const [typingDone, setTypingDone] = useState(false);
  const [uiVisible, setUiVisible] = useState(false);

  const [health, setHealth] = useState(null);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [messages, setMessages] = useState([]);

  // ── Typing animation ───────────────────────────────────────────────────────
  useEffect(() => {
    let i = 0;
    const interval = setInterval(() => {
      setTypedText(TYPING_TEXT.slice(0, i + 1));
      i++;
      if (i === TYPING_TEXT.length) {
        clearInterval(interval);
        setTypingDone(true);
        setTimeout(() => setUiVisible(true), 600);
      }
    }, TYPING_SPEED);
    return () => clearInterval(interval);
  }, []);

  // ── Health polling ─────────────────────────────────────────────────────────
  async function refreshHealth() {
    try {
      const data = await checkHealth();
      setHealth(data);
    } catch {
      setHealth({ status: "error" });
    }
  }

  useEffect(() => {
    refreshHealth();
    const interval = setInterval(refreshHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-black text-[#F5F5F5] flex flex-col overflow-hidden">

      {/* ── Header ──────────────────────────────────────────────────────────── */}
      <header className="flex items-center justify-between px-8 py-5 border-b border-white/[0.06]">
        <div>
          <p className="text-[10px] tracking-[0.3em] uppercase text-white/25 font-mono mb-0.5">
            Research Knowledge Assistant
          </p>
          <div className="h-6 flex items-center">
            <span
              className="font-['Playfair_Display'] text-lg text-[#F5F5F5] tracking-wide"
              style={{ borderRight: typingDone ? "none" : "2px solid #F5F5F5", paddingRight: "2px" }}
            >
              {typedText}
            </span>
          </div>
        </div>
        <StatusBadge health={health} />
      </header>

      {/* ── Main UI ─────────────────────────────────────────────────────────── */}
      <main
        className="flex flex-1 overflow-hidden transition-all duration-700"
        style={{
          opacity: uiVisible ? 1 : 0,
          transform: uiVisible ? "translateY(0)" : "translateY(12px)",
        }}
      >
        {/* Left panel — Upload */}
        <aside className="w-80 shrink-0 border-r border-white/[0.06] p-6 overflow-y-auto">
          <UploadPanel
            uploadedFiles={uploadedFiles}
            setUploadedFiles={setUploadedFiles}
            onReset={() => setMessages([])}
            onHealthRefresh={refreshHealth}
          />
        </aside>

        {/* Right panel — Chat */}
        <section className="flex-1 flex flex-col overflow-hidden">
          <ChatWindow
            uploadedFiles={uploadedFiles}
            messages={messages}
            setMessages={setMessages}
          />
        </section>
      </main>

      {/* ── Subtle noise overlay for depth ──────────────────────────────────── */}
      <div
        className="pointer-events-none fixed inset-0 opacity-[0.025]"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E")`,
          backgroundRepeat: "repeat",
          backgroundSize: "128px",
        }}
      />
    </div>
  );
}
