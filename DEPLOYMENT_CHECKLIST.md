# 🚀 Hugging Face Spaces Deployment Checklist

Use this checklist to ensure a smooth deployment to Hugging Face Spaces.

## ☑️ Pre-Deployment

- [ ] **Test Locally** - Run `docker build` and `docker run` to verify everything works
- [ ] **Check API Keys** - Ensure you have valid API keys for at least one LLM provider
- [ ] **Review Files** - Verify all essential files are present:
  - [ ] `Dockerfile`
  - [ ] `main.py`
  - [ ] `requirements.txt`
  - [ ] All Python modules in project root
  - [ ] `README.md` in Eduforge/ folder (with proper YAML frontmatter)

## 🔐 API Keys & Credentials

Prepare your API keys (you'll need at least one):

- [ ] **OpenAI API Key** ([Get it here](https://platform.openai.com/api-keys))
  - Key format: `sk-...`
  - Test it: `curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"`

- [ ] **Anthropic API Key** ([Get it here](https://console.anthropic.com/))
  - Key format: `sk-ant-...`
  - Test it: Check in Anthropic console

- [ ] **Together AI API Key** ([Get it here](https://api.together.xyz/settings/api-keys))
  - Key format: varies
  - Test it: Check in Together AI console

## 🏗️ Create Hugging Face Space

1. **Create Space**
   - [ ] Go to [huggingface.co/spaces](https://huggingface.co/spaces)
   - [ ] Click "Create new Space"
   - [ ] Choose a unique name (e.g., `eduforge`)
   - [ ] Select **Docker** as SDK
   - [ ] Choose license (e.g., MIT)
   - [ ] Set visibility (Public or Private)

2. **Hardware Selection**
   - [ ] Start with **CPU basic** (free tier)
   - [ ] For production, consider **CPU Upgrade** or **GPU** based on load
   - [ ] Note: Local models (Mistral-7B) require GPU

## 📤 Upload Files

### Option A: Git (Recommended)

```bash
# 1. Clone your Space repository
git clone https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
cd YOUR_SPACE_NAME

# 2. Copy all files from your project
cp -r /path/to/Eduforge_Multimodal_project/* .

# 3. Verify critical files
ls -la Dockerfile main.py requirements.txt

# 4. Commit and push
git add .
git commit -m "Initial deployment"
git push
```

- [ ] Repository cloned
- [ ] Files copied
- [ ] Critical files verified
- [ ] Committed and pushed

### Option B: Web Interface

- [ ] Navigate to Space's "Files" tab
- [ ] Upload all files from project root
- [ ] Verify `Dockerfile` is present
- [ ] Verify `README.md` with YAML frontmatter is present

## ⚙️ Configure Environment Variables

Go to Space Settings → Variables and add:

### Required Variables

- [ ] `LLM_PROVIDER` = `auto` (or `openai`, `anthropic`, `together`)
- [ ] Add at least one API key:
  - [ ] `OPENAI_API_KEY` (mark as Secret ✅)
  - [ ] `ANTHROPIC_API_KEY` (mark as Secret ✅)
  - [ ] `TOGETHER_API_KEY` (mark as Secret ✅)

### Optional Variables

- [ ] `LLM_MODEL` - Specific model to use (e.g., `gpt-4-turbo`)
- [ ] `LLM_FALLBACK_CHAIN` - Comma-separated fallback providers
- [ ] `MAX_TOKENS` - Maximum tokens per generation (default: 2000)
- [ ] `TEMPERATURE` - Sampling temperature (default: 0.7)

## 🔨 Build & Deploy

- [ ] **Wait for Build** - Monitor in Space's "Logs" tab
  - First build takes 5-10 minutes
  - Watch for any errors during Docker build
- [ ] **Check Build Success** - Space status should show "Running"
- [ ] **View Logs** - Check for startup messages

## ✅ Post-Deployment Testing

### 1. Health Check

```bash
curl https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space/health
```

Expected response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "provider": "openai",
  "model": "gpt-4-turbo"
}
```

- [ ] Health check returns 200 OK
- [ ] Provider is correctly identified
- [ ] Model name is shown

### 2. API Documentation

- [ ] Visit `https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space/docs`
- [ ] Swagger UI loads correctly
- [ ] All endpoints are visible

### 3. Generate Content Test

```bash
curl -X POST "https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Binary Search",
    "audience": "beginner",
    "max_duration_sec": 120,
    "render_formats": ["slides"]
  }'
```

- [ ] Request completes successfully
- [ ] Returns `"success": true`
- [ ] Content is generated
- [ ] Response time is reasonable (<30s)

### 4. Download Files Test

```bash
# From the previous response, get session_id and filename
curl "https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space/outputs/{session_id}/{filename}"
```

- [ ] Files download successfully
- [ ] HTML slides render correctly
- [ ] Diagrams display properly

## 🐛 Troubleshooting

### Build Fails

- [ ] Check Dockerfile syntax
- [ ] Review build logs for specific errors
- [ ] Verify all dependencies in requirements.txt are available
- [ ] Check for any missing system dependencies

### Runtime Errors

- [ ] Review Space logs for Python exceptions
- [ ] Verify environment variables are set correctly
- [ ] Test API keys separately using curl
- [ ] Check provider API status pages

### Slow Performance

- [ ] First request may be slow (cold start)
- [ ] Consider upgrading hardware tier
- [ ] Monitor Space performance metrics
- [ ] Check LLM provider rate limits

### API Key Issues

- [ ] Verify keys are marked as "Secret"
- [ ] Check keys haven't expired
- [ ] Verify correct key format
- [ ] Test keys using provider's API directly

## 📊 Monitoring

Set up regular monitoring:

- [ ] Bookmark Space URL
- [ ] Monitor Space logs regularly
- [ ] Check LLM provider usage dashboards
- [ ] Set up alerts for failures (if using external monitoring)

## 📝 Documentation

- [ ] Update Space README with usage examples
- [ ] Add badge to your GitHub repo (optional)
- [ ] Share Space URL with users
- [ ] Document any custom configuration

## 🎉 Going Live

- [ ] Set Space visibility (Public/Private)
- [ ] Pin important Spaces to profile
- [ ] Share on social media (optional)
- [ ] Monitor initial usage and feedback

## 🔄 Future Updates

To update your Space:

```bash
# Pull latest changes
git pull

# Make your updates
# ... edit files ...

# Push changes
git add .
git commit -m "Update: description of changes"
git push
```

- [ ] Test updates locally first
- [ ] Document breaking changes
- [ ] Monitor logs after deployment

---

## 📚 Resources

- [Hugging Face Spaces Docs](https://huggingface.co/docs/hub/spaces)
- [Docker Spaces Guide](https://huggingface.co/docs/hub/spaces-sdks-docker)
- [Full Deployment Guide](./HF_DEPLOYMENT_GUIDE.md)
- [API Guide](./API_GUIDE.md)
- [LLM Provider Guide](./LLM_PROVIDER_GUIDE.md)

---

**Questions?** Check the troubleshooting section in [HF_DEPLOYMENT_GUIDE.md](./HF_DEPLOYMENT_GUIDE.md) or open an issue.
