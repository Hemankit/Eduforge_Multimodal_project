# EduForge - Multimodal Educational Content Generator

A deterministic, multimodal pipeline that converts structured text into synchronized educational artifacts (slides, diagrams, audio) with validation between modalities.

## Features

- **Dynamic LLM Provider Switching** - Choose between local, RunPod-hosted Mistral (`remote_gpu`), or Together AI (`together`)
- **Multiple Output Formats** - Generates slides (HTML), diagrams (Mermaid), and audio narration (WAV)
- **RESTful API** - FastAPI-based server for easy integration
- **Schema Validation** - Ensures consistency across all output formats
- **Session Management** - Organized output storage with unique session IDs
- **Cost-Effective AI** - Together AI integration ($0.88/1M tokens vs GPT-4 $30/1M)

## System Requirements

### For Local Provider (Mistral 7B):
- **RAM:** 16GB+ recommended (model requires ~14GB)
- **Disk Space:** ~15GB for model weights
- **Optional:** NVIDIA GPU with 8GB+ VRAM for faster inference

### For API Provider (Together AI):
- **RAM:** 4GB+ (no local model)
- **API Key:** Together AI account (free tier available)

### For Remote GPU Provider (RunPod + Mistral):
- **RAM:** 4GB+ for API server container
- **RunPod endpoint:** URL reachable from your deployment (example: `https://<id>-8000.proxy.runpod.net`)
- **Remote API key:** Shared key expected by your RunPod `/infer` endpoint

**Python:** 3.10+

## Quick Start

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

# For RunPod-hosted Mistral inference
echo "LLM_PROVIDER=remote_gpu" > .env
echo "REMOTE_GPU_URL=https://<your-runpod-endpoint>" >> .env
echo "REMOTE_GPU_API_KEY=<your-runpod-api-key>" >> .env
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

## Input Requirements (POST /generate)

### Required fields
- `topic` (string): What lesson to generate, e.g. `"Gradient Descent"`

### Common optional fields
- `audience` (string): `beginner` (default), `intermediate`, `advanced`
- `render_formats` (array[string]): any of `slides`, `diagrams`, `audio`
- `llm_provider` (string): `local`, `remote_gpu`, `together` (default is `together`)

### Provider-specific requirements
- `llm_provider: "together"`
  - Must include `together_api_key` in request body (or configure env and pass it in request flow you use)
- `llm_provider: "remote_gpu"`
  - Server must have `REMOTE_GPU_URL` and `REMOTE_GPU_API_KEY` environment variables set
  - Request body does not need additional key fields

### Full request shape (reference)
```json
{
  "topic": "Gradient Descent",
  "audience": "beginner",
  "max_duration_sec": 180,
  "example_count": null,
  "render_formats": ["slides", "diagrams"],
  "slide_format": "html",
  "optimize_for_format": true,
  "include_few_shot": false,
  "llm_provider": "remote_gpu",
  "together_api_key": null
}
```

## Provider Quickstart

### RunPod / Mistral (`remote_gpu`)

1. Ensure your RunPod app exposes:
- `POST /infer`
- request JSON: `{ "prompt": string, "max_tokens": int, "temperature": float }`
- header: `x-api-key`

2. Set env vars on your API service:
```bash
REMOTE_GPU_URL=https://<your-runpod-endpoint>
REMOTE_GPU_API_KEY=<your-runpod-api-key>
```

3. Generate content:
```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Gradient Descent",
    "audience": "beginner",
    "render_formats": ["slides", "diagrams"],
    "llm_provider": "remote_gpu"
  }'
```

### Together AI (`together`)

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

Get key: `https://api.together.xyz/`

## Accessing Generated Files

- API response includes `generated_files`, for example:
  - `"slides": "/outputs/20260423_041646/slides.html"`
- Open with your server base URL:
  - local: `http://localhost:8000/outputs/<session_id>/<filename>`
  - cloud: `https://<your-service-url>/outputs/<session_id>/<filename>`
- List recent sessions:
  - `GET /sessions`

Note: in Cloud Run, local container storage is ephemeral; use object storage (for example GCS) for persistence.

## Docker Deployment

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

## Architecture

- `main.py` - FastAPI server with content generation endpoints
- `llm_client.py` - Unified LLM client with provider abstraction
- `llm_providers/` - Local and API provider implementations
  - `local_provider.py` - Mistral 7B via Transformers
  - `remote_gpu_provider.py` - RunPod-hosted inference via `/infer`
  - `together_provider.py` - Llama 3.3 70B via Together AI
- `content_generator.py` - Orchestrates LLM generation with validation
- `media_renderers/` - Slide, diagram, and audio rendering modules
- `prompt_templates.py` - Prompt engineering with schema injection
- `input_schema.py` / `output_schema.py` - Pydantic models for validation

## Usage

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

### Together AI Provider

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

Get your key: `https://api.together.xyz/`

Outputs are saved to `generated_outputs/SESSION_ID/`.
