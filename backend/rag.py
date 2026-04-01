"""
rag.py — Core RAG Pipeline
Handles: chunking, embedding, FAISS indexing, retrieval, and LLM answer generation.
Supports multi-document indexing and grounded answer generation.
"""
 
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import os
from groq import Groq
from dotenv import load_dotenv
import logging
 
# ── Logging setup ──────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)
 
# ── Upload constraints ─────────────────────────────────────────────────────────
MAX_FILES = 5                   # Maximum number of PDFs allowed at once
MAX_FILE_SIZE_MB = 10           # Maximum size per PDF in megabytes
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
 
# ── Model loading ──────────────────────────────────────────────────────────────
load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

 
logger.info("Loading embedding model: all-MiniLM-L6-v2")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
 
 
# ── File validation ────────────────────────────────────────────────────────────
 
def validate_uploads(file_list):
    """
    Validate uploaded files against size and count constraints.
 
    Args:
        file_list: list of dicts with keys 'name' (str) and 'size' (int, bytes)
 
    Returns:
        (ok: bool, error_message: str or None)
    """
    if len(file_list) > MAX_FILES:
        return False, f"Too many files. Maximum allowed is {MAX_FILES}."
 
    for f in file_list:
        if f["size"] > MAX_FILE_SIZE_BYTES:
            return False, (
                f"File '{f['name']}' exceeds the {MAX_FILE_SIZE_MB} MB size limit."
            )
 
    return True, None
 
 
# ── Text chunking ──────────────────────────────────────────────────────────────
 
def chunk_text(text, max_chunk_size=800):
    """
    Split extracted PDF text into manageable chunks for embedding.
 
    Strategy:
    - Split on newlines (section-level splits).
    - Start a new chunk when a known section header is detected (abstract, introduction).
    - Hard-cap each chunk at max_chunk_size characters to avoid oversized embeddings.
 
    Args:
        text (str): Full cleaned text from a PDF.
        max_chunk_size (int): Maximum character length per chunk.
 
    Returns:
        list[str]: List of text chunks.
    """
    lines = text.split("\n")
    chunks = []
    current_chunk = ""
 
    for line in lines:
        line = line.strip()
        if not line:
            continue
 
        # Start a new chunk when a major section header is detected
        if any(keyword in line.lower() for keyword in ["abstract", "introduction"]):
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = line + " "
        else:
            current_chunk += line + " "
 
        # Hard cap: flush chunk when it exceeds max size
        if len(current_chunk) > max_chunk_size:
            chunks.append(current_chunk.strip())
            current_chunk = ""
 
    # Flush remaining content
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
 
    logger.info("Chunked text into %d chunks.", len(chunks))
    return chunks
 
 
# ── Embedding ──────────────────────────────────────────────────────────────────
 
def embed_chunks(chunks):
    """
    Generate sentence embeddings for a list of text chunks.
 
    Args:
        chunks (list[str]): Text chunks to embed.
 
    Returns:
        np.ndarray: Array of embedding vectors, shape (N, embedding_dim).
    """
    logger.info("Embedding %d chunks...", len(chunks))
    vectors = embedding_model.encode(chunks, show_progress_bar=True)
    return vectors
 
 
def embed_query(question):
    """
    Embed a user query and normalize it for cosine similarity search.
 
    Args:
        question (str): The user's question.
 
    Returns:
        np.ndarray: Normalized query vector, shape (1, embedding_dim).
    """
    vector = embedding_model.encode([question])
    vector = np.array(vector).astype("float32")
    faiss.normalize_L2(vector)
    return vector
 
 
# ── FAISS index management ─────────────────────────────────────────────────────
 
def store_embeddings(vectors, source_label=None, existing_index=None, existing_metadata=None):
    """
    Create or update a FAISS index with normalized chunk embeddings.
 
    Supports multi-document indexing: pass an existing index and metadata
    to append new document vectors to it.
 
    Args:
        vectors (np.ndarray): Chunk embedding vectors for a single document.
        source_label (str, optional): Filename/label to tag these chunks with.
        existing_index: Existing FAISS index to append to (or None to create new).
        existing_metadata (list, optional): Existing metadata list to extend.
 
    Returns:
        tuple: (faiss.Index, list[dict]) — updated index and metadata list.
                Metadata entries have keys: 'chunk_id' (global int), 'source' (str).
    """
    vectors_np = np.array(vectors).astype("float32")
    faiss.normalize_L2(vectors_np)
 
    if existing_index is None:
        # Create a new inner-product (cosine) index
        dimension = vectors_np.shape[1]
        index = faiss.IndexFlatIP(dimension)
        metadata = []
    else:
        index = existing_index
        metadata = existing_metadata or []
 
    start_id = index.ntotal
    index.add(vectors_np)
 
    # Record which source document each vector came from
    for i in range(len(vectors)):
        metadata.append({
            "chunk_id": start_id + i,
            "source": source_label or "unknown"
        })
 
    logger.info(
        "Stored %d vectors from '%s'. Total in index: %d.",
        len(vectors), source_label, index.ntotal
    )
    return index, metadata
 
 
# ── Retrieval ──────────────────────────────────────────────────────────────────
 
def search_index(index, question_vector, k=3):
    """
    Search the FAISS index for the top-k most relevant chunk indices.
 
    Args:
        index: FAISS index to search.
        question_vector (np.ndarray): Normalized query embedding, shape (1, dim).
        k (int): Number of top results to retrieve.
 
    Returns:
        np.ndarray: Array of shape (1, k) containing chunk indices.
    """
    distances, indices = index.search(question_vector, k)
    logger.info("Top-%d indices retrieved: %s", k, indices[0].tolist())
    return indices
 
 
def retrieve_chunks(all_chunks, indices, metadata=None):
    """
    Retrieve text chunks using FAISS search indices.
    """
    results = []
    sources = []

    for i in indices[0]:
        if 0 <= i < len(all_chunks):
            results.append(all_chunks[i])
            src = metadata[i]["source"] if metadata else "unknown"
            sources.append(src)

    logger.info("Retrieved %d chunks.", len(results))
    return results, sources
 
 
# ── Answer generation ──────────────────────────────────────────────────────────
 
def generate_answer(question, chunks):
    """
    Generate a grounded answer using Groq LLM and retrieved context chunks.
    Answers only from provided context — will not hallucinate.
    """
    if not chunks:
        return "Not found in paper."

    # Clean special tokens
    clean_chunks = []
    for c in chunks:
        c = c.replace("<pad>", "").replace("<EOS>", "")
        c = " ".join(c.split())
        clean_chunks.append(c)

    context = " ".join(clean_chunks[:3])

    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are a research assistant. Answer questions using ONLY the provided context. Keep answers concise for simple questions, but provide detailed explanations when the question warrants it."
            },
            {
                "role": "user",
                "content": f"Context: {context}\n\nQuestion: {question}"
            }
        ]
    )

    answer = response.choices[0].message.content
    logger.info("Answer generated (%d chars).", len(answer))
    return answer
 
# ── Standalone test ────────────────────────────────────────────────────────────
 
if __name__ == "__main__":
    from ingestion import extract_text_from_pdf, clean_text

    all_chunks = []
    faiss_index = None
    all_metadata = []

    # ← Add or remove papers from this list as needed
    papers = [
        "data/papers/sample.pdf",
        "data/papers/bert.pdf",
        "data/papers/resnet.pdf"
    ]

    for paper in papers:
        text = extract_text_from_pdf(paper)
        text = clean_text(text)
        chunks = chunk_text(text)
        vectors = embed_chunks(chunks)
        faiss_index, all_metadata = store_embeddings(
            vectors,
            source_label=paper.split("/")[-1],
            existing_index=faiss_index,
            existing_metadata=all_metadata
        )
        all_chunks.extend(chunks)

    question = "What attention mechanism does the paper propose?"
    question_vector = embed_query(question)
    indices = search_index(faiss_index, question_vector, k=6)
    results, sources = retrieve_chunks(all_chunks, indices, all_metadata)
    answer = generate_answer(question, results)

    print("\n── Generated Answer ──")
    print(answer)
    print("\nSource(s):", sources)
    print(f"Chunks indexed: {faiss_index.ntotal}")