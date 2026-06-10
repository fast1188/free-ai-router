# FAQ

## General

### Q: 这是免费的吗?

**A:** 完全免费。利用各 AI 厂商的免费层(free tier)调用,不需要付费。

### Q: 需要付费 API key 吗?

**A:** 不需要。所有默认配置的后端都提供免费层。

### Q: 跟 OpenRouter 有什么区别?

**A:** OpenRouter 是一个统一的付费 API 聚合(有少量免费模型)。本项目专注于**完全免费**的聚合,默认 4 个后端都是真免费,带自动 fallback 链。

### Q: 跟 LiteLLM 有什么区别?

**A:** LiteLLM 更通用、更复杂(支持 100+ 模型,但很多是付费的)。本项目**轻量、专注免费、CLI 优先**。

---

## Setup

### Q: token 怎么获取?

**A:** 每个提供商都有不同的获取方式,详见 [PROVIDERS.md](PROVIDERS.md)。

### Q: 11.txt / .key.txt 这些文件安全吗?

**A:** 文件本身在本地,**不会被上传**(本项目纯本地运行)。但**不要提交到 Git**!已经默认加入了 `.gitignore`。**绝对不要把这些文件发到任何聊天/工单/截图里。**

### Q: token 过期了怎么办?

**A:** token 一般 30-90 天过期。到期前 GitHub/Google/Groq 会发邮件提醒,去对应平台重新生成,替换文件内容即可。

---

## Usage

### Q: 怎么让脚本永远不用手动切换?

**A:** 默认就是自动的!路由器会按优先级顺序尝试后端,失败自动切下一个。你只管发问题,不用选。

### Q: 怎么指定具体模型?

**A:**
```bash
python smart_router.py -m 模型名 "问题"
```
模型名必须在 `router_config.json` 里登记过,否则会报"所有后端都失败"。

### Q: 流式输出怎么用?

**A:**
```bash
python smart_router.py --stream "问题"
```

### Q: 处理文件怎么用?

**A:**
```bash
python smart_router.py -f 文件路径 "对文件的处理要求"
```
例如:
```bash
python smart_router.py -f main.py "找出所有 bug"
python smart_router.py -f article.md "翻译成英文"
```

---

## Troubleshooting

### Q: 报错 "ascii codec can't encode characters"

**A:** CMD/PowerShell 编码问题。解决方法:
```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001
```

或者:
- 用 Windows Terminal(默认 UTF-8)
- 用 VSCode 的终端

### Q: 报错 "Request timed out"

**A:**
- GitHub Models 偶尔慢,稍后重试
- 换更小的模型(`-m gpt-4o-mini` 或 `phi-4`)
- 检查网络

### Q: 报错 "Rate limit exceeded"

**A:**
- 等几分钟重试
- 路由器会自动切下一个后端(如果配置了多个)

### Q: 报错 "All backends failed"

**A:** 所有后端都挂了。检查:
1. `python smart_router.py --status` 看每个后端状态
2. 至少一个后端 `enabled: true` 且 key 有效
3. 网络通畅

### Q: 怎么确认 token 是否有效?

**A:**
```bash
python smart_router.py --test
```
能看到每个后端 ✓/✗ 状态。

### Q: 怎么完全重置配置?

**A:**
```bash
cp router_config.example.json router_config.json
```
重新填 key。

---

## Advanced

### Q: 怎么调冷却时间?

**A:** 编辑 `router_config.json`:
```json
{
  "cooldown_seconds": 60
}
```

### Q: 怎么加新模型?

**A:** 编辑 `router_config.json` 对应 provider 的 `models` 数组,加模型 ID。

### Q: 怎么用代理?

**A:** 设环境变量:
```bash
set HTTPS_PROXY=http://127.0.0.1:7890
```

### Q: 怎么集成到 Claude Code / Cursor / Cline?

**A:** 用任一后端的 base_url + key,填到 IDE 设置里。详见 README "集成到 IDE" 章节。
