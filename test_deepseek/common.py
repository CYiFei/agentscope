# -*- coding: utf-8 -*-
"""DeepSeek 测试公共配置。

key 从环境变量 DEEPSEEK_API_KEY 读取，不内嵌明文。
运行前请先 export DEEPSEEK_API_KEY=sk-...
"""
import os

import httpx

from agentscope.model import DeepSeekChatModel
from agentscope.credential import DeepSeekCredential

API_KEY = os.environ.get("DEEPSEEK_API_KEY")
BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
PROXY = os.environ.get("DEEPSEEK_PROXY")


def _build_http_client() -> httpx.AsyncClient:
    """构造模型用的 httpx 客户端。

    默认 trust_env=False：忽略 shell 里的 http_proxy/all_proxy 等变量。
    httpx 遇到 socks:// 之类不支持的 scheme 会在构造客户端时直接抛
    ValueError，测试还没发请求就崩溃。需要走代理时显式设置
    DEEPSEEK_PROXY，例如 DEEPSEEK_PROXY=http://127.0.0.1:7892。
    """
    if PROXY:
        return httpx.AsyncClient(proxy=PROXY, trust_env=False)
    return httpx.AsyncClient(trust_env=False)


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
    api_key: str | None = None,
) -> DeepSeekChatModel:
    """构造 DeepSeek 模型客户端。"""
    return DeepSeekChatModel(
        credential=build_credential(api_key=api_key, base_url=base_url),
        model=model,
        stream=stream,
        client_kwargs={"http_client": _build_http_client()},
    )
