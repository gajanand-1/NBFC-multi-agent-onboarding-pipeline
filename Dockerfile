FROM python:3.11-slim

# EasyOCR/OpenCV need these system libs to run headless
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Pre-download models at build time so the container doesn't stall
# on first request and doesn't fail if the runtime network is restricted.
RUN python -c "import easyocr; easyocr.Reader(['en'])"
RUN python -c "from langchain_huggingface import HuggingFaceEmbeddings; HuggingFaceEmbeddings(model_name='sentence-transformers/all-mpnet-base-v2')"

# Render sets $PORT at runtime; falls back to 7860 for local/HF Spaces use.
EXPOSE 7860

CMD ["sh", "-c", "uvicorn backend:app --host 0.0.0.0 --port ${PORT:-7860}"]
