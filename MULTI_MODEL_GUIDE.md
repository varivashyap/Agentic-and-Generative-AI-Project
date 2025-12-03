# Multi-Model Support Guide

## 🎯 Overview

Your Study Assistant now supports **multiple LLM models** optimized for 4GB GPU! Users can select different models based on their needs - from ultra-fast lightweight models to high-quality larger models.

---

## 🤖 Available Models

### 1. **Mistral 7B Instruct** (Default)
- **Size:** 7B parameters
- **VRAM:** ~4GB
- **Speed:** Medium
- **Quality:** Excellent ⭐⭐⭐⭐⭐
- **Best for:** Summaries, Quizzes, Flashcards
- **File:** `mistral-7b-instruct-v0.2.Q4_K_M.gguf`

**Pros:** Best overall quality, comprehensive understanding  
**Cons:** Slower, uses more memory

---

### 2. **Phi-3 Mini** (Microsoft)
- **Size:** 3.8B parameters
- **VRAM:** ~2.5GB
- **Speed:** Fast
- **Quality:** Very Good ⭐⭐⭐⭐
- **Best for:** Chatbot, Summaries, Quizzes
- **File:** `phi-3-mini-4k-instruct.Q4_K_M.gguf`

**Pros:** Excellent quality-to-speed ratio, efficient  
**Cons:** Slightly lower quality than Mistral 7B

---

### 3. **Gemma 2B** (Google)
- **Size:** 2B parameters
- **VRAM:** ~1.5GB
- **Speed:** Very Fast
- **Quality:** Good ⭐⭐⭐
- **Best for:** Chatbot, Flashcards
- **File:** `gemma-2b-it.Q4_K_M.gguf`

**Pros:** Very fast, low memory usage  
**Cons:** Lower quality for complex tasks

---

### 4. **Qwen2 1.5B** (Alibaba)
- **Size:** 1.5B parameters
- **VRAM:** ~1GB
- **Speed:** Very Fast
- **Quality:** Good ⭐⭐⭐
- **Best for:** Chatbot, Simple tasks
- **File:** `qwen2-1.5b-instruct.Q4_K_M.gguf`

**Pros:** Ultra-efficient, multilingual support  
**Cons:** Best for simpler tasks

---

### 5. **TinyLlama 1.1B**
- **Size:** 1.1B parameters
- **VRAM:** ~800MB
- **Speed:** Ultra Fast
- **Quality:** Fair ⭐⭐
- **Best for:** Testing, Simple chatbot
- **File:** `tinyllama-1.1b-chat.Q4_K_M.gguf`

**Pros:** Extremely fast, minimal memory  
**Cons:** Lower quality, best for simple tasks only

---

## 📥 How to Download Models

### Option 1: HuggingFace (Recommended)

```bash
# Create models directory
mkdir -p models

# Download Mistral 7B (Default - already have this)
# Already downloaded: models/mistral-7b-instruct-v0.2.Q4_K_M.gguf

# Download Phi-3 Mini
wget https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf \
  -O models/phi-3-mini-4k-instruct.Q4_K_M.gguf

# Download Gemma 2B
wget https://huggingface.co/google/gemma-2b-it-GGUF/resolve/main/gemma-2b-it.Q4_K_M.gguf \
  -O models/gemma-2b-it.Q4_K_M.gguf

# Download Qwen2 1.5B
wget https://huggingface.co/Qwen/Qwen2-1.5B-Instruct-GGUF/resolve/main/qwen2-1_5b-instruct-q4_k_m.gguf \
  -O models/qwen2-1.5b-instruct.Q4_K_M.gguf

# Download TinyLlama 1.1B
wget https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf \
  -O models/tinyllama-1.1b-chat.Q4_K_M.gguf
```

### Option 2: Kaggle

Visit [Kaggle Models](https://www.kaggle.com/models) and search for GGUF versions of the models above.

---

## 🎨 How to Use (Frontend)

### 1. Open Settings
Click the **⚙️ Settings** button in the top-right corner.

### 2. Select Model
In the **Model Selection** section, choose your preferred model from the dropdown.

### 3. View Model Info
The model information panel will show:
- Model size and parameters
- VRAM usage
- Speed rating
- Quality rating
- Recommended use cases

### 4. Save Settings
Click **Save Settings** to apply your selection.

### 5. Generate Content
The selected model will be used for all generation tasks (Summary, Quiz, Flashcards, Chatbot).

---

## 🔧 How It Works (Technical)

### 1. Model Selection Flow
```
User selects model in UI
    ↓
Frontend saves to user_settings.json
    ↓
Backend extracts selected_model from user settings
    ↓
Pipeline checks if model needs to be reloaded
    ↓
LLM client reloads with new model
    ↓
Generation uses new model
```

### 2. Dynamic Model Loading
- **First request:** Loads default model from `config.yaml`
- **User changes model:** Unloads current model, loads new model
- **Subsequent requests:** Uses cached model (no reload needed)

### 3. Memory Management
- Only one model loaded at a time
- Old model is unloaded before loading new model
- Prevents memory overflow on 4GB GPU

---

## 📊 Model Comparison

| Model | Size | Speed | Quality | Memory | Best For |
|-------|------|-------|---------|--------|----------|
| Mistral 7B | 7B | ⚡⚡ | ⭐⭐⭐⭐⭐ | 4GB | All tasks |
| Phi-3 Mini | 3.8B | ⚡⚡⚡ | ⭐⭐⭐⭐ | 2.5GB | Most tasks |
| Gemma 2B | 2B | ⚡⚡⚡⚡ | ⭐⭐⭐ | 1.5GB | Quick tasks |
| Qwen2 1.5B | 1.5B | ⚡⚡⚡⚡ | ⭐⭐⭐ | 1GB | Simple tasks |
| TinyLlama | 1.1B | ⚡⚡⚡⚡⚡ | ⭐⭐ | 800MB | Testing |

---

## 💡 Recommendations

### For Best Quality
Use **Mistral 7B** for:
- Complex summaries
- Difficult quizzes
- Detailed flashcards

### For Speed
Use **Phi-3 Mini** or **Gemma 2B** for:
- Quick chatbot responses
- Simple flashcards
- Fast iterations

### For Testing
Use **TinyLlama** for:
- Testing the pipeline
- Debugging
- Quick experiments

---

## 🚀 Next Steps

1. **Download additional models** (see download instructions above)
2. **Test different models** for your use cases
3. **Compare quality vs speed** trade-offs
4. **Set your preferred default** in settings

---

**Enjoy the flexibility of multi-model support!** 🎉

