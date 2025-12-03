# Setup Guide - Study Assistant

Complete setup guide from downloading models to running the MCP server and frontend.

---

## 📋 Prerequisites

- **Python 3.10+** (required)
- **4GB+ RAM** (8GB+ recommended)
- **~15GB disk space** (for models and data)
- **NVIDIA GPU with 4GB+ VRAM** (recommended, optimized for 4GB GPU)
- **Internet connection** (for initial model download and Google sign-in)
- **Google Account** (optional, for Calendar integration)

---

## 🚀 Quick Setup (Recommended)

### Option 1: MCP Server with Web Interface

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd study-assistant

# 2. Run the setup script (one-time)
./setup_mcp_server.sh

# This will:
# - Check Python version
# - Create virtual environment (aivenv/)
# - Install all dependencies
# - Create necessary directories
# - Generate start/stop scripts

# 3. Start the MCP server
./start_mcp_server.sh

# 4. In a new terminal, start the frontend
./start_frontend.sh

# 5. Open your browser
# Frontend: http://localhost:8080
# API: http://localhost:5000
```

**That's it!** The system is ready to use.

---

## 📥 Model Download

### Automatic Download (Recommended)

Most models download automatically on first use:
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2 (auto-downloads)
- **Whisper**: openai/whisper-large (auto-downloads)
- **Reranker**: cross-encoder/ms-marco-MiniLM-L-6-v2 (auto-downloads)

### Manual LLM Download (One-time)

The LLM models need to be downloaded manually. You can download one or all three:

```bash
# Create models directory
mkdir -p models

# Install HuggingFace CLI
pip install huggingface-hub

# Download Mistral-7B-Instruct (RECOMMENDED - Best Quality, ~4.1GB)
huggingface-cli download TheBloke/Mistral-7B-Instruct-v0.2-GGUF \
  mistral-7b-instruct-v0.2.Q4_K_M.gguf \
  --local-dir models/ \
  --local-dir-use-symlinks False

# Download Qwen2-1.5B (Fast & Efficient, ~941MB)
huggingface-cli download Qwen/Qwen2-1.5B-Instruct-GGUF \
  qwen2-1.5b-instruct.Q4_K_M.gguf \
  --local-dir models/ \
  --local-dir-use-symlinks False

# Download TinyLlama-1.1B (Ultra Fast, ~638MB)
huggingface-cli download TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF \
  tinyllama-1.1b-chat.Q4_K_M.gguf \
  --local-dir models/ \
  --local-dir-use-symlinks False
```

**Model Comparison**:

| Model | Size | VRAM | Speed | Quality | Best For |
|-------|------|------|-------|---------|----------|
| **Mistral 7B** | 4.1GB | ~4GB | Medium | Excellent | Summary, Quiz, Flashcards (Default) |
| **Qwen2 1.5B** | 941MB | ~1GB | Very Fast | Good | Chatbot, Flashcards, Summary |
| **TinyLlama 1.1B** | 638MB | ~800MB | Ultra Fast | Fair | Chatbot, Testing |

**Note**: You can switch between models in the Settings UI (⚙️ icon) without restarting the server.

### Update Configuration

The default configuration in `config/config.yaml` is already optimized for 4GB GPU:

```yaml
llm:
  provider: "local"
  local:
    model: "mistral-7b-instruct-v0.2.Q4_K_M"  # Default model
    model_path: "models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
    n_ctx: 2048  # Reduced for 4GB GPU (was 4096)
    n_gpu_layers: 35  # Set to 0 for CPU-only
    max_tokens: 512  # Reduced for 4GB GPU (was 1000)
```

**Important Notes:**
- **Model Selection**: You can switch models in the Settings UI (⚙️ icon) without editing config.yaml
- **4GB GPU Optimization**:
  - `n_ctx: 2048` - Reduced context window to prevent memory overflow
  - `max_tokens: 512` - Limited generation length for memory safety
- **llama-cpp-python Version**: Requires >=0.3.16 for Qwen2 support (auto-installed by setup script)

---

## 🔧 Manual Setup (Alternative)

If you prefer manual setup or the script doesn't work:

### 1. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv aivenv

# Activate it
source aivenv/bin/activate  # On Windows: aivenv\Scripts\activate
```

### 2. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# For GPU support (optional)
pip install faiss-gpu
```

### 3. Create Directories

```bash
# Create necessary directories
mkdir -p data/uploads data/outputs data/cache data/training data/preprocessed
mkdir -p data/cache/sessions
mkdir -p results/models results/metrics results/hparams
mkdir -p models
```

### 4. Download Models

Follow the "Manual LLM Download" section above.

### 5. Test Installation

```bash
# Test basic pipeline
python examples/basic_usage.py

# Test MCP server
python test_mcp_server.py
```

---

## 🌐 Running the System

### MCP Server + Frontend

```bash
# Terminal 1: Start MCP server
./start_mcp_server.sh
# Server runs on http://localhost:5000

# Terminal 2: Start frontend
./start_frontend.sh
# Frontend runs on http://localhost:8080
```

### Python API Only

```python
from src.pipeline import StudyAssistantPipeline

# Initialize
pipeline = StudyAssistantPipeline()

# Ingest documents
pipeline.ingest_pdf("data/uploads/lecture.pdf")
pipeline.ingest_audio("data/uploads/lecture.mp3")

# Generate study materials
summaries = pipeline.generate_summaries()
flashcards = pipeline.generate_flashcards()
quizzes = pipeline.generate_quizzes()

# Export
pipeline.export_anki("output.apkg")
```

---

## ✅ Verification

### Check Installation

```bash
# Activate environment
source aivenv/bin/activate

# Check Python version
python --version  # Should be 3.10+

# Check installed packages
pip list | grep -E "torch|faiss|transformers|llama-cpp"

# Check models directory
ls -lh models/
```

### Test MCP Server

```bash
# Start server
./start_mcp_server.sh

# In another terminal, test health endpoint
curl http://localhost:5000/health

# Should return: {"status": "healthy", ...}
```

### Test Frontend

```bash
# Start frontend
./start_frontend.sh

# Open browser to http://localhost:8080
# You should see the upload interface
```

---

## 🐛 Troubleshooting

### Issue: "Python version too old"

```bash
# Install Python 3.10+
# On Ubuntu/Debian:
sudo apt update
sudo apt install python3.10 python3.10-venv

# On macOS:
brew install python@3.10
```

### Issue: "pip install fails"

```bash
# Upgrade pip
pip install --upgrade pip setuptools wheel

# Try installing again
pip install -r requirements.txt
```

### Issue: "Model not found"

```bash
# Check models directory
ls -lh models/

# Re-download model
huggingface-cli download TheBloke/Mistral-7B-Instruct-v0.2-GGUF \
  mistral-7b-instruct-v0.2.Q4_K_M.gguf \
  --local-dir models/ --local-dir-use-symlinks False
```

### Issue: "Port 5000 already in use"

```bash
# Find process using port 5000
lsof -i :5000

# Kill it
kill -9 <PID>

# Or use different port
python -m mcp_server.server --port 5001
```

### Issue: "Out of memory"

```bash
# Use smaller model (Phi-3 or Gemma)
# Or reduce batch size in config/config.yaml:
embeddings:
  batch_size: 8  # Reduce from 32
```

### Issue: "CUDA not available"

```bash
# Check CUDA
python -c "import torch; print(torch.cuda.is_available())"

# If False, install CUDA toolkit or use CPU
# Set in config/config.yaml:
system:
  device: "cpu"
```

---

## 📊 System Requirements

### Minimum (4GB GPU - Optimized)
- Python 3.10+
- 4GB RAM
- 4GB VRAM (NVIDIA GPU: GTX 1650, RTX 3050)
- 15GB disk space
- Processing time: ~2-3 min per quiz, ~1-2 min per summary
- **Note**: Optimized with reduced context window (2048) and token limits (512)

### Recommended (6GB+ GPU)
- Python 3.10+
- 8GB RAM
- 6GB+ VRAM (NVIDIA GPU: RTX 3060, RTX 4060)
- 20GB disk space
- Processing time: ~1-2 min per quiz, ~30-60 sec per summary

### High Performance (8GB+ GPU)
- Python 3.10+
- 16GB RAM
- 8GB+ VRAM (NVIDIA GPU: RTX 3070, RTX 4070)
- 30GB disk space
- Processing time: ~30-60 sec per quiz, ~15-30 sec per summary

---

## 🎯 Next Steps

After setup is complete:

1. **Sign in with Google**: Open http://localhost:8080 and sign in (first time only)
2. **Test with sample data**: Upload a PDF or audio file via drag & drop
3. **Try all features**:
   - **📝 Summary**: Generate document summary
   - **❓ Quiz**: Generate 10 MCQ questions (optimized text parser)
   - **🎴 Flashcards**: Generate study flashcards
   - **💬 Chatbot**: Ask questions about your document (RAG-powered)
   - **📅 Calendar**: View/manage Google Calendar events
4. **Explore the API**: See [MCP_SERVER.md](MCP_SERVER.md) for API documentation
5. **Customize configuration**: Edit `config/config.yaml` to adjust settings
6. **Optional: Finetune models**: See advanced training section in README.md
7. **Optional: Setup Google Calendar**: See [GOOGLE_CALENDAR_SETUP.md](GOOGLE_CALENDAR_SETUP.md)

---

## 📅 Optional: Google Calendar Integration

To enable the Calendar feature:

1. **Create Google Cloud Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable Google Calendar API

2. **Create OAuth Credentials**:
   - Create OAuth 2.0 Client ID (Web application)
   - Add redirect URI: `http://localhost:5000/auth/google/callback`
   - Download credentials JSON

3. **Configure Application**:
   ```bash
   # Move credentials to config directory
   mv ~/Downloads/client_secret_*.json config/google_credentials.json

   # Install Google API dependencies (if not already installed)
   source aivenv/bin/activate
   pip install -r requirements.txt

   # Restart MCP server
   ./stop_mcp_server.sh
   ./start_mcp_server.sh
   ```

4. **Test Calendar Integration**:
   - Open http://localhost:8080
   - Click "Calendar" mode
   - Sign in with Google
   - View your calendar events

**For detailed setup instructions, see [GOOGLE_CALENDAR_SETUP.md](GOOGLE_CALENDAR_SETUP.md)**

---

## 📚 Additional Resources

- **[README.md](README.md)** - Project overview
- **[MCP_SERVER.md](MCP_SERVER.md)** - MCP server documentation
- **[PROJECT_SPECIFICATION.md](PROJECT_SPECIFICATION.md)** - Technical details
- **[PROJECT_STATUS.md](PROJECT_STATUS.md)** - Implementation status
- **[GOOGLE_CALENDAR_SETUP.md](GOOGLE_CALENDAR_SETUP.md)** - Calendar integration guide

---

**Setup complete! Start using the Study Assistant now.** 🚀

