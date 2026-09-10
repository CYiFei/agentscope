# -*- coding: utf-8 -*-
"""场景5：自定义 base_url（代理 / 网关 / OpenAI 兼容中转）。

演示如何把请求指向自定义端点，而不是默认的 https://api.deepseek.com。

运行: python test_deepseek/test_custom_url.py
"""
import asyncio

from agentscope.agent import Agent
from agentscope.message import UserMsg

from common import build_model


async def main() -> None:
    # 把 base_url 换成你的代理/网关地址即可（这里用占位地址演示参数传递）
    custom_base_url = "https://your-proxy.example.com/v1"
    print(f"使用自定义 base_url: {custom_base_url}\n")

    model = build_model(base_url=custom_base_url)
    agent = Agent(
        name="助手",
        system_prompt="你是一个助手。",
        model=model,
    )
    await agent.observe(UserMsg("user", "你好"))
    async for event in agent.reply_stream():
        if event.type == "TEXT_BLOCK_DELTA":
            print(event.delta, end="", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
