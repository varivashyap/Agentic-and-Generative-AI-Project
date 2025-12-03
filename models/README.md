# Models Directory

This directory is for storing GGUF language models used by the Study Assistant.

## Quick Start - Download a Model

### Option 1: Small Model (Recommended for testing)
```bash
# Download a smaller model for testing (around 1-2GB)
cd models
curl -L -o phi-3-mini-4k-instruct.Q4_K_M.gguf \
  "https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf"
```

### Option 2: Medium Model (Good balance)
```bash
# Download Mistral 7B (around 4GB)
cd models
curl -L -o mistral-7b-instruct-v0.2.Q4_K_M.gguf \
  "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
```

### Option 3: Using wget (if you prefer)
```bash
cd models
wget https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf \
  -O phi-3-mini-4k-instruct.Q4_K_M.gguf
```

## After Downloading

1. **Update config if needed** (in `config/config.yaml`):
   ```yaml
   llm:
     local:
       model: "your-downloaded-model-name"  # without .gguf extension
   ```

2. **Test the system**:
   ```bash
   python src/cli.py --help
   ```

3. **Test CrewAI integration**:
   ```bash
   python examples/crewai_cli.py --status
   ```

## Supported Model Formats
- **GGUF models** (recommended)
- **Quantized models** (Q4_K_M, Q5_K_M, Q8_0, etc.)
- **Size range**: 1GB - 20GB depending on your hardware

## Where to Find Models
- [HuggingFace GGUF Models](https://huggingface.co/models?library=gguf)
- [TheBloke's GGUF Collection](https://huggingface.co/TheBloke)
- [Microsoft Phi-3 Models](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf)

## Hardware Requirements
- **RAM**: Model size + 2-4GB extra
- **CPU**: Any modern processor (Apple Silicon recommended)
- **Storage**: Model file size + working space

## Current Status
📁 Directory created and ready for models
⬇️ Download a model using the commands above to get started!