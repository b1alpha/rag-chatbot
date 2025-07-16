# 🚀 RAG-Chatbot with Ollama - Quickstart Guide

> **Transform your RAG system to run locally with Ollama instead of OpenAI APIs!**

This guide will walk you through setting up your RAG-powered static analysis system to run completely locally using Ollama, eliminating the need for external API calls and ensuring complete privacy.

## 📋 Prerequisites

- macOS (with Apple Silicon recommended for best performance)
- Homebrew installed
- Python 3.9+ with virtual environment
- VS Code (optional but recommended)

## 🎯 What You'll Get

✅ **Complete Privacy** - No data leaves your machine  
✅ **Zero API Costs** - No more OpenAI API bills  
✅ **Offline Operation** - Works without internet  
✅ **Full Control** - Your own models and parameters  
✅ **Fast Performance** - Metal acceleration on Apple Silicon

## 🔧 Step 1: Install Ollama

Install Ollama using Homebrew:

```bash
brew install ollama
```

## 🐲 Step 2: Download and Test a Model

Download a lightweight model for testing:

```bash
ollama pull llama3.2:1b
```

Verify the model is available:

```bash
ollama list
```

You should see output like:

```
NAME           ID              SIZE      MODIFIED
llama3.2:1b    baf6a787fdff    1.3 GB    2 minutes ago
```

## 🚀 Step 3: Start the Ollama Server

In a terminal window, start the Ollama server (keep this running):

```bash
ollama serve
```

You should see output indicating the server is listening on `127.0.0.1:11434`.

## 🧪 Step 4: Test Ollama Connection

In a **new terminal window**, test the connection:

```bash
curl -s http://localhost:11434/api/tags | python -m json.tool
```

This should return JSON showing your available models.

## 🔨 Step 5: Set Up Your Python Environment

Navigate to your project directory and activate your virtual environment:

```bash
cd /path/to/your/rag-chatbot
source .venv/bin/activate  # or however you activate your venv
```

Install the required packages:

```bash
pip install langchain-ollama requests
```

## 🎪 Step 6: Test the Integration

Run the integration test:

```bash
python test_ollama_integration.py
```

Expected output:

```
🧪 Testing Ollama RAG Integration
==================================================

1. Testing Ollama connection...
✅ Ollama is running
📋 Available models: ['llama3.2:1b']

2. Testing simple question...
Question: What is Python?
Answer: Python is a high-level programming language...
✅ Simple question test passed

3. Testing RAG-specific question...
Question: What is the ideal test pyramid distribution?
Answer: The ideal test pyramid distribution for a microservice...
✅ RAG-specific question test passed

🎉 All tests passed! Your Ollama RAG integration is working.
```

## 🎯 Step 7: Run the Demo

Test the full static analysis system:

```bash
python demo_ollama_analysis.py
```

This will demonstrate:

- RAG-powered test level descriptions
- Quality context loading
- Test distribution scoring
- Repository analysis
- Context-aware recommendations

## 🏗️ Step 8: Use Your RAG System

Now you can use your RAG system in three ways:

### A. Direct API Usage

```python
from app.rag_pipeline_ollama import get_answer

# Ask any question about your quality documentation
answer = get_answer("What is the ideal test pyramid distribution?")
print(answer)
```

### B. Static Analysis

```python
from app.static_analysis import StaticAnalyzer

analyzer = StaticAnalyzer()
description = analyzer._get_test_level_description('unit')
print(description)
```

### C. Full Repository Analysis

```python
from app.static_analysis import analyze_repository

report = analyze_repository("/path/to/your/repo")
print(report)
```

## 🔄 Daily Usage Workflow

1. **Start Ollama** (once per session):

   ```bash
   ollama serve
   ```

2. **Run your scripts** in another terminal:

   ```bash
   python your_analysis_script.py
   ```

3. **Stop when done** (Ctrl+C in the ollama serve terminal)

## 🎛️ Configuration Options

### Change Model

To use a different model:

```bash
# Download a more powerful model
ollama pull llama3.1:8b

# Or a different model entirely
ollama pull mistral:7b
```

Then update your scripts to use the new model:

```python
# In rag_pipeline_ollama.py, change the default model
def get_answer_ollama(question: str, model_name: str = "llama3.1:8b"):
```

### Adjust Performance

Edit the parameters in `rag_pipeline_ollama.py`:

```python
payload = {
    "model": model_name,
    "prompt": prompt,
    "stream": False,
    "options": {
        "temperature": 0.3,    # Lower = more focused, Higher = more creative
        "top_p": 0.9,          # Nucleus sampling
        "max_tokens": 1000     # Response length limit
    }
}
```

## 🛠️ Troubleshooting

### Deprecation Warning

If you see warnings about Chroma being deprecated, you can silence them:

```python
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
```

### Model Not Found

```bash
# Check available models
ollama list

# Pull the required model
ollama pull llama3.2:1b
```

### Connection Refused

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start it
ollama serve
```

### Slow Performance

- Use smaller models (1b instead of 8b)
- Reduce max_tokens in configuration
- Ensure you have sufficient RAM

### Import Errors

```bash
# Install missing packages
pip install langchain-ollama requests langchain-community langchain-openai
```

### "max_tokens" Warning

You may see warnings about `max_tokens` being invalid. This is normal and doesn't affect functionality.

## 📝 Example Usage Script

Create a simple script to test your setup:

```python
#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Silence deprecation warnings
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

from rag_pipeline_ollama import get_answer

# Test the system
answer = get_answer("What is unit testing?")
print(f"Answer: {answer[:200]}...")
```

Run it:

```bash
python example_usage.py
```

## 🎉 Success!

You now have a fully local RAG system that:

- ✅ Runs completely offline
- ✅ Costs nothing to operate
- ✅ Keeps your data private
- ✅ Provides context-aware analysis
- ✅ Integrates with your existing workflow

### 🧪 Verification Checklist

Run these commands to verify everything is working:

```bash
# 1. Check Ollama is running
curl -s http://localhost:11434/api/tags

# 2. Test the integration
python test_ollama_integration.py

# 3. Run the demo
python demo_ollama_analysis.py

# 4. Try the example
python example_usage.py
```

All should complete successfully with helpful output!

## 🔗 Next Steps

1. **Explore Different Models**: Try `ollama pull codellama:7b` for code-specific tasks
2. **Customize Prompts**: Modify the prompt templates in `rag_pipeline_ollama.py`
3. **Add New Features**: Extend the static analysis with more RAG-powered insights
4. **Scale Up**: Use larger models for more sophisticated analysis

## 📚 Additional Resources

- [Ollama Documentation](https://ollama.ai/docs)
- [Available Models](https://ollama.ai/library)
- [LangChain Ollama Integration](https://python.langchain.com/docs/integrations/llms/ollama)

---

**Happy Local RAG Analysis!** 🎊
