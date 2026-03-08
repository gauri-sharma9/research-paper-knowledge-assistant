import faiss
import numpy as np

def store_embeddings(vectors, chunks):
    dimension = len(vectors[0])
    index = faiss.IndexFlatL2(dimension)

    vectors_np = np.array(vectors).astype("float32")
    index.add(vectors_np)

    return index


def chunk_text(text, chunk_size=800, overlap=100):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap

    return chunks

from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")  # fast + high quality

def embed_chunks(chunks):
    vectors = model.encode(chunks, show_progress_bar=True)
    return vectors

def embed_query(question):
    return model.encode([question])

def search_index(index, question_vector, k=3):
    distances, indices = index.search(question_vector, k)
    return indices

def retrieve_chunks(chunks, indices):
    results = []
    for i in indices[0]:
        results.append(chunks[i])
    return results

if __name__ == "__main__":
    from ingestion import extract_text_from_pdf

    text = extract_text_from_pdf("data/papers/sample.pdf")
    chunks = chunk_text(text)
    vectors = embed_chunks(chunks)
    index = store_embeddings(vectors, chunks)
    question = "What is the main contribution of this paper?"

    question_vector = embed_query(question)

    indices = search_index(index, question_vector)

    results = retrieve_chunks(chunks, indices)

    print("\nTop Relevant Chunks:\n")

    for r in results:
        print(r)
        print("\n---\n")

    print("Chunks:", len(chunks))
    print("Vectors stored:", index.ntotal)

