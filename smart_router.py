"""
smart_router.py - 智能多后端 AI 路由器
========================================
链式 fallback: 按优先级依次尝试多个后端,失败自动切换下一个
内置 4 个免费后端: GitHub Models / Gemini / Groq / OpenRouter
随时启用/禁用,自动跳过无 key 的

用法:
  py smart_router.py "你的问题"
  py smart_router.py -m gpt-4o-mini "问题"
  py smart_router.py -f 文件路径 "对这个文件做处理"
  py smart_router.py --status            # 查看各后端状态
  py smart_router.py --test              # 测试所有后端
  py smart_router.py --setup             # 引导配置新 key
  py smart_router.py --stream "问题"     # 流式输出
"""

import os
import sys
import json
import time
from pathlib import Path

from openai import OpenAI, APIError, RateLimitError, APIStatusError

BASE_DIR = Path(__file__).parent
CONFIG_FILE = BASE_DIR / "router_config.json"


DEFAULT_CONFIG = {
    "default_model": "gpt-4o-mini",
    "cooldown_seconds": 60,
    "providers": [
        {
            "name": "github_models",
            "label": "GitHub Models (免费)",
            "base_url": "https://models.inference.ai.azure.com",
            "api_key_file": "11.txt",
            "models": [
                "gpt-4o-mini", "gpt-4o", "o1-mini",
                "llama-3.3-70b", "phi-4", "deepseek-r1",
                "mistral-large-2407", "cohere-command-r-plus"
            ],
            "priority": 1,
            "enabled": True,
        },
        {
            "name": "gemini",
            "label": "Google Gemini (免费层)",
            "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
            "api_key_env": "GEMINI_API_KEY",
            "models": [
                "gemini-2.0-flash-exp",
                "gemini-1.5-flash",
                "gemini-1.5-pro",
            ],
            "priority": 2,
            "enabled": False,
        },
        {
            "name": "groq",
            "label": "Groq (超快推理,免费)",
            "base_url": "https://api.groq.com/openai/v1",
            "api_key_env": "GROQ_API_KEY",
            "models": [
                "llama-3.3-70b-versatile",
                "llama-3.1-8b-instant",
                "mixtral-8x7b-32768",
                "deepseek-r1-distill-llama-70b",
            ],
            "priority": 3,
            "enabled": False,
        },
        {
            "name": "openrouter",
            "label": "OpenRouter (有免费模型)",
            "base_url": "https://openrouter.ai/api/v1",
            "api_key_env": "OPENROUTER_API_KEY",
            "models": [
                "meta-llama/llama-3.3-70b-instruct:free",
                "google/gemini-2.0-flash-exp:free",
                "deepseek/deepseek-chat:free",
                "qwen/qwen-2.5-72b-instruct:free",
            ],
            "priority": 4,
            "enabled": False,
        },
    ],
}


# ============= 工具函数 =============

def load_config():
    if not CONFIG_FILE.exists():
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)
        return DEFAULT_CONFIG
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    # 合并新增的 provider (升级时)
    existing = {p["name"] for p in cfg.get("providers", [])}
    for p in DEFAULT_CONFIG["providers"]:
        if p["name"] not in existing:
            cfg["providers"].append(p)
    return cfg


def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


def get_api_key(provider):
    """从多种来源读取 key"""
    if "api_key_file" in provider:
        path = BASE_DIR / provider["api_key_file"]
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                lines = [
                    line.strip() for line in content.splitlines()
                    if line.strip() and not line.strip().startswith("#")
                ]
                for line in lines:
                    if "=" in line and "TOKEN" in line.upper():
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
                if lines:
                    return lines[0]
    if "api_key_env" in provider:
        return os.getenv(provider["api_key_env"])
    return None


def mask(key: str) -> str:
    if not key or len(key) < 12:
        return "****"
    return f"{key[:4]}...{key[-4:]} ({len(key)})"


# ============= Provider =============

class Provider:
    def __init__(self, config):
        self.config = config
        self.name = config["name"]
        self.label = config.get("label", self.name)
        self.base_url = config["base_url"]
        self.api_key = get_api_key(config)
        self.models = config["models"]
        self.priority = config.get("priority", 100)
        self.enabled = config.get("enabled", True)
        self.cooldown_until = 0
        self.cooldown_seconds = 60
        self.last_error = None
        self.success_count = 0
        self.fail_count = 0
        self.client = None

        if self.api_key:
            try:
                self.client = OpenAI(
                    base_url=self.base_url,
                    api_key=self.api_key,
                    timeout=120,
                )
            except Exception as e:
                self.last_error = f"client init: {e}"

    def status_text(self):
        if not self.enabled:
            return "[已禁用]"
        if not self.api_key:
            return "[无 key]"
        if not self.client:
            return "[初始化失败]"
        if self.cooldown_until > time.time():
            remaining = int(self.cooldown_until - time.time())
            return f"[冷却 {remaining}s]"
        return "[可用]"

    def is_available(self):
        return (
            self.enabled
            and self.api_key
            and self.client
            and self.cooldown_until <= time.time()
        )

    def has_model(self, model: str) -> bool:
        return any(model == m or model in m for m in self.models)

    def mark_success(self):
        self.success_count += 1
        self.cooldown_until = 0
        self.last_error = None

    def mark_failure(self, reason: str, cooldown: int = 60):
        self.fail_count += 1
        self.last_error = reason[:200]
        self.cooldown_until = time.time() + cooldown


# ============= 路由器 =============

class Router:
    def __init__(self):
        self.config = load_config()
        self.cooldown_seconds = self.config.get("cooldown_seconds", 60)
        self.providers = sorted(
            [Provider(p) for p in self.config["providers"]],
            key=lambda x: x.priority,
        )

    def list_providers(self):
        return self.providers

    def ask(self, prompt: str, model: str = None, system: str = None,
            temperature: float = 0.7, max_tokens: int = 2048,
            stream: bool = False):
        """链式 fallback,返回 (response, provider_name, model_used)"""

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        errors = []
        for p in self.providers:
            if not p.is_available():
                continue
            if model:
                if not p.has_model(model):
                    continue
                use_model = model
            else:
                use_model = self.config.get("default_model", "gpt-4o-mini")
                if not p.has_model(use_model):
                    use_model = p.models[0]

            try:
                if stream:
                    stream_iter = p.client.chat.completions.create(
                        model=use_model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        stream=True,
                    )
                    # 流式:返回一个生成器,由调用方消费
                    return StreamWrapper(p, stream_iter, use_model)
                else:
                    r = p.client.chat.completions.create(
                        model=use_model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                    p.mark_success()
                    return r, p.name, use_model
            except (RateLimitError, APIStatusError) as e:
                p.mark_failure(f"{type(e).__name__}: {e}", self.cooldown_seconds)
                errors.append(f"{p.name}: [限流/错误] {str(e)[:80]}")
                continue
            except APIError as e:
                p.mark_failure(f"APIError: {e}", self.cooldown_seconds)
                errors.append(f"{p.name}: [API] {str(e)[:80]}")
                continue
            except Exception as e:
                p.mark_failure(f"{type(e).__name__}: {e}", self.cooldown_seconds)
                errors.append(f"{p.name}: [异常] {str(e)[:80]}")
                continue

        raise RuntimeError("所有后端都失败:\n  " + "\n  ".join(errors))

    def status_report(self):
        lines = []
        lines.append("─" * 72)
        lines.append(f"{'#':<3} {'Provider':<14} {'状态':<12} {'优先级':<6} {'成功':<5} {'失败':<5} 备注")
        lines.append("─" * 72)
        for i, p in enumerate(self.providers, 1):
            extra = ""
            if p.api_key:
                extra = f"key={mask(p.api_key)}"
            else:
                extra = "需配置"
            err = p.last_error[:30] if p.last_error else ""
            lines.append(
                f"{i:<3} {p.name:<14} {p.status_text():<12} {p.priority:<6} "
                f"{p.success_count:<5} {p.fail_count:<5} {err}"
            )
        lines.append("─" * 72)
        # 列出可用 key
        lines.append("\n[Key 状态]")
        for p in self.providers:
            if "api_key_env" in p.config:
                env_val = os.getenv(p.config["api_key_env"])
                lines.append(f"  {p.name}: env={p.config['api_key_env']} = {mask(env_val) if env_val else '(未设置)'}")
        return "\n".join(lines)


class StreamWrapper:
    """流式响应包装器,带 fallback 标记"""
    def __init__(self, provider, stream_iter, model):
        self.provider = provider
        self.stream = stream_iter
        self.model = model
        self.chunks = []

    def __iter__(self):
        for chunk in self.stream:
            delta = chunk.choices[0].delta.content if chunk.choices else None
            if delta:
                self.chunks.append(delta)
                yield delta
        self.provider.mark_success()


# ============= CLI =============

def cmd_setup():
    """引导配置新 key"""
    print("=" * 60)
    print(" 智能路由器 - 引导配置")
    print("=" * 60)
    print()
    print("选择一个后端配置 key:")
    print()

    cfg = load_config()
    optional = [p for p in cfg["providers"]
                if p["name"] != "github_models" and not p.get("enabled")]

    if not optional:
        print("所有后端都已配置!")
        return

    for i, p in enumerate(optional, 1):
        print(f"  {i}. {p['label']}")
        if "api_key_env" in p:
            print(f"     环境变量: {p['api_key_env']}")
        if "models" in p:
            print(f"     模型: {', '.join(p['models'][:3])}{'...' if len(p['models']) > 3 else ''}")
        print(f"     申请地址: {get_signup_url(p['name'])}")
        print()

    print("  0. 退出")
    print()
    choice = input("选择 [0/1/2/3/4]: ").strip()
    if choice == "0" or not choice:
        return
    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(optional):
            return
    except ValueError:
        return

    target = optional[idx]
    api_key = input(f"\n请输入 {target['label']} 的 API key (不会显示): ").strip()

    if not api_key:
        print("未输入 key, 取消")
        return

    # 存到环境变量提示
    env_name = target.get("api_key_env", "")
    print()
    print(f"✓ Key 拿到 (长度 {len(api_key)})")
    print()
    print("如何永久保存(选一种):")
    print()
    print(f"[方法 1] 写一个 key 文件到 {BASE_DIR}/{target['name']}.key.txt")
    key_file = BASE_DIR / f"{target['name']}.key.txt"
    with open(key_file, "w", encoding="utf-8") as f:
        f.write(api_key)
    print(f"    已自动写到: {key_file}")

    print()
    print(f"[方法 2] 设环境变量(推荐系统级):")
    print(f"    setx {env_name} \"{api_key}\"")

    # 启用 provider
    for p in cfg["providers"]:
        if p["name"] == target["name"]:
            p["enabled"] = True
            # 切换为读 key_file
            p.pop("api_key_env", None)
            p["api_key_file"] = f"{target['name']}.key.txt"
    save_config(cfg)
    print()
    print(f"✓ {target['label']} 已启用!")


def get_signup_url(name: str) -> str:
    return {
        "gemini": "https://aistudio.google.com/apikey",
        "groq": "https://console.groq.com/keys",
        "openrouter": "https://openrouter.ai/keys",
        "github_models": "https://github.com/settings/personal-access-tokens",
    }.get(name, "(未知)")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="智能多后端 AI 路由器")
    parser.add_argument("prompt", nargs="*", help="问题")
    parser.add_argument("-m", "--model", help="指定模型,如 gpt-4o-mini")
    parser.add_argument("-f", "--file", help="读文件作为上下文")
    parser.add_argument("-s", "--system", default="你是一个有帮助的助手,回答简洁准确。")
    parser.add_argument("--stream", action="store_true", help="流式输出")
    parser.add_argument("--status", action="store_true", help="查看状态")
    parser.add_argument("--test", action="store_true", help="测试所有可用后端")
    parser.add_argument("--config", action="store_true", help="显示配置文件路径")
    parser.add_argument("--setup", action="store_true", help="配置新 key")
    parser.add_argument("--list", action="store_true", help="列出所有可用模型")
    args = parser.parse_args()

    router = Router()

    if args.setup:
        cmd_setup()
        return

    if args.config:
        print(f"配置文件: {CONFIG_FILE}")
        print(f"目录: {BASE_DIR}")
        return

    if args.status:
        print(router.status_report())
        return

    if args.list:
        print("所有 provider 的模型:")
        for p in router.providers:
            avail = "✓" if p.is_available() else "✗"
            print(f"\n  [{avail}] {p.name} ({p.label})")
            for m in p.models:
                print(f"      - {m}")
        return

    if args.test:
        print("测试所有可用后端...")
        for p in router.providers:
            if not p.is_available():
                reason = "无 key" if not p.api_key else ("冷却中" if p.cooldown_until > time.time() else "已禁用")
                print(f"  ⊘ {p.name:<14} 跳过 ({reason})")
                continue
            use_model = p.models[0]
            try:
                r, name, model = router.ask("回复 OK", model=use_model, max_tokens=20)
                txt = r.choices[0].message.content[:50].replace("\n", " ")
                print(f"  ✓ {p.name:<14} {model:<30} → {txt}")
            except Exception as e:
                print(f"  ✗ {p.name:<14} {use_model:<30} → {str(e)[:60]}")
        return

    if not args.prompt and not args.file:
        parser.print_help()
        return

    # 拼装 prompt
    prompt = " ".join(args.prompt) if args.prompt else "请处理这个文件"
    if args.file:
        if not os.path.exists(args.file):
            print(f"[错误] 文件不存在: {args.file}")
            sys.exit(1)
        with open(args.file, "r", encoding="utf-8") as f:
            content = f.read()
        prompt = f"文件内容:\n```\n{content}\n```\n\n任务: {prompt}"

    try:
        if args.stream:
            result = router.ask(
                prompt, model=args.model, system=args.system,
                stream=True, max_tokens=2048
            )
            if isinstance(result, StreamWrapper):
                print(f"\n[{result.provider.name} / {result.model}] ", end="", flush=True)
                for chunk in result:
                    print(chunk, end="", flush=True)
                print()
            return

        r, name, model = router.ask(
            prompt, model=args.model, system=args.system, max_tokens=2048
        )
        content = r.choices[0].message.content
        print(f"\n[{name} / {model}]")
        print("─" * 60)
        print(content)
        print("─" * 60)
        if r.usage:
            u = r.usage
            print(f"[用量] 输入: {u.prompt_tokens} | 输出: {u.completion_tokens} | 合计: {u.total_tokens}")
    except Exception as e:
        print(f"\n[错误] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
