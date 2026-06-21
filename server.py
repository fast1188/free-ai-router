"""server.py — OpenAI 兼容 HTTP server (sillytavern / lm-studio 友好) v0.1

把 free-ai-router 8 provider 暴露成 OpenAI /v1/chat/completions 标准 endpoint.
0 依赖 · 用 stdlib http.server.
sillytavern / LM Studio / Open WebUI 等工具只需把 base URL 改成 http://localhost:8765/v1

用法:
    py server.py                       # 默认 :8765
    py server.py --port 9000           # 自定义端口
    py server.py --host 0.0.0.0        # 局域网暴露

API:
    GET  /v1/models                    # 列出所有可用模型
    GET  /health                       # 健康检查
    POST /v1/chat/completions          # OpenAI 兼容 chat (走 smart_router)
    POST /v1/completions               # legacy completions (用 chat 模拟)

测试:
    py -X utf8 -m unittest test_server.py -v
"""
import argparse
import json
import sys
import time
import uuid
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from datetime import datetime
from pathlib import Path

# GBK 兜底
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# 复用 smart_router
sys.path.insert(0, str(Path(__file__).parent))
try:
    from smart_router import Router, load_health_state
    HAS_ROUTER = True
except ImportError as e:
    HAS_ROUTER = False
    _router_err = str(e)


def list_models(router) -> list:
    """聚合所有 provider 的 models, 标 provider 前缀"""
    models = []
    for p in router.providers:
        if not p.enabled:
            continue
        for m in p.models:
            models.append({
                "id": m,
                "object": "model",
                "created": int(time.time()),
                "owned_by": p.name,
            })
    # 标 default
    if router.config.get("default_model"):
        models.append({
            "id": router.config["default_model"],
            "object": "model",
            "created": int(time.time()),
            "owned_by": "default",
        })
    return models


def openai_error(message: str, err_type: str = "invalid_request_error", code: int = 400) -> dict:
    return {
        "error": {
            "message": message,
            "type": err_type,
            "param": None,
            "code": code,
        }
    }


def handle_chat_completions(router, body: dict) -> dict:
    """POST /v1/chat/completions 主逻辑"""
    messages = body.get("messages", [])
    if not messages:
        return None, openai_error("messages 字段为空", code=400)
    model = body.get("model", router.config.get("default_model", "deepseek-chat"))
    temperature = body.get("temperature", 0.7)
    max_tokens = body.get("max_tokens", 2048)
    stream = body.get("stream", False)

    # 把 messages 拼成单个 prompt (simple 模式, 不维护 system/assistant 角色历史)
    # 高级模式可后续支持 messages 数组
    prompt_parts = []
    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")
        if role == "system":
            prompt_parts.append(f"系统: {content}")
        elif role == "assistant":
            prompt_parts.append(f"AI: {content}")
        elif role == "user":
            prompt_parts.append(f"用户: {content}")
    prompt = "\n\n".join(prompt_parts)
    if not prompt:
        return None, openai_error("所有 messages.content 都为空", code=400)

    # 调 router
    try:
        response, prov_name, model_used = router.ask(
            prompt, model=model, temperature=temperature, max_tokens=max_tokens, stream=False
        )
    except Exception as e:
        return None, openai_error(f"router 异常: {e}", err_type="server_error", code=500)

    # 返回 OpenAI 格式
    return {
        "id": f"chatcmpl-{uuid.uuid4().hex[:24]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model_used,
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": response},
            "finish_reason": "stop",
        }],
        "usage": {
            "prompt_tokens": len(prompt),  # 简化估算
            "completion_tokens": len(response),
            "total_tokens": len(prompt) + len(response),
        },
        "_meta": {  # 自定义, 不影响 OpenAI 兼容
            "provider": prov_name,
            "model_used": model_used,
        },
    }, None


def handle_completions(router, body: dict) -> dict:
    """POST /v1/completions (legacy) - 简化为单 prompt"""
    prompt = body.get("prompt", "")
    if not prompt:
        return None, openai_error("prompt 字段为空", code=400)
    # 转成 chat 格式复用
    body2 = {"messages": [{"role": "user", "content": prompt}], "model": body.get("model")}
    body2.update({k: v for k, v in body.items() if k in ("temperature", "max_tokens", "stream")})
    return handle_chat_completions(router, body2)


class Handler(BaseHTTPRequestHandler):
    """HTTP request handler"""

    # 共享 router 实例 (server 启动时创建)
    router = None
    server_started_at = None

    def log_message(self, fmt, *args):
        """改成 log 到 stderr 带 timestamp"""
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sys.stderr.write(f"[{ts}] {self.address_string()} {fmt % args}\n")
        sys.stderr.flush()

    def _send_json(self, status: int, body: dict):
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")  # CORS
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        """CORS preflight"""
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        if self.path == "/health":
            self._send_json(200, {"status": "ok", "ts": datetime.now().isoformat()})
        elif self.path == "/v1/models":
            models = list_models(self.router)
            self._send_json(200, {"object": "list", "data": models})
        elif self.path == "/" or self.path == "/index.html":
            html = "<h1>free-ai-router OpenAI 兼容 server</h1><p>POST /v1/chat/completions</p>"
            data = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        else:
            self._send_json(404, openai_error(f"路径不存在: {self.path}", code=404))

    def do_POST(self):
        # 读 body
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            self._send_json(400, openai_error("Content-Length = 0", code=400))
            return
        try:
            raw = self.rfile.read(length).decode("utf-8")
            body = json.loads(raw)
        except json.JSONDecodeError as e:
            self._send_json(400, openai_error(f"JSON 解析失败: {e}", code=400))
            return

        # 路由
        if self.path == "/v1/chat/completions":
            data, err = handle_chat_completions(self.router, body)
        elif self.path == "/v1/completions":
            data, err = handle_completions(self.router, body)
        else:
            self._send_json(404, openai_error(f"路径不存在: {self.path}", code=404))
            return

        if err:
            self._send_json(400, err)
        else:
            self._send_json(200, data)


def run_server(host: str = "127.0.0.1", port: int = 8765):
    if not HAS_ROUTER:
        print(f"✗ smart_router 导入失败: {_router_err}", file=sys.stderr)
        print(f"  pip install openai", file=sys.stderr)
        sys.exit(1)

    router = Router()
    Handler.router = router
    Handler.server_started_at = time.time()

    server = ThreadingHTTPServer((host, port), Handler)
    print(f"✓ free-ai-router OpenAI 兼容 server")
    print(f"  listen: http://{host}:{port}")
    print(f"  endpoints:")
    print(f"    GET  /v1/models")
    print(f"    POST /v1/chat/completions")
    print(f"    GET  /health")
    print(f"  providers: {len([p for p in router.providers if p.enabled])} enabled, {len(router.providers)} total")
    print(f"  health_state: {'loaded' if router.health_state else 'none (will use all)'}")
    print(f"  按 Ctrl+C 停止")
    print()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopping...")
        server.shutdown()


def main():
    ap = argparse.ArgumentParser(description="OpenAI 兼容 server (sillytavern/lm-studio 友好)")
    ap.add_argument("--host", default="127.0.0.1", help="监听地址 (默认 127.0.0.1)")
    ap.add_argument("--port", type=int, default=8765, help="监听端口 (默认 8765)")
    args = ap.parse_args()
    run_server(args.host, args.port)


if __name__ == "__main__":
    main()
