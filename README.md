# Free AI Router

> 多 AI 后端链式 fallback 路由器 / Multi-provider AI fallback router
> 当 Claude / GPT 限速时,自动切到免费后端 / When paid AI hits rate limits, auto-fall back to free tiers

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/fast118/free-ai-router)
[![Gitee](https://img.shields.io/badge/Gitee-C71D23?style=for-the-badge&logo=gitee&logoColor=white)](https://gitee.com/wudijia2026/free-ai-router)

> 🌐 **控制台总览:** [fast118.github.io/console](https://fast118.github.io/console/) - 看所有 fast118 开源项目

[English](#english) | [中文](#中文)

---

## 中文

### 这是什么?

当你用 Claude Code / Cursor / Codex 跑满 token 时,这个工具**自动切到免费的 AI 后端**继续工作,不会断。

支持 4 个免费 AI 后端(GitHub Models / Gemini / Groq / OpenRouter),**链式 fallback**:一个挂了自动切下一个,带 60 秒冷却避免反复重试挂掉的后端。

### 特性

- 🔄 **链式 fallback** —— 主后端失败自动切备用
- 💰 **完全免费** —— 用各家免费额度,不是白嫖就是用得起的低价
- ⚡ **多模型** —— 30+ 模型可选(GPT-4o, Llama 3.3 70B, Gemini, Phi-4, DeepSeek-R1 等)
- 🛡️ **60s 冷却** —— 失败后端冷却 60s,避免雪崩
- 🎯 **简单配置** —— JSON 一处改,优先级/模型/启用状态全可控
- 🖥️ **CLI 友好** —— 一行命令调用,可流式输出
- 🔌 **可扩展** —— 加新后端只要在 config 里加一项

### 为什么用?

- Claude Code / GPT 限速? **不会断,自动切**
- 想白嫖 GPT-4o 写代码? **GitHub Models 免费**
- 想跑 Llama 3.3 70B 又不想自己部署? **Groq 免费**
- 多家免费额度想轮着用? **配置优先级即可**
- 想做个统一的"AI 网关"? **这就是**

### 5 分钟快速开始

**前置:** Python 3.8+

**1. 克隆仓库**
```bash
git clone https://github.com/你的用户名/free-ai-router.git
cd free-ai-router
```

**2. 装依赖**

Windows:
```bash
install.bat
```

Linux/Mac:
```bash
pip install -r requirements.txt
```

**3. 配置 API key(至少一个)**

最简单的办法,跑引导:
```bash
python smart_router.py --setup
```

或手动:
- 复制 `router_config.example.json` 为 `router_config.json`
- 在 [GitHub Models](https://github.com/settings/personal-access-tokens) 申请 token(免费)
- 把 token 存到 `github_models.key.txt`
- 编辑 `router_config.json`,把 `github_models` 的 `enabled` 设为 `true`

**4. 测试**
```bash
python smart_router.py --status    # 看后端状态
python smart_router.py --test      # 测所有可用后端
```

**5. 开始用**
```bash
python smart_router.py "用 Python 写个快排"
python smart_router.py -f main.py "找出这个文件的所有 bug"
python smart_router.py --stream "写首七言绝句"
```

### 支持的免费后端

| 后端 | 免费额度 | 速度 | 推荐模型 |
|------|----------|------|----------|
| **GitHub Models** | 个人账号,无明确上限 | 中 | gpt-4o-mini, llama-3.3-70b, phi-4 |
| **Google Gemini** | 15 RPM / 1500 RPD | 快 | gemini-2.0-flash-exp |
| **Groq** | 30 RPM / 14.4K RPD | **极快** | llama-3.3-70b-versatile |
| **OpenRouter** | 部分模型 `:free` | 中 | deepseek-chat:free |

> 限速是按账号/分钟/天循环刷新,不是按月。挂了等几分钟或第二天就好。

### 命令行用法

```bash
# 基础:问问题(自动选最优后端)
python smart_router.py "你的问题"

# 指定模型
python smart_router.py -m gemini-2.0-flash-exp "问题"

# 读文件再问(总结/翻译/解释)
python smart_router.py -f README.md "翻译成英文"

# 流式输出(打字机效果)
python smart_router.py --stream "写个递归函数解释"

# 看各后端状态
python smart_router.py --status

# 测所有后端
python smart_router.py --test

# 列出所有可用模型
python smart_router.py --list

# 配置新 key
python smart_router.py --setup
```

### 集成到 IDE

**Cursor:**
Settings → Models → Custom OpenAI API → 填 base_url + key

**VSCode + Cline:**
装 Cline 插件 → API Provider 选 "OpenAI Compatible" → 填 base_url + key

**示例(以 Groq 为例):**
- base_url: `https://api.groq.com/openai/v1`
- api_key: `gsk_xxx...`
- model: `llama-3.3-70b-versatile`

### 路线图

- [x] 基础 fallback 路由
- [x] 多后端配置
- [x] 冷却机制
- [ ] Web 界面
- [ ] 自动横评脚本(同题多模型对比)
- [ ] 免费额度监控
- [ ] 配置文件在线生成
- [ ] Docker 镜像
- [ ] Claude Code MCP 集成

### 贡献

欢迎 PR! 可以加:
- 新的 AI 后端 provider
- 新功能(Web 界面、监控、统计)
- 文档改进
- Bug 修复

### 微信交流群

扫码加入微信群,一起交流 AI 工具使用、薅羊毛心得、提 issue / 建议:

> 📷 **占位:微信群二维码**
>
> 把你的群二维码图片保存为 `assets/wechat-qr.png`,即可在此处显示:
>
> ![WeChat Group QR](assets/wechat-qr.png)

### Star History

如果这个项目对你有帮助,欢迎 ⭐ Star 支持一下!

### 许可证

[MIT](LICENSE)

---

## English

### What is this?

When Claude Code / Cursor / Codex hits rate limits, this tool **auto-falls-back to free AI backends** so you never get blocked.

Supports 4 free AI providers (GitHub Models / Gemini / Groq / OpenRouter) with **chain fallback**: if one fails, automatically try the next. 60-second cooldown prevents thrashing on broken backends.

### Features

- 🔄 **Chain fallback** — auto-switch when primary fails
- 💰 **Completely free** — uses free tiers, not freemium traps
- ⚡ **30+ models** — GPT-4o, Llama 3.3 70B, Gemini, Phi-4, DeepSeek-R1, etc.
- 🛡️ **60s cooldown** — failed backends cool down to avoid stampedes
- 🎯 **Simple config** — JSON single source of truth
- 🖥️ **CLI-first** — one-liner, supports streaming
- 🔌 **Extensible** — add a backend by adding a config block

### Quick Start

**Prerequisites:** Python 3.8+

```bash
git clone https://github.com/fast118/free-ai-router.git
cd free-ai-router
pip install -r requirements.txt
cp router_config.example.json router_config.json
# Edit router_config.json, enable at least one provider, add key
python smart_router.py --status
python smart_router.py "Hello world"
```

### Supported Free Backends

| Provider | Free Tier | Speed | Recommended Model |
|----------|-----------|-------|-------------------|
| **GitHub Models** | Per-account, no hard cap | Medium | gpt-4o-mini, llama-3.3-70b |
| **Google Gemini** | 15 RPM / 1500 RPD | Fast | gemini-2.0-flash-exp |
| **Groq** | 30 RPM / 14.4K RPD | **Ultra-fast** | llama-3.3-70b-versatile |
| **OpenRouter** | `:free` models | Medium | deepseek-chat:free |

### CLI Usage

```bash
python smart_router.py "your question"
python smart_router.py -m gemini-2.0-flash-exp "question"
python smart_router.py -f file.py "review this code"
python smart_router.py --stream "stream response"
python smart_router.py --status
python smart_router.py --test
python smart_router.py --list
python smart_router.py --setup
```

### License

[MIT](LICENSE)

### WeChat Group

Scan to join our WeChat group for discussion and updates:

> 📷 **Placeholder: WeChat Group QR Code**
>
> Save your QR image as `assets/wechat-qr.png` to display here:
>
> ![WeChat Group QR](assets/wechat-qr.png)


## v0.2 更新 (2026-06-21 Day 13 A 档)

### ✨ 新增 OpenAI 兼容 HTTP server (server.py)

把 free-ai-router 8 provider 暴露成 OpenAI `/v1/chat/completions` 标准 endpoint. **sillytavern / LM Studio / Open WebUI** 等工具只需把 base URL 改成 `http://localhost:8765/v1` 就能用.

**用法**:
```bash
py server.py                       # 默认 :8765
py server.py --port 9000           # 自定义端口
py server.py --host 0.0.0.0        # 局域网暴露
```

**端点**:
- `GET  /v1/models` - 列出所有 provider 的 models (聚合)
- `GET  /health` - 健康检查
- `POST /v1/chat/completions` - OpenAI 兼容 chat (走 smart_router)
- `POST /v1/completions` - legacy 单 prompt 模式

**示例** (LM Studio 配):
```
Base URL: http://localhost:8765/v1
Model: MiniMax-M3  (或 deepseek-chat, deepseek-reasoner...)
```

**sillytavern 配**:
```
API: OpenAI compatible
Base URL: http://localhost:8765/v1
Model: deepseek-chat
```

**测试** (9 个 unittest 全过):
```bash
py -X utf8 -m unittest test_server.py -v
# 9/9: list_models / handle_chat (basic/empty_messages/default_model/meta/id_format/usage) / handle_completions (legacy/empty_prompt)
```

### v0.2 vs v0.1

| 项 | v0.1 (06-11) | v0.2 (06-21) |
|---|------|------|
| 入口 | CLI (`py smart_router.py`) | CLI + HTTP server |
| OpenAI 兼容 | ❌ | ✅ `/v1/chat/completions` |
| sillytavern 接入 | ❌ | ✅ 直接 base URL |
| 8 provider 调度 | ✅ | ✅ |
| 健康跳过 | ✅ | ✅ |
| 文件 | smart_router.py | smart_router.py + server.py + test_server.py |
