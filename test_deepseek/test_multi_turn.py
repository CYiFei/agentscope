# -*- coding: utf-8 -*-
"""场景1：多轮对话 / 上下文保持。

验证 Agent 能否在后续轮次记住前面轮次的信息。

运行: python test_deepseek/test_multi_turn.py
"""
import asyncio

from agentscope.agent import Agent
from agentscope.message import UserMsg

from common import build_model


async def main() -> None:
    agent = Agent(
        name="助手",
        system_prompt="你是一个友好的助手，请记住用户提供的信息。",
        model=build_model(),
    )
    questions = [
        "我叫小明，今年 28 岁。",
        "我刚才说我叫什么、多大了？",
        "总结一下我们到目前为止聊了什么。",
    ]
    for q in questions:
        print(f"\n>>> 用户: {q}")
        await agent.observe(UserMsg("user", q))
        async for event in agent.reply_stream():
            if event.type == "TEXT_BLOCK_DELTA":
                print(event.delta, end="", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
