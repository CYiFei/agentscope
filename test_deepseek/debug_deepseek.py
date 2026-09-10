# -*- coding: utf-8 -*-
"""基础单轮对话测试（原 debug_deepseek.py 迁移版）。

运行: python test_deepseek/debug_deepseek.py
"""
import asyncio

from agentscope.agent import Agent
from agentscope.message import UserMsg

from common import build_model


async def main() -> None:
    agent = Agent(
        name="助手",
        system_prompt="你是一个简洁、有帮助的助手。",
        model=build_model(),
    )
    await agent.observe(UserMsg("user", "用一句话介绍 AgentScope"))
    async for event in agent.reply_stream():
        if event.type == "TEXT_BLOCK_DELTA":
            print(event.delta, end="", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
