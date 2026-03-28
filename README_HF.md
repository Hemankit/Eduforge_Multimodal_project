# 🎓 EduForge - AI Educational Content Generator

> **Running on Hugging Face Spaces!** 🤗

Generate high-quality educational content with AI: slides, diagrams, and audio narration.

## 🚀 Quick Start

This Space uses **Llama 3.3 70B** via Together AI. **You provide your own API key** in each request - we don't store or charge you!

### Get Your API Key

1. Sign up at [Together AI](https://api.together.xyz/)
2. Get free $25 credit
3. Copy your API key

### Generate Content

```bash
curl -X POST "https://heman20-eduforge.hf.space/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Binary Search Algorithm",
    "audience": "beginner",
    "max_duration_sec": 180,
    "render_formats": ["slides", "diagrams"],
    "llm_provider": "together",
    "together_api_key": "YOUR_API_KEY_HERE"
  }'
```

### Try Local Model (No API Key!)

For lighter workloads, use the local Mistral 7B model:

```bash
curl -X POST "https://heman20-eduforge.hf.space/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Python Lists",
    "audience": "beginner",
    "llm_provider": "local"
  }'
```

## 📚 Features

- **🧠 Bring Your Own Key**: You control your API usage and billing
- **🎯 Two Modes**: Local (Mistral 7B, free) or API (Llama 3.3 70B, paid)
- **📊 Multi-Modal**: Slides + Diagrams + Audio
- **✅ Validated**: Schema-based output consistency  
- **🔄 RESTful API**: Easy integration
- **💰 Affordable**: ~$0.88 per 1M tokens (Together AI)

## 🛠️ API Endpoints

### `POST /generate`
Generate educational content from a topic.

**Request Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `topic` | string | ✅ | Topic to generate content about |
| `audience` | string | No | `beginner`, `intermediate`, or `advanced` (default: `beginner`) |
| `max_duration_sec` | int | No | Target duration in seconds (default: 180) |
| `render_formats` | array | No | `["slides", "diagrams", "audio"]` (default: `["slides", "diagrams"]`) |
| `llm_provider` | string | No | `"local"` or `"together"` (default: `"together"`) |
| `together_api_key` | string | ⚠️ | **Required if `llm_provider="together"`** |

**Request Example:**
```json
{
  "topic": "Quantum Computing Basics",
  "audience": "intermediate",
  "max_duration_sec": 240,
  "render_formats": ["slides", "diagrams"],
  "llm_provider": "together",
  "together_api_key": "YOUR_API_KEY_HERE"
}
```

**Response:**
```json
{
  "success": true,
  "generated_files": {
    "slides": "/outputs/20260328_120000/slides.html",
    "diagrams": ["/outputs/20260328_120000/diagram_00.svg"]
  },
  "generation_time_sec": 15.3
}
```

### `GET /health`
Check system status and provider info.

### `GET /outputs/{session_id}/{filename}`
Download generated files.

## 🔧 Configuration

**No Space-level configuration needed!** Users provide their own API keys in requests.

This approach means:
- ✅ **Free for you**: No API bills for the Space owner
- ✅ **Private**: Each user's key is only used for their requests
- ✅ **Flexible**: Users can switch between local and API modes anytime

## 💡 Examples

### Option 1: Together AI (High Quality)

Requires your Together AI API key from https://api.together.xyz/

```json
{
  "topic": "Introduction to Variables in Python",
  "audience": "beginner",
  "max_duration_sec": 120,
  "example_count": 3,
  "llm_provider": "together",
  "together_api_key": "your_key_here"
}
```

**Cost**: ~$0.01-0.05 per generation (depending on content length)

### Option 2: Local Mistral 7B (Free)

No API key needed! Uses the Space's built-in model.

```json
{
  "topic": "Python Lists Basics",
  "audience": "beginner",
  "max_duration_sec": 120,
  "llm_provider": "local"
}
```

**Cost**: $0 (slower, but free!)

### Advanced Deep Dive
```json
{
  "topic": "Understanding Backpropagation in Neural Networks",
  "audience": "advanced",
  "max_duration_sec": 300,
  "render_formats": ["slides", "diagrams"],
  "llm_provider": "together",
  "together_api_key": "your_key_here"
}
```

## 📖 Documentation

- [API Guide](./API_GUIDE.md) - Detailed API documentation
- [Quick Start](./QUICK_START_LLM.md) - LLM setup guide
- [Schema Reference](./input_schema.py) - Input validation

## 🧪 Local Development

```bash
# Clone and install
git clone https://huggingface.co/spaces/YOUR_USERNAME/eduforge
cd eduforge
pip install -r requirements.txt
pip install langchain-together

# Set API key
export TOGETHER_API_KEY=your_key_here

# Run locally
uvicorn main:app --host 0.0.0.0 --port 7860
```

## 💰 Cost Estimate

With Together AI Llama 3.3 70B:
- **Per generation**: ~$0.007 (less than 1¢)
- **100 generations**: ~$0.70
- **Free tier**: $25 credit = 3,500+ generations

## 🏗️ Tech Stack

- **Backend**: FastAPI + Uvicorn
- **AI Model**: Llama 3.3 70B via Together AI (LangChain)
- **Rendering**: Jinja2, Matplotlib, Mermaid
- **Audio**: pyttsx3 (offline TTS)
- **Validation**: Pydantic v2

## 🤝 Contributing

This is an academic project showcasing deterministic AI pipelines for education.

## 📄 License

MIT License - See LICENSE file

## 🔗 Links

- [Together AI](https://together.xyz/) - Get your API key
- [GitHub Repo](https://github.com/YOUR_USERNAME/eduforge) - Source code
- [Report Issues](https://github.com/YOUR_USERNAME/eduforge/issues)

---

**Made with ❤️ for educators and learners**
