# Study Assistant Pipeline - Complete Architecture Report

## Table of Contents
1. [System Overview](#system-overview)
2. [Request Flow](#request-flow)
3. [Settings Management](#settings-management)
4. [Component Details](#component-details)
5. [Model Management](#model-management)
6. [Data Flow Diagrams](#data-flow-diagrams)

---

## 1. System Overview

### Architecture Pattern
The Study Assistant uses a **3-tier architecture**:

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Tier 1)                     │
│  - HTML/CSS/JavaScript                                   │
│  - User Interface & Interaction                          │
│  - Settings Management UI                                │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP REST API
┌────────────────────▼────────────────────────────────────┐
│                 MCP Server (Tier 2)                      │
│  - Flask REST API (Port 5000)                            │
│  - Request Routing & Validation                          │
│  - Session Management & Caching                          │
│  - Settings Persistence                                  │
│  - Model Selection & Switching                           │
└────────────────────┬────────────────────────────────────┘
                     │ Python API
┌────────────────────▼────────────────────────────────────┐
│              Pipeline Core (Tier 3)                      │
│  - Document Processing (PDF/Audio/Video)                 │
│  - RAG (Retrieval Augmented Generation)                  │
│  - LLM Generation (Summary/Quiz/Flashcards/Chat)         │
│  - Vector Store & Embeddings                             │
└──────────────────────────────────────────────────────────┘
```

### Key Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| **Frontend** | User interface | HTML5, CSS3, Vanilla JS |
| **MCP Server** | API gateway & orchestration | Flask, Python 3.10 |
| **Pipeline** | Core processing logic | Python, llama-cpp-python |
| **Vector Store** | Semantic search | FAISS |
| **Embeddings** | Text vectorization | sentence-transformers |
| **LLM** | Text generation | GGUF quantized models |
| **Reranker** | Result refinement | cross-encoder |

---

## 2. Request Flow

### 2.1 Document Upload & Processing

```
User uploads PDF/Audio/Video
         │
         ▼
┌────────────────────────────────────────────────────────┐
│ 1. Frontend: POST /upload                              │
│    - FormData with file                                │
│    - user_id (default)                                 │
└────────────┬───────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────┐
│ 2. MCP Server: Upload Handler                          │
│    - Save file to data/uploads/                        │
│    - Generate timestamp prefix                         │
│    - Return: {success, filename, file_id}              │
└────────────┬───────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────┐
│ 3. Frontend: POST /process                             │
│    - Parameters: {                                     │
│        file_id,                                        │
│        request_type (summary/quiz/flashcards/chatbot), │
│        user_settings (optional)                        │
│      }                                                 │
└────────────┬───────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────┐
│ 4. MCP Server: Process Handler                         │
│    a) Check session cache (SHA256 hash)                │
│    b) If cached: Load existing session                 │
│    c) If new: Process document                         │
└────────────┬───────────────────────────────────────────┘
             │
             ▼ (if new document)
┌────────────────────────────────────────────────────────┐
│ 5. Pipeline: Document Ingestion                        │
│    a) Detect file type (PDF/Audio/Video)               │
│    b) Extract content:                                 │
│       - PDF: PyMuPDF → text + metadata                 │
│       - Audio: Whisper → transcription                 │
│       - Video: Extract audio → Whisper                 │
│    c) Chunk text (300 tokens, 60 overlap)              │
│    d) Generate embeddings (all-MiniLM-L6-v2)           │
│    e) Build vector store (FAISS)                       │
│    f) Build BM25 index                                 │
│    g) Save to cache                                    │
└────────────┬───────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────┐
│ 6. Request Handler: Route to Component                 │
│    - SummaryRequestHandler                             │
│    - QuizRequestHandler                                │
│    - FlashcardsRequestHandler                          │
│    - ChatbotRequestHandler                             │
└────────────┬───────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────┐
│ 7. Component: Generate Content                         │
│    (See Component Details section)                     │
└────────────┬───────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────┐
│ 8. Return Response to Frontend                         │
│    - JSON with generated content                       │
│    - Metadata (processing time, model used, etc.)      │
└────────────────────────────────────────────────────────┘
```

### 2.2 Session Management & Caching

**Purpose**: Avoid reprocessing the same document multiple times.

**Implementation**:
```python
# 1. Generate file hash
file_hash = hashlib.sha256(file_content).hexdigest()

# 2. Check cache
cache_dir = f"data/cache/sessions/{file_hash}"
if os.path.exists(cache_dir):
    # Load cached session
    pipeline.load_index(cache_dir)
else:
    # Process new document
    pipeline.ingest_pdf(file_path)
    pipeline.save_index(cache_dir)
```

**Cache Structure**:
```
data/cache/sessions/
└── {file_hash}/
    ├── vector_store.faiss    # FAISS index
    ├── metadata.json         # Document metadata
    └── chunks.json           # Text chunks
```

---

## 3. Settings Management

### 3.1 Settings Architecture

**Two-Level Configuration**:
1. **Global Defaults** (`config/config.yaml`) - System-wide defaults
2. **User Settings** (`data/settings/user_settings.json`) - Per-user overrides

**Priority**: User Settings > Global Defaults

### 3.2 Settings Flow

```
User opens Settings UI
         │
         ▼
┌────────────────────────────────────────────────────────┐
│ 1. Frontend: GET /settings?user_id=default             │
└────────────┬───────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────┐
│ 2. SettingsManager: Load Settings                      │
│    a) Load user_settings.json                          │
│    b) If user exists: return saved settings            │
│    c) If new user: return defaults from config.yaml    │
└────────────┬───────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────┐
│ 3. Frontend: Populate UI                               │
│    - Model dropdown                                    │
│    - Temperature sliders                               │
│    - Max tokens inputs                                 │
│    - System prompt text areas                          │
└────────────────────────────────────────────────────────┘
```

**User Modifies Settings**:
```
User changes settings → Click Save
         │
         ▼
┌────────────────────────────────────────────────────────┐
│ 1. Frontend: POST /settings                            │
│    Body: {                                             │
│      user_id: "default",                               │
│      selected_model: "qwen2-1.5b-instruct.Q4_K_M",     │
│      summary_temperature: 0.1,                         │
│      summary_max_tokens: 600,                          │
│      summary_system_prompt: "Custom prompt...",        │
│      ... (all settings)                                │
│    }                                                   │
└────────────┬───────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────┐
│ 2. SettingsManager: Save Settings                      │
│    a) Validate settings                                │
│    b) Update user_settings.json                        │
│    c) Return: {success: true}                          │
└────────────────────────────────────────────────────────┘
```

### 3.3 Settings Application

**When generating content**, settings are applied in this order:

```python
# 1. Extract user settings from request
user_settings = extract_user_settings(request_parameters)

# 2. Check if model needs to be switched
if user_settings.selected_model != pipeline.current_model:
    pipeline.reload_model(user_settings.selected_model)

# 3. Apply settings to generation
temperature = user_settings.summary_temperature  # or None (use default)
max_tokens = user_settings.summary_max_tokens    # or None (use default)
system_prompt = user_settings.summary_system_prompt  # or None (use default)

# 4. Generate with overrides
summary = pipeline.generate_summaries(
    temperature=temperature,      # Overrides config.yaml
    max_tokens=max_tokens,        # Overrides config.yaml
    system_prompt=system_prompt   # Overrides hardcoded prompt
)
```

**Fallback Pattern**:
```python
# In generator classes
def generate(self, temperature=None, max_tokens=None, system_prompt=None):
    # Use user setting if provided, else use config default
    temp = temperature if temperature is not None else self.config.temperature
    tokens = max_tokens if max_tokens is not None else self.config.max_tokens
    prompt = system_prompt if system_prompt is not None else self._get_system_prompt()
```

---

## 4. Component Details

### 4.1 Summary Generation

**Request Parameters**:
- `scale`: "paragraph" | "bullet" | "detailed"
- `query`: Optional focus query
- `user_settings`: Temperature, max_tokens, system_prompt

**Processing Steps**:

1. **Retrieve Context** (RAG Pipeline)
   - Generate query embedding
   - Vector search (FAISS) → top 20
   - BM25 search → top 20
   - Hybrid fusion (RRF)
   - Rerank → top 6
   - Truncate to 500 chars/chunk

2. **Format Prompt**
   ```
   System: [Custom or default system prompt]

   User: Based on the following content, generate a [scale] summary.

   Context:
   [Chunk 1]
   [Chunk 2]
   ...

   Generate summary.
   ```

3. **Generate** with LLM (temperature=0.1, max_tokens=600)

4. **Validate** (optional)
   - Check hallucination risk
   - Check source containment

5. **Return** summary + metadata

### 4.2 Quiz Generation

**Request Parameters**:
- `question_type`: "mcq" | "true_false" | "short_answer"
- `num_questions`: 1-50
- `difficulty`: "easy" | "medium" | "hard" (optional)
- `user_settings`: Temperature, max_tokens, system_prompt

**Processing Steps**:

1. **Retrieve Context** (same RAG as summary)

2. **Format Structured Prompt**
   ```
   System: [Quiz system prompt]

   User: Generate exactly {num_questions} {question_type} questions.

   Context:
   [Chunks...]

   Return ONLY a JSON array:
   [
     {
       "question": "...",
       "options": ["A", "B", "C", "D"],
       "correct_answer": "B",
       "explanation": "...",
       "difficulty": "medium"
     }
   ]
   ```

3. **Generate** with LLM (temperature=0.2, max_tokens=1500)

4. **Parse JSON Response**
   - Extract JSON array
   - Validate structure
   - Assign difficulty if missing

5. **Return** questions array

### 4.3 Flashcard Generation

**Request Parameters**:
- `card_type`: "definition" | "concept" | "qa"
- `max_cards`: 1-50
- `user_settings`: Temperature, max_tokens, system_prompt

**Processing Steps**:

1. **Retrieve Context** (RAG)

2. **Format Prompt**
   ```
   System: [Flashcard system prompt]

   User: Generate exactly {max_cards} flashcards.

   Context:
   [Chunks...]

   Return JSON array:
   [
     {
       "front": "Question or term",
       "back": "Answer or definition"
     }
   ]
   ```

3. **Generate** with LLM (temperature=0.25, max_tokens=1500)

4. **Parse & Validate**

5. **Return** flashcards array

### 4.4 Chatbot (RAG Q&A)

**Request Parameters**:
- `message`: User question
- `session_id`: Conversation ID
- `max_history`: Number of previous turns to include
- `user_settings`: Temperature, max_tokens, system_prompt

**Processing Steps**:

1. **Load Conversation History**
   - Retrieve last N turns from session

2. **Retrieve Context** (RAG with user question)

3. **Format Conversational Prompt**
   ```
   System: [Chatbot system prompt]

   Context:
   [Retrieved chunks...]

   Conversation History:
   User: [Previous question]
   Assistant: [Previous answer]
   ...

   User: [Current question]
   Assistant:
   ```

4. **Generate** with LLM (temperature=0.7, max_tokens=300)

5. **Save to History**

6. **Return** response

---

## 5. Model Management

### 5.1 Available Models

| Model | Size | VRAM | Speed | Quality | Prompt Format |
|-------|------|------|-------|---------|---------------|
| Mistral 7B | 4.1GB | ~4GB | Medium | Excellent | `<s>[INST] ... [/INST]` |
| Qwen2 1.5B | 941MB | ~1GB | Very Fast | Good | `<|im_start|>...<|im_end|>` |
| TinyLlama 1.1B | 638MB | ~800MB | Ultra Fast | Fair | `<|user|>...<|assistant|>` |

### 5.2 Model Switching Flow

```
User selects different model in Settings
         │
         ▼
┌────────────────────────────────────────────────────────┐
│ 1. Frontend: Save settings with new selected_model     │
└────────────┬───────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────┐
│ 2. Next generation request                             │
│    - Handler extracts user_settings                    │
│    - Compares selected_model vs current_model          │
└────────────┬───────────────────────────────────────────┘
             │
             ▼ (if different)
┌────────────────────────────────────────────────────────┐
│ 3. Pipeline.reload_model()                             │
│    a) Unload current model (free VRAM)                 │
│    b) Load new model from models/ directory            │
│    c) Update current_model tracker                     │
└────────────┬───────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────┐
│ 4. LLMClient.reload()                                  │
│    a) Delete old Llama instance                        │
│    b) Create new Llama instance                        │
│    c) Detect model architecture                        │
│    d) Set prompt format & stop tokens                  │
└────────────┬───────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────┐
│ 5. Continue with generation using new model            │
└────────────────────────────────────────────────────────┘
```

### 5.3 Prompt Formatting by Model

**Mistral 7B**:
```
<s>[INST] {system_prompt}

{user_prompt} [/INST]
```

**Qwen2 1.5B**:
```
<|im_start|>system
{system_prompt}<|im_end|>
<|im_start|>user
{user_prompt}<|im_end|>
<|im_start|>assistant
```

**TinyLlama 1.1B**:
```
<|system|>
{system_prompt}</s>
<|user|>
{user_prompt}</s>
<|assistant|>
```

---

## 6. Data Flow Diagrams

### 6.1 Complete Request Lifecycle

```
┌─────────┐
│  User   │
└────┬────┘
     │ 1. Upload PDF
     ▼
┌─────────────────┐
│   Frontend      │
│  (Port 8080)    │
└────┬────────────┘
     │ 2. POST /upload
     ▼
┌─────────────────┐
│  MCP Server     │
│  (Port 5000)    │
└────┬────────────┘
     │ 3. Save file
     │ 4. Generate hash
     ▼
┌─────────────────┐
│ Session Manager │
└────┬────────────┘
     │ 5. Check cache
     ▼
┌─────────────────┐
│   Pipeline      │
└────┬────────────┘
     │ 6. Process PDF
     ▼
┌─────────────────┐
│ PDF Processor   │
└────┬────────────┘
     │ 7. Extract text
     ▼
┌─────────────────┐
│    Chunker      │
└────┬────────────┘
     │ 8. Create chunks
     ▼
┌─────────────────┐
│   Embeddings    │
└────┬────────────┘
     │ 9. Generate vectors
     ▼
┌─────────────────┐
│  Vector Store   │
│    (FAISS)      │
└────┬────────────┘
     │ 10. Build index
     ▼
┌─────────────────┐
│  BM25 Index     │
└────┬────────────┘
     │ 11. Save to cache
     ▼
┌─────────────────┐
│ Session Manager │
└────┬────────────┘
     │ 12. Return success
     ▼
┌─────────────────┐
│   Frontend      │
└────┬────────────┘
     │ 13. Show "Ready"
     ▼
┌─────────┐
│  User   │ Clicks "Generate Summary"
└────┬────┘
     │ 14. POST /process
     ▼
┌─────────────────┐
│  MCP Server     │
└────┬────────────┘
     │ 15. Route to handler
     ▼
┌─────────────────┐
│ Summary Handler │
└────┬────────────┘
     │ 16. Extract settings
     │ 17. Check model switch
     ▼
┌─────────────────┐
│   Pipeline      │
└────┬────────────┘
     │ 18. RAG retrieval
     ▼
┌─────────────────┐
│ Hybrid Retriever│
└────┬────────────┘
     │ 19. Vector + BM25
     ▼
┌─────────────────┐
│    Reranker     │
└────┬────────────┘
     │ 20. Top 6 chunks
     ▼
┌─────────────────┐
│Summary Generator│
└────┬────────────┘
     │ 21. Format prompt
     ▼
┌─────────────────┐
│   LLM Client    │
└────┬────────────┘
     │ 22. Generate text
     ▼
┌─────────────────┐
│  llama.cpp      │
└────┬────────────┘
     │ 23. Return summary
     ▼
┌─────────────────┐
│   Validator     │
└────┬────────────┘
     │ 24. Check quality
     ▼
┌─────────────────┐
│  MCP Server     │
└────┬────────────┘
     │ 25. Return JSON
     ▼
┌─────────────────┐
│   Frontend      │
└────┬────────────┘
     │ 26. Display result
     ▼
┌─────────┐
│  User   │
└─────────┘
```

---

## 7. Key Design Patterns

### 7.1 Strategy Pattern (Model Selection)
Different models implement the same interface but with different prompt formats.

### 7.2 Factory Pattern (Request Handlers)
Request type determines which handler factory creates.

### 7.3 Singleton Pattern (Pipeline)
One pipeline instance per session, reused across requests.

### 7.4 Observer Pattern (Settings)
Settings changes trigger model reloads when needed.

### 7.5 Cache-Aside Pattern (Sessions)
Check cache first, compute and store if miss.

---

## 8. Performance Optimizations

1. **Session Caching** - Avoid reprocessing same document
2. **Lazy Loading** - Load models only when needed
3. **Chunk Truncation** - Limit context to 500 chars/chunk
4. **Hybrid Retrieval** - Combine vector + keyword search
5. **Reranking** - Refine top results for quality
6. **GPU Offloading** - Use GPU when available (4GB limit)
7. **Quantization** - Q4_K_M models for memory efficiency

---

## 9. Error Handling

### 9.1 Document Processing Errors
- Invalid file format → Return error message
- Corrupted PDF → Fallback to text extraction
- Empty document → Return warning

### 9.2 Model Loading Errors
- Model file not found → Use default Mistral
- Insufficient VRAM → Fallback to CPU
- Unsupported architecture → Show error

### 9.3 Generation Errors
- JSON parsing failure → Return empty array + warning
- Timeout → Return partial results
- Hallucination detected → Add warning flag

---

## 10. Security Considerations

1. **File Upload** - Validate file types, size limits
2. **User Isolation** - Separate settings per user_id
3. **Input Sanitization** - Clean user prompts
4. **Rate Limiting** - Prevent abuse (not implemented)
5. **CORS** - Configured for localhost only

---

## 11. Future Enhancements

1. **Multi-user Support** - Real authentication
2. **GPU Acceleration** - Better VRAM management
3. **Streaming Responses** - Real-time generation
4. **Advanced RAG** - Query expansion, multi-hop
5. **Fine-tuning** - Custom model adapters
6. **Analytics** - Usage tracking, quality metrics

---

**Document Version**: 1.0
**Last Updated**: 2025-12-03
**Author**: AI Study Assistant Team

