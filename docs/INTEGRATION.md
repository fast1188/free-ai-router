# IDE Integration

Use free AI backends in your favorite code editor.

---

## Cursor

1. Open Cursor Settings (Ctrl+,)
2. Go to "Models" tab
3. Click "Add Custom OpenAI API"
4. Fill in:
   - **API Key:** Your provider's key (e.g., Groq key)
   - **Base URL:** Provider's base URL
   - **Model:** Choose from the provider's model list

### Example: Groq
- Base URL: `https://api.groq.com/openai/v1`
- API Key: `gsk_xxx...`
- Model: `llama-3.3-70b-versatile`

---

## VSCode + Cline

1. Install "Cline" extension from VSCode marketplace
2. Click Cline icon in sidebar
3. Click settings gear icon
4. API Provider: Select "OpenAI Compatible"
5. Fill in:
   - **Base URL:** Provider's base URL
   - **API Key:** Your key
   - **Model ID:** Model name

### Example: GitHub Models
- Base URL: `https://models.inference.ai.azure.com`
- API Key: `github_pat_xxx...`
- Model ID: `gpt-4o-mini`

---

## VSCode + Continue

1. Install "Continue" extension
2. Edit `~/.continue/config.json`:
```json
{
  "models": [
    {
      "title": "GitHub Models",
      "provider": "openai",
      "model": "gpt-4o-mini",
      "apiBase": "https://models.inference.ai.azure.com",
      "apiKey": "github_pat_xxx..."
    }
  ]
}
```

---

## Aider (CLI coding assistant)

```bash
pip install aider-chat

# GitHub Models
aider --model openai/gpt-4o-mini \
      --openai-api-base https://models.inference.ai.azure.com \
      --openai-api-key github_pat_xxx...

# Groq
aider --model openai/llama-3.3-70b-versatile \
      --openai-api-base https://api.groq.com/openai/v1 \
      --openai-api-key gsk_xxx...

# Gemini
aider --model openai/gemini-2.0-flash-exp \
      --openai-api-base https://generativelanguage.googleapis.com/v1beta/openai \
      --openai-api-key AIzaSy...
```

---

## Cherry Studio (Desktop)

1. Download from https://cherry-ai.com/
2. Settings → Model Services → Add
3. Provider: "Custom OpenAI Compatible"
4. Fill in Base URL, API Key, Models
5. Use the top dropdown to switch between providers

---

## ChatBox (Desktop)

1. Download from https://github.com/chatboxai/chatbox/releases
2. Settings → Custom Provider
3. Fill in Base URL, API Key
4. Choose model
5. Start chatting
