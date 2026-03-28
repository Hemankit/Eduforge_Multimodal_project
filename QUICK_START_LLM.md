# LLM Setup - Simple Guide

## 🎯 Two Options

Your pipeline supports two LLM options:

| Option | Model | Cost | Setup | Use Case |
|--------|-------|------|-------|----------|
| **Local** | Mistral 7B | Free | GPU required | Development, testing, privacy |
| **API** | Llama 3.3 70B | ~$0.88/1M tokens | API key needed | Production, better quality |

## ⚡ Quick Start

### Option 1: Local (Default)

**No setup needed!** Just run:

```python
from llm_client import LLMClient

# Uses local Mistral 7B
client = LLMClient.create(provider="local")
response = client.generate_content("Explain Python")
```

**Requirements:**
- GPU with 16GB+ VRAM (or 32GB+ RAM for CPU)
- Packages: `transformers`, `torch`, `accelerate` (already in requirements.txt)

### Option 2: Together AI (Llama 3.3 70B)

**1. Get API key** (free $25 credit): https://api.together.xyz/

**2. Set environment variable:**
```bash
# In .env file
LLM_PROVIDER=together
TOGETHER_API_KEY=your_key_here
```

**3. Use it:**
```python
from llm_client import LLMClient

# Uses Llama 3.3 70B via Together AI
client = LLMClient.create(provider="together")
response = client.generate_content("Explain quantum computing")
```

**Requirements:**
- API key from Together AI
- Package: `langchain-together` (install: `pip install langchain-together`)

## 📦 Installation

```bash
# Core dependencies (includes local support)
pip install -r requirements.txt

# Add Together AI support (optional)
pip install langchain-together
```

## 🔧 Configuration

### Method 1: Environment Variables (.env file)
```env
# Local (default, no API key needed)
LLM_PROVIDER=local

# OR Together AI (needs API key)
LLM_PROVIDER=together
TOGETHER_API_KEY=your_key_here
```

### Method 2: Direct in Code
```python
# Local
client = LLMClient.create(provider="local")

# Together AI with API key
client = LLMClient.create(
    provider="together",
    api_key="your_key_here"
)
```

## 🆚 Comparison

### Local Mistral 7B
- ✅ **Free** (no API costs)
- ✅ **Private** (runs on your machine)
- ✅ **Fast** (if you have good GPU)
- ❌ Requires GPU/RAM
- ❌ Lower quality than 70B models
- **Context**: 8K tokens

### Together AI Llama 3.3 70B
- ✅ **Better quality** (70B parameters)
- ✅ **No GPU needed** (cloud-hosted)
- ✅ **Huge context** (128K tokens!)
- ✅ **Fast Turbo inference**
- ❌ Costs ~$0.88 per 1M tokens
- ❌ Needs internet connection

## 💰 Cost Estimate (Together AI)

Typical educational content generation:
- Input: ~5K tokens (prompt + schema)
- Output: ~3K tokens (content)
- **Cost per generation**: ~$0.007 (less than 1 cent!)
- **100 generations**: ~$0.70
- **Free tier**: $25 credit = ~3,500 generations

## 🔄 Automatic Fallback

System automatically falls back to local if API fails:

```python
# Try Together AI, fall back to local on failure
client = LLMClient.create(
    provider="together",
    fallback_to_local=True  # Default behavior
)
```

## 📊 Usage Statistics

Track your usage:
```python
client = LLMClient.create(provider="together")

# Make some calls
client.generate_content("...")

# Check stats
stats = client.get_stats()
print(f"Total cost: ${stats['total_cost_usd']:.4f}")
print(f"Total tokens: {stats['total_tokens']}")
```

## ✅ Backward Compatibility

Old code still works:
```python
# Legacy method (still supported)
client = LLMClient.from_pretrained("mistralai/Mistral-7B-Instruct-v0.3")
```

## 🚀 Recommended Setup

**For development/testing:**
```env
LLM_PROVIDER=local
```

**For demos/production:**
```env
LLM_PROVIDER=together
TOGETHER_API_KEY=your_key
```

## 🧪 Test Your Setup

```bash
python test_llm_providers.py
```

---

**That's it!** Pick local (free) or Together AI (better quality), and you're ready to generate educational content. 🎓
