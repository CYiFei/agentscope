# -*- coding: utf-8 -*-
"""场景4：结构化输出（structured output）。

验证 Agent 能按要求产出符合 Pydantic schema 的结构化数据。

运行: python test_deepseek/test_structured_output.py
"""
import asyncio

from pydantic import BaseModel

from agentscope.agent import Agent
from agentscope.message import UserMsg

from common import build_model


class Person(BaseModel):
    """从文本中抽取的人物信息。"""

    name: str
    age: int
    city: str


async def main() -> None:
    agent = Agent(
        name="助手",
        system_prompt="你是一个助手，擅长从文本中抽取结构化信息。",
        model=build_model(),
    )
    await agent.observe(
        UserMsg("user", "小明，28 岁，住在上海。请抽取他的信息。"),
    )
    async for event in agent.reply_stream(structured_schema=Person):
        if event.type == "TEXT_BLOCK_DELTA":
            print(event.delta, end="", flush=True)

    # 读取最终结构化结果（best-effort，可能随版本略有差异）
    try:
        result = agent.state.reply_context.structured_output
        print("\n\n结构化结果:", result)
    except Exception as exc:  # pylint: disable=broad-except
        print(f"\n(无法读取结构化结果: {exc})")


if __name__ == "__main__":
    asyncio.run(main())
