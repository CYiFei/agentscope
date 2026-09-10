# -*- coding: utf-8 -*-
"""场景6：错误处理与重试。

演示使用错误 key 时如何捕获鉴权异常，便于在应用中做降级/提示。

运行: python test_deepseek/test_error_handling.py
"""
import asyncio

from agentscope.model import DeepSeekChatModel
from agentscope.credential import DeepSeekCredential
from agentscope.agent import Agent
from agentscope.message import UserMsg


async def main() -> None:
    # 故意使用错误 key
    bad_credential = DeepSeekCredential(api_key="sk-错误的keyxxxxxxxxxxxxxxxx")
    model = DeepSeekChatModel(credential=bad_credential, model="deepseek-chat")
    agent = Agent(
        name="助手",
        system_prompt="你是一个助手。",
        model=model,
    )
    await agent.observe(UserMsg("user", "你好"))
    try:
        async for _ in agent.reply_stream():
            pass
        print("意外：未抛出异常（请检查 key 是否有效）。")
    except Exception as exc:  # pylint: disable=broad-except
        print(f"捕获到异常（预期行为）: {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    asyncio.run(main())
