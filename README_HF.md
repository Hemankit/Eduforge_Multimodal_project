# 🎓 EduForge - AI Educational Content Generator

> **Running on Hugging Face Spaces!** 🤗

Generate high-quality educational content with AI: slides, diagrams, and audio narration.

## 🚀 Quick Start

This Space uses **Llama 3.3 70B** via Together AI for content generation.

### Set Your API Key

1. Go to **Settings → Repository secrets**
2. Add: `TOGETHER_API_KEY` with your [Together AI key](https://api.together.xyz/)
3. Free tier includes $25 credit!

### Generate Content

```bash
curl -X POST "https://YOUR_USERNAME-eduforge.hf.space/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Binary Search Algorithm",
    "audience": "beginner",
    "max_duration_sec": 180,
    "render_formats": ["slides", "diagrams"]
  }'
```

## 📚 Features

- **🧠 AI-Powered**: Llama 3.3 70B (128K context)
- **📊 Multi-Modal**: Slides + Diagrams + Audio
- **✅ Validated**: Schema-based output consistency  
- **🔄 RESTful API**: Easy integration
- **💰 Affordable**: ~$0.88 per 1M tokens

## 🛠️ API Endpoints

### `POST /generate`
Generate educational content from a topic.

**Request:**
```json
{
  "topic": "Quantum Computing Basics",
  "audience": "intermediate",
  "max_duration_sec": 240,
  "render_formats": ["slides", "diagrams", "audio"]
}
```

**Response:**
```json
{
  "success": true,
  "generated_files": {
    "slides": "/outputs/20260328_120000/slides.html",
    "diagrams": ["/outputs/20260328_120000/diagram_00.svg"]
  }
}
```

### `GET /health`
Check system status and provider info.

### `GET /outputs/{session_id}/{filename}`
Download generated files.

## 🔧 Configuration

### Environment Variables (Set in Space Settings)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TOGETHER_API_KEY` | ✅ Yes | - | Together AI API key |
| `LLM_PROVIDER` | No | `together` | Use `together` for best quality |

## 💡 Examples

### Beginner Tutorial
```json
{
  "topic": "Introduction to Variables in Python",
  "audience": "beginner",
  "max_duration_sec": 120,
  "example_count": 3
}
```

### Advanced Deep Dive
```json
{
  "topic": "Understanding Backpropagation in Neural Networks",
  "audience": "advanced",
  "max_duration_sec": 300,
  "render_formats": ["slides", "diagrams"]
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
