# 掘金文章 #1: 白嫖 GPT-4o 完整指南(2026 最新版)

## 标题(多备选)

- 《还在花钱开 ChatGPT?这 4 个免费 API 直接白嫖 GPT-4o》
- 《Claude Code / Codex 没 token 了怎么办?免费 AI 后端顶上》
- 《2026 年最全免费 AI 接口汇总 + 一键脚本》

## 标签

`AI`、`GitHub`、`开源`、`白嫖`、`ChatGPT`、`Gemini`、`Groq`

## 正文

```markdown
# 2026 年最全免费 AI 接口白嫖指南

> 当 ChatGPT Plus / Claude Pro 月费用完,或者 token 跑光的时候,这 4 个免费 API 可以无缝顶上。

---

## 写在前面

作为一个长期被 Claude Code 和 Codex "token 跑光"困扰的开发者,我前前后后试过十几种"白嫖"方案。最后沉淀下来一个开源工具:[free-ai-router](https://github.com/fast1188/free-ai-router) —— 一个多 AI 后端链式 fallback 路由器。

今天分享的就是工具背后的 4 个免费后端,**全部免费**,**全部能直接调用 GPT-4o / Claude 级模型**。

---

## 一、GitHub Models ——最稳的"白嫖 GPT-4o"方案

**很多人不知道:** 你只要有 GitHub 账号,就能免费用 GPT-4o、Llama 3.3 70B、Phi-4、DeepSeek-R1 等几十个模型。

### 1. 申请 Token

去 https://github.com/settings/personal-access-tokens

- Generate new token → Fine-grained token
- 勾选 **Models: Read** 权限
- 生成后复制 token(以 `github_pat_` 开头)

### 2. 调用示例(curl)

```bash
curl https://models.inference.ai.azure.com/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ghp_你的token" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "你好"}]
  }'
```

### 3. 支持的模型(部分)

- `gpt-4o`、`gpt-4o-mini`、`o1-preview`、`o1-mini`
- `meta-llama-3.3-70b-instruct`、`llama-3.2-90b-vision-instruct`
- `phi-4`、`mistral-large-2407`、`cohere-command-r-plus`
- `deepseek-r1`

**限制:** 限速比较严,适合学习、测试、低频调用。生产环境慎用。

---

## 二、Google Gemini ——免费额度大方的多模态

**Gemini 2.0 Flash 现在完全免费开放**,而且支持图片、视频、音频多模态。

### 1. 申请 API Key

去 https://aistudio.google.com/apikey

- 登录 Google 账号
- 点 "Create API Key"
- 复制 key(以 `AIzaSy` 开头)

### 2. 调用示例

```python
from openai import OpenAI

client = OpenAI(
    api_key="AIzaSy_你的key",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai"
)

response = client.chat.completions.create(
    model="gemini-2.0-flash-exp",
    messages=[{"role": "user", "content": "你好"}]
)
print(response.choices[0].message.content)
```

### 3. 免费额度

- 15 RPM(每分钟请求数)
- 1500 RPD(每天请求数)
- 100 万 TPM(每分钟 token 数)

**对个人开发者来说基本用不完。**

---

## 三、Groq ——速度快到离谱的推理

**Groq 的推理速度是业界最快的**(每秒 500+ token 输出),而且 Llama 3.3 70B 完全免费。

### 1. 申请 Key

去 https://console.groq.com/keys

- 注册账号(用 Google 账号秒过)
- Create API Key
- 复制(以 `gsk_` 开头)

### 2. 调用示例

```python
from openai import OpenAI

client = OpenAI(
    api_key="gsk_你的key",
    base_url="https://api.groq.com/openai/v1"
)

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "写个 Python 快速排序"}]
)
print(response.choices[0].message.content)
```

### 3. 推荐场景

- **代码生成**(超快反馈)
- **实时对话**
- **大批量批处理**

---

## 四、OpenRouter ——免费模型聚合

**OpenRouter 类似 LiteLLM,但有 `:free` 后缀的模型完全免费。**

### 1. 申请 Key

去 https://openrouter.ai/keys

### 2. 调用示例

```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-or-你的key",
    base_url="https://api.openrouter.ai/v1"
)

response = client.chat.completions.create(
    model="meta-llama/llama-3.3-70b-instruct:free",
    messages=[{"role": "user", "content": "hi"}]
)
```

### 3. 免费模型清单(部分)

- `meta-llama/llama-3.3-70b-instruct:free`
- `google/gemini-2.0-flash-exp:free`
- `deepseek/deepseek-chat:free`
- `qwen/qwen-2.5-72b-instruct:free`

---

## 五、一键整合:free-ai-router

上面 4 个 API 各有各的好处,但切换起来很麻烦。所以我做了这个工具:

**[free-ai-router](https://github.com/fast1188/free-ai-router)**

**核心功能:链式 fallback —— 一个挂了自动切下一个,完全无需手动。**

### 5 分钟上手

```bash
git clone https://github.com/fast1188/free-ai-router
cd free-ai-router
pip install -r requirements.txt

# 跑配置引导,粘贴你的 key
python smart_router.py --setup

# 测一下所有后端
python smart_router.py --test

# 开始用
python smart_router.py "用 Python 写个快排"
python smart_router.py -f main.py "找出所有 bug"
python smart_router.py --stream "写首诗"
```

### 支持的功能

- ✓ 4 个免费后端自动 fallback
- ✓ 60 秒冷却机制(失败的不会一直试)
- ✓ 流式输出
- ✓ 文件批量处理
- ✓ 集成到 Cursor / Cline / Cherry Studio

---

## 写在最后

**这些免费额度个人用完全够了,生产环境慎用。**

如果工具对你有帮助,**点个 Star** 支持一下:

> ⭐ https://github.com/fast1188/free-ai-router

**进微信群交流**(项目 README 有二维码,或者扫码下图):

[WeChat QR Code]

更多 AI 工具、薅羊毛心得、提 issue 建议,群里聊。
```

## 配图建议

1. **封面图**:4 个免费 API logo 拼图(GitHub / Gemini / Groq / OpenRouter)
2. **架构图**:free-ai-router 工作原理(主→备→备→备)
3. **效果截图**:命令行跑通的截图
4. **群二维码**:文章末尾

## 发布时间建议

- 工作日晚上 8-10 点(程序员活跃时段)
- 周末下午 2-4 点