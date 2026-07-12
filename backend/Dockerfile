FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# sentence-transformers pulls in torch, which defaults to the CUDA build on
# Linux (~2GB of unused NVIDIA libraries) even though this app only ever runs
# CPU inference on a small embedding model. Installing the CPU-only wheel
# first keeps the later `torch>=1.11.0` requirement already satisfied.
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch
RUN pip install --no-cache-dir -r requirements.txt

# Bake the embedding model into the image at build time so no network call
# happens at request time (matches the product's zero-external-AI-API claim).
ENV HF_HOME=/opt/hf-cache
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
RUN python -m spacy download en_core_web_sm

COPY . .

# Vercel's container runtime injects $PORT (default 80); local docker-compose
# doesn't set it, so this falls back to 8000 to match compose's port mapping.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
