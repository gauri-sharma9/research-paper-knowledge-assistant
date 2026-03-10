import faiss
import numpy as np
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from sentence_transformers import SentenceTransformer

llm_model_name = "google/flan-t5-base"

tokenizer = AutoTokenizer.from_pretrained(llm_model_name)
llm_model = AutoModelForSeq2SeqLM.from_pretrained(llm_model_name)

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")  # fast + high quality


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


def embed_chunks(chunks):
    vectors = embedding_model.encode(chunks, show_progress_bar=True)
    return vectors


def embed_query(question):
    return embedding_model.encode([question])


# increased retrieval context
def search_index(index, question_vector, k=5):
    distances, indices = index.search(question_vector, k)
    return indices


def retrieve_chunks(chunks, indices):
    results = []

    for i in indices[0]:
        if i < len(chunks):
            results.append(chunks[i])

    return results


def generate_answer(question, chunks):

    # clean chunk text
    clean_chunks = []
    for c in chunks:
        c = c.replace("<pad>", "")
        c = c.replace("<EOS>", "")
        c = " ".join(c.split())
        clean_chunks.append(c)

    context = " ".join(clean_chunks)

    prompt = f"""
You are an AI assistant that answers questions about research papers.

Use ONLY the information from the context below.

Context:
{context}

Question:
{question}

Give a clear and short answer.
"""

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True)

    outputs = llm_model.generate(
        **inputs,
        max_new_tokens=150,
        temperature=0.2
    )

    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return answer


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

    answer = generate_answer(question, results)

    print("\nGenerated Answer:\n")
    print(answer)

    print("Chunks:", len(chunks))
    print("Vectors stored:", index.ntotal)