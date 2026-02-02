# Research Paper Knowledge Assistant

## Overview
This project is an AI-powered assistant designed to help users understand and query research papers.
It uses Large Language Models (LLMs) together with Retrieval-Augmented Generation (RAG) to ensure
that responses are grounded in the content of uploaded research papers rather than relying solely
on the model’s general knowledge.

Users can upload one or more research paper PDFs and ask natural language questions such as
summaries, key contributions, methodologies, or where a specific concept is discussed.

---

## Key Features
- Upload and process research paper PDFs
- Extract and chunk textual content from papers
- Build a vector-based knowledge index for efficient retrieval
- Answer user questions using LLMs with Retrieval-Augmented Generation
- Support querying across multiple research papers

---

## Tech Stack
- **Backend**: Python, FastAPI
- **LLM**: API-based Large Language Model
- **Retrieval**: Vector embeddings with FAISS / Chroma
- **Frontend**: Streamlit
- **PDF Parsing**: PyPDF
- **Computer Vision**: OpenCV (used for document quality checks during ingestion)

---

## Project Structure
research-paper-knowledge-assistant/
│
├── backend/
│ ├── app.py
│ ├── ingestion.py
│ ├── rag.py
│ └── requirements.txt
│
├── ui/
│ └── app.py
│
├── data/
│ └── papers/
│
├── README.md
└── .gitignore


---

## How to Run Locally

### 1. Clone the repository
```bash
git clone <repo-url>
cd research-paper-knowledge-assistant

### 2.Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

###3.Install dependencies
pip install -r backend/requirements.txt

###4.Run the backend
uvicorn backend.app:app --reload

###5. Run the frontend
streamlit run ui/app.py
