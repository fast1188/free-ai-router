# Providers Guide

Detailed guide for configuring each supported AI provider.

## GitHub Models

**Free tier:** Personal access token, no hard cap on usage
**Speed:** Medium
**Best for:** General purpose, multi-model testing

### Setup

1. Visit https://github.com/settings/personal-access-tokens
2. Click "Generate new token" → "Fine-grained token"
3. Set Token name (e.g., "free-ai-router")
4. Set Resource owner to yourself
5. Set Expiration (30/60/90 days)
6. Repository access: "Public Repositories (read-only)"
7. Under Permissions → Account permissions → Add "Models: Read"
8. Click "Generate token"
9. Copy the token (starts with `github_pat_` or `ghp_`)

### Save Token

Save the token to `github_models.key.txt`:
```bash
echo "github_pat_xxx..." > github_models.key.txt
```

### Available Models

- `gpt-4o` — OpenAI flagship
- `gpt-4o-mini` — OpenAI fast variant
- `o1-preview`, `o1-mini` — OpenAI reasoning models
- `meta-llama-3.3-70b-instruct` — Meta Llama 3.3
- `llama-3.2-90b-vision-instruct` — Llama 3.2 multimodal
- `phi-4` — Microsoft Phi-4
- `mistral-large-2407` — Mistral Large
- `cohere-command-r-plus` — Cohere
- `deepseek-r1` — DeepSeek reasoning
- `ai21-jamba-1.5-large` — AI21 Jamba

### Troubleshooting

**Error: "Token does not have Models: Read permission"**
- Generate a new fine-grained token with Models: Read permission
- Or use a classic token (no scope needed)

**Error: "Rate limit exceeded"**
- Wait a few minutes and retry
- Consider switching to another provider in the meantime

---

## Google Gemini

**Free tier:** 15 RPM / 1500 RPD / 1M TPM
**Speed:** Fast
**Best for:** Long context, multimodal

### Setup

1. Visit https://aistudio.google.com/apikey
2. Sign in with Google account
3. Click "Create API key"
4. Copy the key (starts with `AIzaSy`)

### Save Key

```bash
echo "AIzaSy..." > gemini.key.txt
```

### Available Models

- `gemini-2.0-flash-exp` — Latest experimental flash
- `gemini-1.5-flash` — Stable flash
- `gemini-1.5-pro` — Pro tier (more capable)

### Enable in Config

Edit `router_config.json`:
```json
{
  "name": "gemini",
  "enabled": true,
  "api_key_file": "gemini.key.txt",
  ...
}
```

---

## Groq

**Free tier:** 30 RPM / 14,400 RPD
**Speed:** **Ultra-fast** (fastest inference available)
**Best for:** Real-time applications, code generation

### Setup

1. Visit https://console.groq.com/keys
2. Sign in / create account
3. Click "Create API Key"
4. Copy the key (starts with `gsk_`)

### Save Key

```bash
echo "gsk_..." > groq.key.txt
```

### Available Models

- `llama-3.3-70b-versatile` — Llama 3.3 70B (recommended)
- `llama-3.1-8b-instant` — Llama 3.1 8B (very fast)
- `mixtral-8x7b-32768` — Mixtral 8x7B
- `deepseek-r1-distill-llama-70b` — DeepSeek R1 distilled

---

## OpenRouter

**Free tier:** Various `:free` models
**Speed:** Medium
**Best for:** Accessing many models through one API

### Setup

1. Visit https://openrouter.ai/keys
2. Sign in
3. Click "Create Key"
4. Copy the key (starts with `sk-or-`)

### Save Key

```bash
echo "sk-or-..." > openrouter.key.txt
```

### Available Free Models

- `meta-llama/llama-3.3-70b-instruct:free`
- `google/gemini-2.0-flash-exp:free`
- `deepseek/deepseek-chat:free`
- `qwen/qwen-2.5-72b-instruct:free`
- `mistralai/mistral-7b-instruct:free`

---

## Adding a Custom Provider

To add a new provider not in the default config:

1. Open `router_config.json`
2. Add a new entry under `providers`:
```json
{
  "name": "my_provider",
  "label": "My Custom Provider",
  "base_url": "https://api.example.com/v1",
  "api_key_file": "my_provider.key.txt",
  "models": ["model-1", "model-2"],
  "priority": 5,
  "enabled": true
}
```

3. Save the API key to `my_provider.key.txt`
4. Run `python smart_router.py --status` to verify
