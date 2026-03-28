---
title: Eduforge
emoji: 🎓
colorFrom: pink
colorTo: blue
sdk: docker
pinned: false
short_description: Multimodal AI content generator with LLM switching
---

# 🎓 EduForge - Multimodal Educational Content Generator

A deterministic, multimodal pipeline that converts structured text into synchronized educational artifacts (slides, diagrams, audio) with validation between modalities.

## 🚀 Features

- **Dynamic LLM Provider Switching** - Choose between local (Mistral 7B) or API-based (Llama 3.3 70B) inference
- **Multiple Output Formats** - Generates slides (HTML), diagrams (Mermaid), and audio narration (WAV)
- **RESTful API** - FastAPI-based server for easy integration
- **Schema Validation** - Ensures consistency across all output formats
- **Session Management** - Organized output storage with unique session IDs
- **Cost-Effective AI** - Together AI integration ($0.88/1M tokens vs GPT-4 $30/1M)

## 💻 System Requirements

### For Local Provider (Mistral 7B):
- **RAM:** 16GB+ recommended (model requires ~14GB)
- **Disk Space:** ~15GB for model weights
- **Optional:** NVIDIA GPU with 8GB+ VRAM for faster inference

### For API Provider (Llama 3.3 70B):
- **RAM:** 4GB+ (no local model)
- **API Key:** Together AI account (free tier available)

**Python:** 3.10+

## 📦 Quick Start

### Local Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure provider:**
```bash
# For local inference (Mistral 7B)
echo "LLM_PROVIDER=local" > .env

# For API inference (Llama 3.3 70B)
echo "LLM_PROVIDER=together" > .env
echo "TOGETHER_API_KEY=your_key_here" >> .env
```

3. **Start the server:**
```bash
python main.py
```

4. **Test the API:**
```bash
python test_api_client.py
```

For detailed LLM provider configuration, see [QUICK_START_LLM.md](QUICK_START_LLM.md).

## 🐳 Docker Deployment

### Option 1: Docker Compose (Recommended for Local Testing)

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env and add your API keys

# 2. Start with Docker Compose
docker-compose up -d

# 3. Test the deployment
python test_docker_deployment.py

# 4. View logs
docker-compose logs -f

# 5. Stop services
docker-compose down
```

### Option 2: Docker Manual Build

```bash
# Build image
docker build -t eduforge:latest .

# Run container
docker run -d \
  --name eduforge \
  -p 8000:7860 \
  --env-file .env \
  -v $(pwd)/generated_outputs:/app/generated_outputs \
  eduforge:latest

# View logs
docker logs -f eduforge
```

### Option 3: Hugging Face Spaces (Cloud Deployment)

**Users provide their own API keys** - no billing for the Space owner!

This Space supports two modes:
- **Together AI** (Llama 3.3 70B): Users provide API key in request
- **Local** (Mistral 7B): Free, no key needed

See [README_HF.md](README_HF.md) for detailed HF Spaces deployment guide.

## 🏗️ Architecture

- `main.py` - FastAPI server with content generation endpoints
- `llm_client.py` - Unified LLM client with provider abstraction
- `llm_providers/` - Local and API provider implementations
  - `local_provider.py` - Mistral 7B via Transformers
  - `together_provider.py` - Llama 3.3 70B via Together AI
- `content_generator.py` - Orchestrates LLM generation with validation
- `media_renderers/` - Slide, diagram, and audio rendering modules
- `prompt_templates.py` - Prompt engineering with schema injection
- `input_schema.py` / `output_schema.py` - Pydantic models for validation

## 📖 Usage

### Local Provider (Free)

Use the built-in Mistral 7B model:

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Binary Search Algorithm",
    "audience": "beginner",
    "render_formats": ["slides", "diagrams"],
    "llm_provider": "local"
  }'
```

### Together AI Provider (High Quality)

Provide your API key in the request:

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Neural Networks Fundamentals",
    "audience": "intermediate",
    "render_formats": ["slides", "diagrams", "audio"],
    "llm_provider": "together",
    "together_api_key": "YOUR_API_KEY_HERE"
  }'
```

**Get your key**: https://api.together.xyz/ (free $25 credit)

Outputs are saved to `generated_outputs/SESSION_ID/`.
