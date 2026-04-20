# Dockerfile for EduForge deployment
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    espeak \
    ffmpeg \
    libsndfile1 \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p generated_outputs

ENV HOST=0.0.0.0
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD sh -c 'python -c "import os, requests; requests.get(f\"http://localhost:{os.getenv(\"PORT\", \"8000\")}/health\", timeout=5)"'

CMD uvicorn main:app --host ${HOST} --port ${PORT} --log-level info
