# -*- coding: utf-8 -*-
"""场景3：工具调用（FunctionTool）。

验证 Agent 能识别需要调用工具的场景，并消费工具返回结果。

运行: python test_deepseek/test_tool_call.py
"""
import asyncio

from agentscope.agent import Agent
from agentscope.message import UserMsg
from agentscope.tool import FunctionTool, Toolkit

from common import build_model


def get_weather(city: str) -> str:
    """查询指定城市的当前天气。

    Args:
        city (str): 城市名称，例如 "北京"、"上海"
    """
    return f"{city} 今天晴，气温 25 度，微风。"


async def main() -> None:
    toolkit = Toolkit(tools=[FunctionTool(func=get_weather)])
    agent = Agent(
        name="助手",
        system_prompt="你是一个助手，当用户询问天气时请调用工具。",
        model=build_model(),
        toolkit=toolkit,
    )
    await agent.observe(UserMsg("user", "北京天气怎么样？"))
    async for event in agent.reply_stream():
        if event.type == "TEXT_BLOCK_DELTA":
            print(event.delta, end="", flush=True)
        elif event.type == "TOOL_CALL_START":
            print(f"\n[工具调用] {event.tool_call_name}", flush=True)
        elif event.type == "TOOL_RESULT_END":
            print(f"[工具结果状态] {event.state}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
