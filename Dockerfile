# Dockerfile for EduForge deployment
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies for audio rendering and other tools
RUN apt-get update && apt-get install -y \
    espeak \
    ffmpeg \
    libsndfile1 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Together AI support for Llama 3.3 70B (recommended for production)
RUN pip install --no-cache-dir langchain-together>=0.1.0

# Copy application code
COPY . .

# Debug: Verify critical files are present
RUN echo "=== Checking for Python modules ===" && \
    ls -la *.py | head -20 && \
    echo "=== Checking cross_validation.py specifically ===" && \
    ls -la cross_validation.py && \
    echo "=== Testing import ===" && \
    python -c "import cross_validation; print('✅ cross_validation imports OK')" && \
    echo "=== Done ==="

# Create necessary directories
RUN mkdir -p generated_outputs

# Set environment variables
ENV PORT=7860
ENV HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

# Expose the application port
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:7860/health')"

# Run the application
CMD uvicorn main:app --host ${HOST} --port ${PORT} --log-level info
