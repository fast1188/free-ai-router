# 掘金文章 #2: Claude Code 没 token 了?这 3 个免费后端顶上

## 标题备选

- 《Claude Code token 跑光别慌,3 个免费模型自动顶上》
- 《Claude Code + free-ai-router:永不中断的 AI 编程体验》
- 《用 5 分钟配置一个永远不会"卡 token"的 AI 编程环境》

## 标签

`Claude Code`、`Codex`、`AI编程`、`开源工具`、`GitHub`、`白嫖`

## 目标读者

- 用 Claude Code / Cursor / Codex 的开发者
- 经常遇到 "You've reached your limit" 提示的人
- 想省 token 钱的人

## 正文大纲

1. **痛点引入**(300 字)
   - Claude Code 用着用着就限速
   - GPT-4o API 又贵
   - 等待时间浪费生命

2. **方案介绍**(500 字)
   - free-ai-router 是什么
   - 链式 fallback 怎么工作
   - 一图流架构

3. **5 分钟配置**(800 字,带命令)
   - 克隆项目
   - 装依赖
   - 配置 key
   - 测试
   - 第一次调用

4. **集成到 IDE**(500 字)
   - Cursor 配置
   - Cline 配置
   - Cherry Studio

5. **实战场景**(400 字)
   - 场景 1:批量翻译
   - 场景 2:代码 review
   - 场景 3:长文总结

6. **总结 + Star + 进群**(200 字)

## 文章结构示例

```markdown
# Claude Code token 跑光别慌,3 个免费模型自动顶上

[封面图:Claude Code 警告 + free-ai-router 解决方案]

## 一、前言:token 焦虑

作为一个每天重度使用 Claude Code 的开发者,我最怕看到这两句话:

> "You've reached your limit. Resets at 3:00 PM."
> "Rate limit reached. Please try again later."

尤其是写到一半、思路正顺的时候。

## 二、解决方案:free-ai-router

我做了这个开源工具:[free-ai-router](https://github.com/fast118/free-ai-router)

**核心思路:** 当主后端(Claude / GPT)挂了,自动切到 4 个**完全免费**的后端:

| 后端 | 速度 | 模型示例 |
|------|------|----------|
| GitHub Models | 中 | gpt-4o-mini, phi-4 |
| Gemini | 快 | gemini-2.0-flash-exp |
| Groq | **极快** | llama-3.3-70b-versatile |
| OpenRouter | 中 | deepseek-chat:free |

[架构图]

## 三、5 分钟配置

### Step 1:克隆

\`\`\`bash
git clone https://github.com/fast118/free-ai-router
cd free-ai-router
\`\`\`

### Step 2:装依赖

\`\`\`bash
pip install -r requirements.txt
\`\`\`

### Step 3:申请 Key(选一个)

[详细步骤...]

### Step 4:配置

\`\`\`bash
python smart_router.py --setup
\`\`\`

### Step 5:测试 + 使用

\`\`\`bash
python smart_router.py --test
python smart_router.py "你的问题"
\`\`\`

## 四、集成到 Claude Code

等等,**Claude Code 不能直接换模型**。但你可以在 token 用完时:

1. **用 free-ai-router 在终端问问题**(不影响 Claude Code)
2. **同时用 Cursor + free-ai-router 配置**(白嫖 GPT-4o 写代码)
3. **VSCode + Cline 插件**(类似 Claude Code 体验)

## 五、实战场景

### 场景 1:批量翻译文档

\`\`\`bash
for f in docs/*.md; do
  py smart_router.py -f "$f" "翻译成英文,保持代码不变" > "en_${f}"
done
\`\`\`

### 场景 2:代码 review

\`\`\`bash
py smart_router.py -f main.py "找出所有 bug 和改进点"
\`\`\`

## 六、写在最后

⭐ 项目地址:https://github.com/fast118/free-ai-router

进微信群交流(见项目 README):
[群二维码]
```