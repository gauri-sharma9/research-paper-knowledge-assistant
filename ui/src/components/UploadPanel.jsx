import { useState, useRef } from "react";
import { uploadPDFs, resetIndex } from "../api";

const MAX_FILES = 5;
const MAX_SIZE_MB = 10;
const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024;

export default function UploadPanel({ uploadedFiles, setUploadedFiles, onReset, onHealthRefresh }) {
  const [dragging, setDragging] = useState(false);
  const [progress, setProgress] = useState(null);
  const [error, setError] = useState("");
  const [resetting, setResetting] = useState(false);
  const inputRef = useRef();

  function validateFiles(files) {
    if (files.length + uploadedFiles.length > MAX_FILES) {
      return `Max ${MAX_FILES} files allowed. You already have ${uploadedFiles.length} uploaded.`;
    }
    for (const f of files) {
      if (!f.name.endsWith(".pdf")) return `"${f.name}" is not a PDF.`;
      if (f.size > MAX_SIZE_BYTES) return `"${f.name}" exceeds ${MAX_SIZE_MB}MB limit.`;
    }
    return null;
  }

  async function handleFiles(files) {
    setError("");
    const fileArray = Array.from(files);
    const validationError = validateFiles(fileArray);
    if (validationError) {
      setError(validationError);
      return;
    }

    setProgress(0);
    try {
      const result = await uploadPDFs(fileArray, (pct) => setProgress(pct));
      const newFiles = result.uploaded.map((u) => ({
        name: u.file,
        chunks: u.chunks,
        status: u.status,
      }));
      setUploadedFiles((prev) => {
        const names = new Set(prev.map((f) => f.name));
        return [...prev, ...newFiles.filter((f) => !names.has(f.name))];
      });
      onHealthRefresh();
    } catch (e) {
      setError(e?.response?.data?.detail || "Upload failed. Is the backend running?");
    } finally {
      setProgress(null);
    }
  }

  async function handleReset() {
    setResetting(true);
    setError("");
    try {
      await resetIndex();
      setUploadedFiles([]);
      onReset();
      onHealthRefresh();
    } catch (e) {
      setError("Reset failed. Is the backend running?");
    } finally {
      setResetting(false);
    }
  }

  return (
    <div className="flex flex-col gap-4 h-full">
      {/* Drop zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => { e.preventDefault(); setDragging(false); handleFiles(e.dataTransfer.files); }}
        onClick={() => inputRef.current.click()}
        className={`relative cursor-pointer rounded-xl border-2 border-dashed transition-all duration-300 p-8 flex flex-col items-center justify-center gap-3
          ${dragging ? "border-[#6C63FF] bg-[#6C63FF]/10" : "border-white/15 hover:border-white/30 bg-white/[0.02] hover:bg-white/[0.04]"}`}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf"
          multiple
          className="hidden"
          onChange={(e) => handleFiles(e.target.files)}
        />
        <div className="w-10 h-10 rounded-full border border-white/15 flex items-center justify-center">
          <svg className="w-5 h-5 text-white/40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 4v16m8-8H4" />
          </svg>
        </div>
        <div className="text-center">
          <p className="text-sm text-white/50">Drop PDFs here or click to browse</p>
          <p className="text-xs text-white/25 mt-1 font-mono">Max {MAX_FILES} files · {MAX_SIZE_MB}MB each</p>
        </div>
      </div>

      {/* Progress bar */}
      {progress !== null && (
        <div className="w-full bg-white/10 rounded-full h-0.5">
          <div
            className="bg-[#6C63FF] h-0.5 rounded-full transition-all duration-200"
            style={{ width: `${progress}%` }}
          />
        </div>
      )}

      {/* Error */}
      {error && (
        <p className="text-xs text-red-400 font-mono px-1">{error}</p>
      )}

      {/* Uploaded files list */}
      {uploadedFiles.length > 0 && (
        <div className="flex flex-col gap-2 mt-1">
          <p className="text-[10px] tracking-[0.2em] uppercase text-white/25 font-mono">Indexed Papers</p>
          {uploadedFiles.map((f, i) => (
            <div
              key={i}
              className="flex items-center justify-between px-3 py-2.5 rounded-lg bg-white/[0.03] border border-white/8"
            >
              <div className="flex items-center gap-2 min-w-0">
                <svg className="w-3.5 h-3.5 text-red-400/60 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" />
                </svg>
                <span className="text-xs text-white/60 truncate font-mono">{f.name}</span>
              </div>
              {f.chunks && (
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#6C63FF]/15 border border-[#6C63FF]/25 text-[#6C63FF] font-mono shrink-0 ml-2">
                  {f.chunks} chunks
                </span>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Reset button */}
      {uploadedFiles.length > 0 && (
        <button
          onClick={handleReset}
          disabled={resetting}
          className="mt-auto w-full py-2.5 rounded-lg border border-red-500/25 text-red-400/70 text-xs font-mono tracking-widest uppercase hover:bg-red-500/10 hover:border-red-500/40 hover:text-red-400 transition-all duration-200 disabled:opacity-40"
        >
          {resetting ? "Resetting..." : "Reset Index"}
        </button>
      )}
    </div>
  );
}
