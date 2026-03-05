# Local LLM Setup with Ollama

The Academic Research Assistant can use local LLMs via Ollama instead of Google's API.

## Prerequisites

1. **Install Ollama**: https://ollama.ai/download
2. **Pull a model**:
   ```bash
   ollama pull llama3.1:8b
   # or for better quality:
   ollama pull llama3.1:70b
   ```

## Configuration

### Option 1: Environment Variable
Set in your `.env` file:
```bash
USE_LOCAL_LLM=true
OLLAMA_MODEL=llama3.1:8b
OLLAMA_BASE_URL=http://localhost:11434
```

### Option 2: Direct Code Change
Edit `agents.py` and replace the Gemini model with Ollama:

```python
from google.adk.models.ollama_llm import Ollama

# Instead of:
# model=Gemini(model=DEFAULT_MODEL_NAME, retry_options=retry_config)

# Use:
model=Ollama(model="llama3.1:8b", base_url="http://localhost:11434")
```

## Recommended Models

| Model | Size | Quality | Speed | Use Case |
|-------|------|---------|-------|----------|
| `llama3.1:8b` | 4.7GB | Good | Fast | Development/Testing |
| `llama3.1:70b` | 40GB | Excellent | Slow | Production |
| `mistral:7b` | 4.1GB | Good | Fast | Lightweight |
| `qwen2.5:14b` | 9GB | Very Good | Medium | Balanced |

## Trade-offs

**Local LLM (Ollama)**
- ✅ No API costs
- ✅ Complete privacy
- ✅ No rate limits
- ✅ Works offline
- ❌ Requires powerful hardware (16GB+ RAM for 8B models)
- ❌ Slower than cloud APIs
- ❌ Lower quality than Gemini 2.5

**Google Gemini API**
- ✅ Very fast
- ✅ High quality
- ✅ No local resources needed
- ✅ Free tier available
- ❌ Requires internet
- ❌ API costs for heavy use
- ❌ Rate limits

## Quick Test

```bash
# Start Ollama
ollama serve

# In another terminal, test the model
ollama run llama3.1:8b "What are knowledge graphs?"
```

If that works, you can use it with the Academic Research Assistant!
