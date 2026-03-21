import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

model_name = "google/flan-t5-base"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")  # fast + high quality


def store_embeddings(vectors, chunks):
    dimension = len(vectors[0])
    index = faiss.IndexFlatIP(dimension)

    vectors_np = np.array(vectors).astype("float32")
    faiss.normalize_L2(vectors_np)
    index.add(vectors_np)

    return index


def chunk_text(text):

    # split by section titles
    sections = text.split("\n")

    chunks = []
    current_chunk = ""

    for line in sections:

        line = line.strip()

        if len(line) == 0:
            continue

        # detect section headers
        if any(keyword in line.lower() for keyword in ["abstract", "introduction"]):
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = line + " "
        else:
            current_chunk += line + " "

        # keep chunk size reasonable
        if len(current_chunk) > 800:
            chunks.append(current_chunk)
            current_chunk = ""

    if current_chunk:
        chunks.append(current_chunk)

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

    # ✅ FIRST: check if abstract exists anywhere
    for chunk in chunks:
        if "abstract" in chunk.lower():
            print("\nUsing ABSTRACT directly\n")
            return [chunk]

    # fallback to FAISS
    results = []

    for i in indices[0]:
        if i < len(chunks):
            results.append(chunks[i])

    print("\nRetrieved Chunks:\n")
    for r in results:
        print(r[:200])
        print("----")

    return results

def generate_answer(question, chunks):

    # clean chunks
    clean_chunks = []
    for c in chunks:
        c = c.replace("<pad>", "")
        c = c.replace("<EOS>", "")
        c = " ".join(c.split())
        clean_chunks.append(c)

    # 🔥 MOST IMPORTANT: only top 2 chunks
    if len(clean_chunks) == 0:
        return "No relevant context found."

    context = clean_chunks[0]

    prompt = f"""
You are reading a research paper.

Based on the context below, explain the main contribution of the paper in detail.

Context:
{context}

Question: {question}

Write a detailed answer in 3-4 sentences explaining what the paper proposes and why it is important.
Do not give a short phrase.
Write a clear explanation of the main contribution only.
Do not include experimental results or numbers.
"""

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True)

    outputs = model.generate(
    **inputs,
    max_new_tokens=200,
    do_sample=False,
    min_length=80
)

    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return answer

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