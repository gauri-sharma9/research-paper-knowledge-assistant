"""
app.py — FastAPI Backend
Handles: PDF upload, indexing, and question answering via the RAG pipeline.
"""
 
import os
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
 
from ingestion import extract_text_from_pdf, clean_text
from rag import (
    chunk_text, embed_chunks, store_embeddings,
    embed_query, search_index, retrieve_chunks,
    generate_answer, validate_uploads,
    MAX_FILES, MAX_FILE_SIZE_MB
)
 
# ── Logging setup ──────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)
 
# ── App setup ──────────────────────────────────────────────────────────────────
app = FastAPI()
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
 
# ── In-memory state (reset on server restart) ──────────────────────────────────
faiss_index = None
all_chunks = []
all_metadata = []
uploaded_files = []   # track filenames for UI display
 
UPLOAD_DIR = "data/papers"
os.makedirs(UPLOAD_DIR, exist_ok=True)
 
 
# ── Request models ─────────────────────────────────────────────────────────────
class QueryRequest(BaseModel):
    question: str
 
 
# ── Routes ─────────────────────────────────────────────────────────────────────
 
@app.get("/")
def root():
    return {"status": "backend running"}
 
 
@app.get("/health")
def health():
    return {
        "status": "ok",
        "indexed_chunks": len(all_chunks),
        "uploaded_files": uploaded_files
    }
 
 
@app.post("/upload")
async def upload_pdfs(files: list[UploadFile] = File(...)):
    """
    Accept one or more PDF uploads, validate them, extract + index their text.
    Enforces MAX_FILES and MAX_FILE_SIZE_MB constraints.
    """
    global faiss_index, all_chunks, all_metadata, uploaded_files
 
    # Read file bytes first so we can validate sizes
    file_data = []
    for f in files:
        content = await f.read()
        file_data.append({"name": f.filename, "size": len(content), "content": content})
 
    # Validate count + size constraints
    ok, error = validate_uploads([{"name": f["name"], "size": f["size"]} for f in file_data])
    if not ok:
        raise HTTPException(status_code=400, detail=error)
 
    results = []
 
    for f in file_data:
        save_path = os.path.join(UPLOAD_DIR, f["name"])
 
        # Save PDF to disk
        with open(save_path, "wb") as out:
            out.write(f["content"])
 
        # Extract, clean, chunk, embed, and index
        try:
            text = extract_text_from_pdf(save_path)
            text = clean_text(text)
            chunks = chunk_text(text)
            vectors = embed_chunks(chunks)
 
            faiss_index, all_metadata = store_embeddings(
                vectors,
                source_label=f["name"],
                existing_index=faiss_index,
                existing_metadata=all_metadata
            )
 
            all_chunks.extend(chunks)
 
            if f["name"] not in uploaded_files:
                uploaded_files.append(f["name"])
 
            logger.info("Indexed '%s' — %d chunks.", f["name"], len(chunks))
            results.append({"file": f["name"], "status": "indexed", "chunks": len(chunks)})
 
        except Exception as e:
            logger.error("Failed to process '%s': %s", f["name"], str(e))
            results.append({"file": f["name"], "status": "error", "detail": str(e)})
 
    return {"uploaded": results, "total_chunks": len(all_chunks)}
 
 
@app.post("/query")
def query(data: QueryRequest):
    """
    Answer a question using the indexed documents.
    Returns the answer and the source paper(s) it came from.
    """
    if faiss_index is None or len(all_chunks) == 0:
        raise HTTPException(status_code=400, detail="No documents indexed yet. Please upload a PDF first.")
 
    question = data.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
 
    question_vector = embed_query(question)
    indices = search_index(faiss_index, question_vector)
    chunks, sources = retrieve_chunks(all_chunks, indices, all_metadata)
    answer = generate_answer(question, chunks)
 
    return {
        "question": question,
        "answer": answer,
        "sources": list(set(sources))   # deduplicated source filenames
    }
 
 
@app.delete("/reset")
def reset():
    """
    Clear all indexed documents and reset state.
    Useful for testing or starting fresh.
    """
    global faiss_index, all_chunks, all_metadata, uploaded_files
    faiss_index = None
    all_chunks = []
    all_metadata = []
    uploaded_files = []
    logger.info("Index and state reset.")
    return {"status": "reset complete"}
 