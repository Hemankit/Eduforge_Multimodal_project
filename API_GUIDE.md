# 🎓 EduForge - AI-Powered Educational Content Generator

Generate multimodal educational content (slides, diagrams, audio) using Mistral-7B-Instruct.

## 💻 System Requirements

- **RAM:** 16GB+ recommended (model requires ~14GB)
- **Python:** 3.10+
- **Disk Space:** ~15GB for model weights
- **Optional:** NVIDIA GPU with 8GB+ VRAM (for faster inference)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the API Server

```bash
python main.py
```

The server will start at `http://localhost:8000`

**Note:** First request will be slow (~2-3 min) as it loads the Mistral-7B model (~14GB).

### 3. Test the API

In a new terminal:

```bash
python test_api_client.py
```

## 📚 API Endpoints

### Generate Content
**POST** `/generate`

Generate educational content with multimodal outputs.

**Request Body:**
```json
{
  "topic": "Binary Search Algorithm",
  "audience": "intermediate",
  "max_duration_sec": 240,
  "example_count": 2,
  "render_formats": ["slides", "diagrams", "audio"],
  "optimize_for_format": true,
  "include_few_shot": false
}
```

**Response:**
```json
{
  "success": true,
  "message": "Content generated successfully in 45.23s",
  "content_output": { ... },
  "generated_files": {
    "slides": "/outputs/20260309_143022/slides.html",
    "diagrams": ["/outputs/20260309_143022/diagram_00.html"],
    "audio": ["/outputs/20260309_143022/narration_00.wav"]
  },
  "generation_time_sec": 45.23
}
```

### Health Check
**GET** `/health`

Check if the server is running and model is loaded.

### List Sessions
**GET** `/sessions`

List all generation sessions and their files.

### Download File
**GET** `/outputs/{session_id}/{filename}`

Download a specific generated file.

## 🧪 Testing Without LLM

Test individual components without loading the model:

```bash
# Test schemas and validation
python test_schemas.py

# Test slide renderer
python test_slide_renderer.py

# Test diagram renderer
python test_diagram_renderer.py

# Test audio renderer
python test_audio_renderer.py

# Test prompt builder
python test_prompt_builder.py

# Test full rendering pipeline (no LLM)
python test_rendering.py
```

## 📖 Interactive API Documentation

Once the server is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 🛠️ Example Usage with cURL

```bash
# Generate content
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Gradient Descent",
    "audience": "beginner",
    "max_duration_sec": 180,
    "render_formats": ["slides", "diagrams"],
    "optimize_for_format": true
  }'

# Download slides
curl -O "http://localhost:8000/outputs/20260309_143022/slides.html"
```

## 📦 Project Structure

```
├── main.py                    # FastAPI server (orchestration)
├── llm_client.py             # LLM loading and generation
├── content_generator.py      # Content generation with repair loop
├── input_schema.py           # Input validation schemas
├── output_schema.py          # Output validation schemas
├── prompt_templates.py       # Prompt building with schema injection
├── cross_validation.py       # Input ↔ Output validation
├── few_shot_examples.py      # Example data for few-shot learning
├── system_prompt.txt         # Educational content guidelines
├── media_renderers/          # Rendering modules
│   ├── slide_renderer.py     # HTML slides (custom template)
│   ├── diagram_renderer.py   # Mermaid diagrams → SVG/HTML
│   └── audio_renderer.py     # pyttsx3 TTS narration
├── templates/                # Jinja2 templates
│   └── deck.html.j2          # Slide deck template
└── test_*.py                 # Test files for each component
```

## ⚙️ Configuration

### Audience Levels
- `beginner` - Simple explanations, lots of examples
- `intermediate` - Balanced detail and examples
- `advanced` - Technical depth, fewer basics

### Render Formats
- `slides` - HTML slide deck
- `diagrams` - Mermaid diagrams (HTML/SVG)
- `audio` - TTS narration (WAV files)
- `video` - (Future: video generation)

### Optimization
- `optimize_for_format=true` - Generates content optimized for selected formats
  - Slides → Punchy, concise bullet points
  - Diagrams → Detailed `mermaid_source` generation
  - Audio → Standalone narration scripts

## 🔧 Production Deployment

### Environment Variables
Set these before running in production:

```bash
export MODEL_CACHE_DIR="/path/to/model/cache"
export OUTPUT_DIR="/path/to/outputs"
export MAX_WORKERS=4
export PORT=8000
```

### Running with Gunicorn (Production)

```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "main.py"]
```

## 🐛 Troubleshooting

### Model Loading Issues
- **Problem:** Model takes too long to load
- **Solution:** Pre-download with `huggingface-cli download mistralai/Mistral-7B-Instruct-v0.3`

### Memory Issues
- **Problem:** OOM errors during model loading
- **Solution:** 
  1. Ensure system has 16GB+ RAM
  2. Close other applications
  3. Use a machine with GPU (8GB+ VRAM) for faster inference

### Diagram Not Rendering
- **Problem:** Blank page when opening diagram HTML
- **Solution:** 
  1. Check browser console for errors
  2. Verify internet connection (Mermaid.js loads from CDN)
  3. Install mermaid-cli: `npm install -g @mermaid-js/mermaid-cli`

## 🤝 Contributing

Contributions welcome! Please open an issue or PR.
