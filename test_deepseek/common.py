# -*- coding: utf-8 -*-
"""DeepSeek 测试公共配置。

key 从环境变量 DEEPSEEK_API_KEY 读取，不内嵌明文。
运行前请先 export DEEPSEEK_API_KEY=sk-...
"""
import os

from agentscope.model import DeepSeekChatModel
from agentscope.credential import DeepSeekCredential

API_KEY = os.environ.get("DEEPSEEK_API_KEY")
BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")


def build_credential(
    api_key: str | None = None,
    base_url: str | None = None,
) -> DeepSeekCredential:
    """构造 DeepSeek 凭证。"""
    key = api_key or API_KEY
    if not key:
        raise RuntimeError(
            "缺少 DeepSeek API key，请先设置环境变量 DEEPSEEK_API_KEY。",
        )
    return DeepSeekCredential(
        api_key=key,
        base_url=base_url or BASE_URL,
    )


def build_model(
    model: str = "deepseek-chat",
    stream: bool = True,
    base_url: str | None = None,
) -> DeepSeekChatModel:
    """构造 DeepSeek 模型客户端。"""
    return DeepSeekChatModel(
        credential=build_credential(base_url=base_url),
        model=model,
        stream=stream,
    )
