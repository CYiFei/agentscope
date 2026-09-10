# -*- coding: utf-8 -*-
"""场景2：流式 vs 非流式输出。

验证 stream=True（增量 delta）与 stream=False（一次性返回）两种模式。

运行: python test_deepseek/test_streaming.py
"""
import asyncio

from agentscope.agent import Agent
from agentscope.message import UserMsg

from common import build_model


async def main() -> None:
    question = "用三句话介绍北京。"

    print("=== 流式 (stream=True) ===")
    agent_stream = Agent(
        name="s",
        system_prompt="你是一个助手。",
        model=build_model(stream=True),
    )
    await agent_stream.observe(UserMsg("user", question))
    async for event in agent_stream.reply_stream():
        if event.type == "TEXT_BLOCK_DELTA":
            print(event.delta, end="", flush=True)

    print("\n\n=== 非流式 (stream=False) ===")
    agent_once = Agent(
        name="n",
        system_prompt="你是一个助手。",
        model=build_model(stream=False),
    )
    await agent_once.observe(UserMsg("user", question))
    async for event in agent_once.reply_stream():
        if event.type == "TEXT_BLOCK_DELTA":
            print(event.delta, end="", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
