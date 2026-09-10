# -*- coding: utf-8 -*-
"""场景9：Human-in-the-loop（HITL）人机交互。

验证"需要用户确认"的工具调用会暂停回复并抛出
`RequireUserConfirmEvent`，外部构造 `UserConfirmResultEvent` 后再调用
`reply_stream` 即可恢复执行。

运行: python test_deepseek/test_hitl.py
"""
import asyncio

from agentscope.agent import Agent
from agentscope.event import (
    ConfirmResult,
    EventType,
    RequireUserConfirmEvent,
    ToolCallBlock,
    ToolResultEndEvent,
    UserConfirmResultEvent,
)
from agentscope.message import UserMsg
from agentscope.permission import PermissionBehavior, PermissionRule
from agentscope.tool import FunctionTool, Toolkit

from common import build_model

# 记录确认前/后的工具结果状态
_states: list[str] = []


def delete_file(path: str) -> str:
    """删除指定路径的文件（危险操作，需要用户确认）。

    Args:
        path (str): 要删除的文件路径。
    """
    _states.append(f"delete_file 执行，path={path}")
    return f"已删除 {path}"


async def main() -> None:
    toolkit = Toolkit(tools=[FunctionTool(func=delete_file)])
    agent = Agent(
        name="助手",
        system_prompt=(
            "你是一个助手。当用户要求删除文件时，"
            "请调用 delete_file 工具。"
        ),
        model=build_model(),
        toolkit=toolkit,
    )
    await agent.observe(UserMsg("user", "请删除 /tmp/test.txt 这个文件。"))

    print("=== 第 1 次 reply_stream：触发工具调用并暂停 ===")
    confirm_event: RequireUserConfirmEvent | None = None
    async for event in agent.reply_stream():
        print(f"  事件: {event.type}", flush=True)
        if event.type == EventType.REQUIRE_USER_CONFIRM:
            confirm_event = event
            assert isinstance(event, RequireUserConfirmEvent)
            assert len(event.tool_calls) == 1
            print(f"  → 暂停，等待用户确认: {event.tool_calls[0].name}")
        elif event.type == EventType.TOOL_RESULT_END:
            assert isinstance(event, ToolResultEndEvent)
            _states.append(f"ToolResultEnd.state={event.state}")

    assert confirm_event is not None, "未产生 RequireUserConfirmEvent"
    assert _states == [], "确认前不应产生工具结果"

    # 构造用户确认结果（批准该工具调用）
    tc: ToolCallBlock = confirm_event.tool_calls[0]
    confirm_result = ConfirmResult(
        confirmed=True,
        tool_call=tc,
        rules=[
            PermissionRule(
                tool_name=tc.name,
                rule_content=None,
                behavior=PermissionBehavior.ALLOW,
                source="user",
            ),
        ],
    )
    resume_event = UserConfirmResultEvent(
        reply_id=confirm_event.reply_id,
        confirm_results=[confirm_result],
    )

    print("\n=== 第 2 次 reply_stream：传入确认结果，恢复执行 ===")
    async for event in agent.reply_stream(inputs=resume_event):
        if event.type == EventType.TEXT_BLOCK_DELTA:
            print(event.delta, end="", flush=True)
        elif event.type == EventType.TOOL_RESULT_END:
            print(f"\n[工具结果] state={event.state}", flush=True)

    print("\n=== 校验 ===")
    print(f"  工具执行日志: {_states}")
    assert any("delete_file 执行" in s for s in _states), "确认后工具未执行"
    print("  ✓ 用户确认后工具成功执行")
    print("\n✅ HITL 校验通过")


if __name__ == "__main__":
    asyncio.run(main())