# -*- coding: utf-8 -*-
"""场景7：事件序列完整性校验。

验证一次完整回复中，事件的**类型与顺序**符合 AgentScope 的契约：
    REPLY_START
    MODEL_CALL_START
    TEXT_BLOCK_START / TEXT_BLOCK_DELTA / TEXT_BLOCK_END
    MODEL_CALL_END
    REPLY_END

同时检查关键字段（reply_id 一致性、model_name）非空。

运行: python test_deepseek/test_event_sequence.py
"""
import asyncio

from agentscope.agent import Agent
from agentscope.event import (
    EventType,
    ModelCallEndEvent,
    ModelCallStartEvent,
    ReplyEndEvent,
    ReplyStartEvent,
    TextBlockDeltaEvent,
    TextBlockEndEvent,
    TextBlockStartEvent,
)
from agentscope.message import UserMsg

from common import build_model

# 期望的事件类型顺序（仅取骨架，中间的 delta 块可变长）
EXPECTED_ORDER = [
    EventType.REPLY_START,
    EventType.HINT_BLOCK,  # 运行时状态注入（时间/任务/上下文用量）
    EventType.MODEL_CALL_START,
    EventType.TEXT_BLOCK_START,
    EventType.TEXT_BLOCK_DELTA,  # 可出现 0..N 次
    EventType.TEXT_BLOCK_END,
    EventType.MODEL_CALL_END,
    EventType.REPLY_END,
]


def _check_sequence(events: list) -> None:
    """把事件序列压成骨架类型列表后与 EXPECTED_ORDER 比对。"""
    types = [e.type for e in events]
    # 把连续的 TEXT_BLOCK_DELTA 折叠成一个
    skeleton = []
    for t in types:
        if t == EventType.TEXT_BLOCK_DELTA and skeleton and skeleton[-1] == t:
            continue
        skeleton.append(t)
    assert skeleton == [str(t) for t in EXPECTED_ORDER], (
        f"事件序列不匹配:\n  期望: {EXPECTED_ORDER}\n  实际: {skeleton}"
    )
    print("  ✓ 事件骨架顺序正确:", " -> ".join(skeleton))


async def main() -> None:
    agent = Agent(
        name="助手",
        system_prompt="你是一个简洁的助手。每次只用一句话回答。",
        model=build_model(),
    )
    await agent.observe(UserMsg("user", "用一句话介绍 AgentScope"))

    events = []
    async for event in agent.reply_stream():
        events.append(event)
        if event.type == EventType.TEXT_BLOCK_DELTA:
            assert isinstance(event, TextBlockDeltaEvent)
            assert event.delta, "TEXT_BLOCK_DELTA 的 delta 不应为空"

    print("=== 事件序列校验 ===")
    _check_sequence(events)

    print("\n=== 关键字段校验 ===")
    reply_ids = {e.reply_id for e in events if hasattr(e, "reply_id")}
    assert len(reply_ids) == 1, f"reply_id 不一致: {reply_ids}"
    print(f"  ✓ reply_id 一致: {reply_ids.pop()}")

    start = next(e for e in events if isinstance(e, ReplyStartEvent))
    end = next(e for e in events if isinstance(e, ReplyEndEvent))
    assert start.name == "助手"
    assert end.finished_reason is not None
    print(f"  ✓ ReplyStartEvent.name={start.name}, ReplyEndEvent.finished_reason={end.finished_reason}")

    call_start = next(e for e in events if isinstance(e, ModelCallStartEvent))
    call_end = next(e for e in events if isinstance(e, ModelCallEndEvent))
    assert call_start.model_name == "deepseek-chat"
    assert call_end.finished_reason is not None
    print(f"  ✓ ModelCallStart.model_name={call_start.model_name}, "
          f"ModelCallEnd.finished_reason={call_end.finished_reason}")

    print("\n✅ 全部事件序列校验通过")


if __name__ == "__main__":
    asyncio.run(main())