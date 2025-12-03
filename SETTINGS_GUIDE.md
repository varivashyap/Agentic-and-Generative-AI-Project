# User Settings Guide

## Overview

The Study Assistant now supports **user-configurable hyperparameters** that allow you to customize the behavior of all AI features (Summary, Flashcards, Quiz, Chatbot) without modifying code or configuration files.

## Features

✅ **User-Friendly UI** - Settings modal with sliders and number inputs  
✅ **Per-User Settings** - Each user can have their own preferences  
✅ **Default Fallback** - Uses `config.yaml` defaults if no custom settings  
✅ **Persistent Storage** - Settings saved to disk and loaded on startup  
✅ **Real-Time Updates** - Changes apply immediately to all features  
✅ **Reset to Defaults** - One-click reset to original values  

---

## How to Use

### Frontend (Web UI)

1. **Open Settings**
   - Click the **⚙️ Settings** button in the top-right corner (next to Calendar)
   - Settings modal will open with all configurable parameters

2. **Adjust Parameters**
   - Use **sliders** for temperature values (continuous)
   - Use **number inputs** for discrete values (tokens, counts)
   - Changes are shown in real-time

3. **Save Settings**
   - Click **"Save Settings"** button at the bottom
   - Settings are saved to backend and applied immediately
   - Success message confirms save

4. **Reset to Defaults**
   - Click **"Reset to Defaults"** button
   - All settings revert to `config.yaml` values
   - Confirmation message appears

### Backend (API)

#### Get Settings Schema
```bash
GET /settings/schema
```
Returns the schema describing all available settings with min/max/step values.

#### Get User Settings
```bash
GET /settings?user_id=default
```
Returns current settings for a user (or defaults if no custom settings).

#### Update User Settings
```bash
POST /settings
Content-Type: application/json

{
  "user_id": "default",
  "settings": {
    "summary_temperature": 0.3,
    "quiz_num_questions": 15
  }
}
```
Updates specific settings (only provided fields are changed).

#### Reset User Settings
```bash
POST /settings/reset
Content-Type: application/json

{
  "user_id": "default"
}
```
Resets all settings to defaults from `config.yaml`.

---

## Available Settings

### 📝 Summary Settings

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `summary_temperature` | float | 0.0 - 0.5 | 0.1 | Creativity (lower = more factual) |
| `summary_max_tokens` | int | 200 - 1000 | 600 | Maximum summary length |

### 🗂️ Flashcard Settings

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `flashcard_temperature` | float | 0.0 - 0.5 | 0.25 | Creativity for flashcard generation |
| `flashcard_max_cards` | int | 5 - 50 | 20 | Maximum number of flashcards |

### 📋 Quiz Settings

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `quiz_temperature` | float | 0.0 - 0.5 | 0.2 | Creativity for quiz generation |
| `quiz_num_questions` | int | 5 - 20 | 10 | Number of questions to generate |

### 💬 Chatbot Settings

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `chatbot_temperature` | float | 0.0 - 1.0 | 0.7 | Conversational creativity (higher = more varied) |
| `chatbot_max_tokens` | int | 100 - 500 | 300 | Maximum response length |

### 🔍 Retrieval Settings (Advanced)

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `retrieval_top_k` | int | 5 - 50 | 20 | Number of chunks to retrieve initially |
| `reranker_top_m` | int | 2 - 10 | 6 | Final chunks after reranking |

---

## Technical Implementation

### Architecture

```
Frontend (app.js)
    ↓ GET /settings
Backend (server.py)
    ↓
SettingsManager (settings_manager.py)
    ↓ Load defaults from config.yaml
    ↓ Load user overrides from disk
    ↓ Return merged settings
    ↓
Handlers (handlers.py)
    ↓ Extract user_settings from parameters
    ↓ Pass to pipeline methods
    ↓
Pipeline (pipeline.py)
    ↓ Pass to generators
    ↓
Generators (summary_generator.py, etc.)
    ↓ Use provided values or config defaults
    ↓ Generate content with custom parameters
```

### Key Design Decisions

1. **Dynamic Override (NOT Temporary YAML)**
   - Settings passed as parameters in API requests
   - No file creation/deletion overhead
   - Thread-safe and efficient

2. **Backward Compatibility**
   - If `user_settings` not in parameters → use `config.yaml` defaults
   - Existing code continues to work without modifications
   - No breaking changes to API contracts

3. **Persistent Storage**
   - User settings saved to `data/cache/user_settings.json`
   - Loaded on server startup
   - Survives server restarts

4. **Granular Control**
   - Can update individual settings without affecting others
   - Partial updates supported (only changed fields sent)
   - Full reset available when needed

---

## Examples

### Example 1: More Creative Summaries
```javascript
// In frontend
saveUserSettings({
  summary_temperature: 0.4,  // Increase from 0.1
  summary_max_tokens: 800    // Increase from 600
});
```

### Example 2: Shorter Quiz with More Questions
```javascript
saveUserSettings({
  quiz_num_questions: 20,    // Increase from 10
  quiz_max_tokens: 1200      // Decrease per-question tokens
});
```

### Example 3: More Conversational Chatbot
```javascript
saveUserSettings({
  chatbot_temperature: 0.9,  // Increase from 0.7
  chatbot_max_tokens: 400    // Increase from 300
});
```

---

## Troubleshooting

### Settings Not Saving
- Check browser console for errors
- Verify MCP server is running (`http://localhost:5000/health`)
- Check server logs for error messages

### Settings Not Applied
- Refresh the page to reload settings
- Verify settings were saved (check success message)
- Try resetting to defaults and re-applying

### Default Values Wrong
- Check `config/config.yaml` for correct defaults
- Restart MCP server to reload config
- Reset user settings to pick up new defaults

---

## Future Enhancements

- [ ] Per-feature settings profiles (e.g., "Quick Summary", "Detailed Summary")
- [ ] Import/export settings as JSON
- [ ] Settings history and undo
- [ ] A/B testing different parameter combinations
- [ ] Recommended settings based on document type

---

**Note:** All settings are stored locally and not shared between users. Each user ID has independent settings.

