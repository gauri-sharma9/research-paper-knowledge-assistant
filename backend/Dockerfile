FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential gfortran && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    pymupdf \
    faiss-cpu \
    numpy \
    sentence-transformers \
    groq \
    python-dotenv \
    python-multipart

RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

COPY backend/ .

RUN mkdir -p data/papers

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]