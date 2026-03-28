# 🚀 Hugging Face Spaces Deployment Guide

This guide explains how to deploy EduForge on Hugging Face Spaces using Docker.

## 📋 Prerequisites

- A Hugging Face account ([sign up here](https://huggingface.co/join))
- Your LLM provider API keys (OpenAI, Anthropic, or Together AI)
- Basic familiarity with Hugging Face Spaces

## 🏗️ Deployment Steps

### 1. Create a New Space

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Fill in the details:
   - **Space name**: `eduforge` (or your preferred name)
   - **License**: Choose your preferred license
   - **SDK**: Select **Docker**
   - **Hardware**: Start with CPU (free tier) or upgrade to GPU if needed

### 2. Configure Space Settings

In your Space settings, add the following **Environment Variables** (Secrets):

#### Required for API-based LLM Providers:

```bash
# Choose your LLM provider
LLM_PROVIDER=auto              # Options: auto, local, openai, anthropic, together

# API Keys (add the ones you plan to use)
OPENAI_API_KEY=sk-...          # For OpenAI (GPT-4, GPT-3.5)
ANTHROPIC_API_KEY=sk-ant-...   # For Anthropic (Claude)
TOGETHER_API_KEY=...           # For Together AI (Llama, Mixtral)
```

#### Optional Configuration:

```bash
# Specific model selection
LLM_MODEL=gpt-4-turbo          # Override default model

# Fallback chain (comma-separated)
LLM_FALLBACK_CHAIN=openai,anthropic,together

# Performance tuning
MAX_TOKENS=2000
TEMPERATURE=0.7
```

### 3. Push Your Code

You have two options:

#### Option A: Using Git (Recommended)

```bash
# Clone your Space repository
git clone https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
cd YOUR_SPACE_NAME

# Copy all project files (from your Eduforge project root)
cp -r ../Eduforge_Multimodal_project/* .

# Ensure these files are present
ls Dockerfile  # Should exist
ls main.py     # Should exist

# Commit and push
git add .
git commit -m "Initial deployment"
git push
```

#### Option B: Using Web Interface

1. Navigate to your Space's "Files" tab
2. Upload all files from your project root
3. Ensure `Dockerfile` and all Python files are uploaded

### 4. Update README.md (Space Configuration)

Create or update `README.md` in your Space root with:

```yaml
---
title: EduForge
emoji: 🎓
colorFrom: pink
colorTo: blue
sdk: docker
pinned: false
python_version: "3.10"
app_port: 7860
---

# 🎓 EduForge - Multimodal Educational Content Generator

AI-powered educational content generation with slides, diagrams, and audio narration.

## 🚀 Features

- **AI-Powered Content**: Uses advanced LLMs to create educational content
- **Multiple Formats**: Generates slides (HTML), diagrams (Mermaid), and audio (WAV)
- **RESTful API**: Easy integration via FastAPI
- **Multi-Provider**: Supports OpenAI, Anthropic, Together AI, and local models

## 📖 API Usage

### Generate Content

```bash
curl -X POST "https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Binary Search Algorithm",
    "audience": "intermediate",
    "max_duration_sec": 240,
    "render_formats": ["slides", "diagrams"]
  }'
```

### Check Health

```bash
curl "https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space/health"
```

## 🔧 Configuration

Set environment variables in Space Settings for your preferred LLM provider.
```

### 5. Wait for Build

- Hugging Face will automatically build your Docker container
- Monitor the build logs in the "Logs" tab
- First build may take 5-10 minutes

### 6. Test Your Deployment

Once deployed, visit:

- **API Endpoint**: `https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space`
- **Interactive Docs**: `https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space/docs`
- **Health Check**: `https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space/health`

## 🧪 Testing the API

### Using Swagger UI

Visit `/docs` on your Space URL for interactive API documentation.

### Using cURL

```bash
# Health check
curl https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space/health

# Generate content
curl -X POST "https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Introduction to Machine Learning",
    "audience": "beginner",
    "max_duration_sec": 180,
    "render_formats": ["slides", "diagrams", "audio"]
  }'
```

### Using Python

```python
import requests

url = "https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space/generate"
payload = {
    "topic": "Binary Search Algorithm",
    "audience": "intermediate",
    "max_duration_sec": 240,
    "render_formats": ["slides", "diagrams"]
}

response = requests.post(url, json=payload)
print(response.json())
```

## ⚙️ Hardware Requirements

### CPU (Free Tier)
- **Suitable for**: API-based LLM providers (OpenAI, Anthropic, Together)
- **Not suitable for**: Local model inference (Mistral-7B)

### GPU (Paid)
- **Suitable for**: Local model inference + all features
- **Required for**: Running Mistral-7B locally
- **Recommended**: T4 or better

## 🔒 Security Best Practices

1. **Never commit API keys**: Always use Space environment variables
2. **Use secrets**: Mark sensitive variables as "Secret" in Space settings
3. **Rotate keys**: Regularly rotate your API keys
4. **Monitor usage**: Check your LLM provider dashboards for usage

## 🐛 Troubleshooting

### Build Fails

- Check `Dockerfile` syntax
- Verify all required files are uploaded
- Review build logs in Space's "Logs" tab

### Runtime Errors

- Check Space logs for stack traces
- Verify environment variables are set correctly
- Test API keys separately

### Memory Issues

- Reduce `MAX_TOKENS` in environment variables
- Upgrade to larger hardware tier
- Use API providers instead of local models

### Timeout on First Request

- First request may take longer (cold start)
- Consider using persistent hardware tier
- Implement API warmup strategies

## 📊 Monitoring

Monitor your Space:
- **Logs**: Real-time logs in Space's "Logs" tab
- **Health**: `/health` endpoint for status checks
- **Stats**: `/health` returns LLM provider stats

## 🔄 Updating Your Space

```bash
# Pull latest changes
git pull

# Make your changes
# ... edit files ...

# Push updates
git add .
git commit -m "Update: description of changes"
git push
```

The Space will automatically rebuild and redeploy.

## 📚 Additional Resources

- [Hugging Face Spaces Documentation](https://huggingface.co/docs/hub/spaces)
- [Docker Spaces Guide](https://huggingface.co/docs/hub/spaces-sdks-docker)
- [EduForge API Guide](./API_GUIDE.md)
- [LLM Provider Guide](./LLM_PROVIDER_GUIDE.md)

## 💡 Tips for Production

1. **Use persistent storage**: Enable persistent storage for generated outputs
2. **Set up monitoring**: Use health checks and logging
3. **Optimize costs**: Choose appropriate hardware tier
4. **Rate limiting**: Implement rate limiting for public APIs
5. **Caching**: Cache frequent requests to reduce LLM calls

## 🆘 Support

- **Issues**: Open an issue in the repository
- **Community**: Join Hugging Face Discord
- **Documentation**: Check [API_GUIDE.md](./API_GUIDE.md)

---

Built with ❤️ for educators and learners worldwide.
