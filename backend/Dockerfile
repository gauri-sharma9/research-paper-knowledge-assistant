# ── Base image ─────────────────────────────────────────────────────────────────
FROM python:3.12-slim

# ── Set working directory ───────────────────────────────────────────────────────
WORKDIR /app

# ── Install system dependencies ─────────────────────────────────────────────────
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ── Copy and install Python dependencies ────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy backend source ─────────────────────────────────────────────────────────
COPY backend/ .

# ── Create upload directory ─────────────────────────────────────────────────────
RUN mkdir -p data/papers

# ── Expose port ─────────────────────────────────────────────────────────────────
EXPOSE 8000

# ── Start server ────────────────────────────────────────────────────────────────
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
