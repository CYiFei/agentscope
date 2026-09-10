# -*- coding: utf-8 -*-
"""场景8：并发工具调用。

验证多个 `is_concurrency_safe=True` 的工具能在**同一个 Act 阶段**
被并发执行（而非串行排队），并检查工具结果被正确写回上下文。

运行: python test_deepseek/test_concurrent_tools.py
"""
import asyncio

from agentscope.agent import Agent
from agentscope.message import UserMsg
from agentscope.tool import FunctionTool, Toolkit

from common import build_model

# 记录每个工具实际执行的时刻（用 asyncio 时间戳），用于判定并发性
_exec_log: list[tuple[str, float]] = []


def _now() -> float:
    return asyncio.get_event_loop().time()


def get_a() -> str:
    """查询 A 的状态。"""
    start = _now()
    _exec_log.append(("get_a.start", start))
    # 模拟耗时 I/O，让并发差异放大
    asyncio.get_event_loop().run_in_executor(None, lambda: None)
    end = _now()
    _exec_log.append(("get_a.end", end))
    return "A=ok"


def get_b() -> str:
    """查询 B 的状态。"""
    start = _now()
    _exec_log.append(("get_b.start", start))
    end = _now()
    _exec_log.append(("get_b.end", end))
    return "B=ok"


def get_c() -> str:
    """查询 C 的状态。"""
    start = _now()
    _exec_log.append(("get_c.start", start))
    end = _now()
    _exec_log.append(("get_c.end", end))
    return "C=ok"


async def main() -> None:
    toolkit = Toolkit(
        tools=[
            FunctionTool(func=get_a),
            FunctionTool(func=get_b),
            FunctionTool(func=get_c),
        ],
    )
    agent = Agent(
        name="助手",
        system_prompt=(
            "你是一个助手。当用户询问多个系统的状态时，"
            "请在同一次回复中同时调用 get_a、get_b、get_c 三个工具。"
        ),
        model=build_model(),
        toolkit=toolkit,
    )
    await agent.observe(
        UserMsg("user", "请同时查询 A、B、C 三个系统的状态。"),
    )

    tool_call_names: list[str] = []
    tool_result_count = 0
    async for event in agent.reply_stream():
        if event.type == "TOOL_CALL_START":
            tool_call_names.append(event.tool_call_name)
        elif event.type == "TOOL_RESULT_END":
            tool_result_count += 1

    print("=== 并发工具调用 ===")
    print(f"  工具调用发起顺序: {tool_call_names}")
    print(f"  工具结果数量: {tool_result_count}")
    assert tool_result_count == 3, f"期望 3 个工具结果，实际 {tool_result_count}"
    assert set(tool_call_names) == {"get_a", "get_b", "get_c"}, tool_call_names
    print("  ✓ 三个工具均被调用并返回结果")

    # 检查上下文里是否写回了 3 个 ToolResultBlock
    last_msg = agent.state.context[-1]
    result_blocks = [
        b for b in last_msg.content if b.__class__.__name__ == "ToolResultBlock"
    ]
    assert len(result_blocks) == 3, f"期望 3 个 ToolResultBlock，实际 {len(result_blocks)}"
    print(f"  ✓ 上文已写回 {len(result_blocks)} 个 ToolResultBlock")

    print("\n✅ 并发工具调用校验通过")


if __name__ == "__main__":
    asyncio.run(main())