"""test_server.py — server v0.1 单元测试
跑法: python -X utf8 -m unittest test_server.py -v
"""
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent))
import server  # noqa


class TestListModels(unittest.TestCase):

    def test_list_models_basic(self):
        """聚合多 provider 的 models"""
        # mock router
        router = MagicMock()
        router.config = {"default_model": "deepseek-chat"}
        p1 = MagicMock()
        p1.enabled = True
        p1.name = "minimax_1"
        p1.models = ["M3", "M2.7"]
        p2 = MagicMock()
        p2.enabled = True
        p2.name = "deepseek_1"
        p2.models = ["deepseek-chat"]
        p3 = MagicMock()
        p3.enabled = False
        p3.name = "disabled_provider"
        p3.models = ["x"]
        router.providers = [p1, p2, p3]

        models = server.list_models(router)
        # 至少 4 个 (2 minimax + 1 deepseek + 1 default)
        self.assertGreaterEqual(len(models), 4)
        ids = [m["id"] for m in models]
        self.assertIn("M3", ids)
        self.assertIn("M2.7", ids)
        self.assertIn("deepseek-chat", ids)
        # disabled 的不该出现
        self.assertNotIn("x", ids)
        # owned_by 标对了
        for m in models:
            if m["id"] == "M3":
                self.assertEqual(m["owned_by"], "minimax_1")


class TestHandleChat(unittest.TestCase):

    def setUp(self):
        self.router = MagicMock()
        self.router.config = {"default_model": "deepseek-chat"}
        # mock ask 返回值
        self.mock_response = MagicMock()
        self.mock_response.choices = [MagicMock()]
        self.mock_response.choices[0].message.content = "mock answer"
        self.router.ask.return_value = (self.mock_response.choices[0].message.content, "minimax_1", "MiniMax-M3")

    def test_basic(self):
        body = {
            "model": "MiniMax-M3",
            "messages": [
                {"role": "system", "content": "你是助手"},
                {"role": "user", "content": "你好"},
            ],
            "temperature": 0.5,
            "max_tokens": 1024,
        }
        data, err = server.handle_chat_completions(self.router, body)
        self.assertIsNone(err)
        self.assertEqual(data["object"], "chat.completion")
        self.assertEqual(data["model"], "MiniMax-M3")
        self.assertEqual(data["choices"][0]["message"]["content"], "mock answer")
        # 调了 router
        self.router.ask.assert_called_once()
        # 验证 prompt 拼对了 (system + user)
        args, kwargs = self.router.ask.call_args
        self.assertIn("系统: 你是助手", args[0])
        self.assertIn("用户: 你好", args[0])

    def test_empty_messages(self):
        data, err = server.handle_chat_completions(self.router, {"messages": []})
        self.assertIsNone(data)
        self.assertIsNotNone(err)
        self.assertIn("messages 字段为空", err["error"]["message"])

    def test_uses_default_model(self):
        """没指定 model 时用 default"""
        body = {"messages": [{"role": "user", "content": "hi"}]}
        server.handle_chat_completions(self.router, body)
        # 验证传给 ask 的是 default
        args, kwargs = self.router.ask.call_args
        self.assertEqual(kwargs.get("model"), "deepseek-chat")

    def test_meta_includes_provider(self):
        body = {"messages": [{"role": "user", "content": "test"}]}
        data, err = server.handle_chat_completions(self.router, body)
        self.assertEqual(data["_meta"]["provider"], "minimax_1")
        self.assertEqual(data["_meta"]["model_used"], "MiniMax-M3")

    def test_response_id_format(self):
        body = {"messages": [{"role": "user", "content": "x"}]}
        data, _ = server.handle_chat_completions(self.router, body)
        self.assertTrue(data["id"].startswith("chatcmpl-"))
        self.assertEqual(len(data["id"]), len("chatcmpl-") + 24)

    def test_usage_estimated(self):
        body = {"messages": [{"role": "user", "content": "hello world"}]}
        data, _ = server.handle_chat_completions(self.router, body)
        # 简化估算: prompt_tokens = len("用户: hello world") = 12 chars
        self.assertGreater(data["usage"]["prompt_tokens"], 0)
        self.assertGreater(data["usage"]["completion_tokens"], 0)
        self.assertEqual(
            data["usage"]["total_tokens"],
            data["usage"]["prompt_tokens"] + data["usage"]["completion_tokens"],
        )


class TestHandleCompletions(unittest.TestCase):

    def test_legacy(self):
        """legacy /v1/completions 走 prompt 字段"""
        router = MagicMock()
        router.config = {"default_model": "deepseek-chat"}
        mock = MagicMock()
        mock.choices = [MagicMock()]
        mock.choices[0].message.content = "ok"
        router.ask.return_value = ("ok", "ds1", "deepseek-chat")
        body = {"prompt": "say hi", "model": "deepseek-chat"}
        data, err = server.handle_completions(router, body)
        self.assertIsNone(err)
        self.assertEqual(data["choices"][0]["message"]["content"], "ok")
        # prompt 透传到 chat 格式
        args, _ = router.ask.call_args
        self.assertIn("用户: say hi", args[0])

    def test_empty_prompt(self):
        router = MagicMock()
        body = {"prompt": ""}
        data, err = server.handle_completions(router, body)
        self.assertIsNone(data)
        self.assertIn("prompt 字段为空", err["error"]["message"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
