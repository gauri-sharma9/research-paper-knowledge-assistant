import faiss
import numpy as np
from transformers import pipeline
from sentence_transformers import SentenceTransformer

qa_pipeline = pipeline(
    "document-question-answering",
    model="deepset/roberta-base-squad2"
)

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")  # fast + high quality


def store_embeddings(vectors, chunks):
    dimension = len(vectors[0])
    index = faiss.IndexFlatIP(dimension)

    vectors_np = np.array(vectors).astype("float32")
    faiss.normalize_L2(vectors_np)
    index.add(vectors_np)

    return index


def chunk_text(text, chunk_size=800, overlap=100):

    sentences = text.split(". ")
    chunks = []
    current_chunk = ""

    for sentence in sentences:

        if len(current_chunk) + len(sentence) < chunk_size:
            current_chunk += sentence + ". "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks



def embed_chunks(chunks):
    vectors = embedding_model.encode(chunks, show_progress_bar=True)
    return vectors


def embed_query(question):
    vector = embedding_model.encode([question])
    vector = np.array(vector).astype("float32")
    faiss.normalize_L2(vector)
    return vector


# increased retrieval context
def search_index(index, question_vector, k=3):
    distances, indices = index.search(question_vector, k)
    return indices


def retrieve_chunks(chunks, indices):
    results = []

    for i in indices[0]:
        if i < len(chunks):
            chunk = chunks[i]

            # filter unwanted sections
            if "@" in chunk:
                continue
            if "reference" in chunk.lower():
                continue
            if "arxiv" in chunk.lower():
                continue
            if "[" in chunk and "]" in chunk:  # citations
                continue

            results.append(chunk)

    return results
    print("\nRetrieved Chunks:\n")
    for r in results:
        print(r[:300])
        print("----")

def generate_answer(question, chunks):

    clean_chunks = []

    for c in chunks:
        c = c.replace("<pad>", "")
        c = c.replace("<EOS>", "")
        c = " ".join(c.split())
        clean_chunks.append(c)

    context = " ".join(clean_chunks[:3])  # top 3 chunks only

    result = qa_pipeline(
        question=question,
        context=context
    )

    return result["answer"]

if __name__ == "__main__":
    from ingestion import extract_text_from_pdf, clean_text

    text = extract_text_from_pdf("data/papers/sample.pdf")
    text = clean_text(text)

    chunks = chunk_text(text)

    vectors = embed_chunks(chunks)

    index = store_embeddings(vectors, chunks)

    question = "What is the main contribution of this paper?"

    question_vector = embed_query(question)

    indices = search_index(index, question_vector)

    results = retrieve_chunks(chunks, indices)

    answer = generate_answer(question, results)

    print("\nGenerated Answer:\n")
    print(answer)

    print("Chunks:", len(chunks))
    print("Vectors stored:", index.ntotal)