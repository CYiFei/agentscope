# test_deepseek — DeepSeek 测试用例

基于 AgentScope + DeepSeek 的场景化测试集合。每个用例独立可运行，
覆盖流式输出、多轮对话、工具调用、结构化输出、HITL、事件序列等。

## 运行方式

```bash
export DEEPSEEK_API_KEY=sk-...      # 必填；可选 DEEPSEEK_BASE_URL 覆盖接口地址
cd test_deepseek
python debug_deepseek.py          # 基础单轮对话（原迁移版）
python test_multi_turn.py          # 场景1：多轮对话 / 上下文保持
python test_streaming.py           # 场景2：流式 vs 非流式
python test_tool_call.py           # 场景3：工具调用
python test_structured_output.py   # 场景4：结构化输出
python test_custom_url.py          # 场景5：自定义 base_url
python test_error_handling.py      # 场景6：错误处理与重试
python test_event_sequence.py      # 场景7：事件序列完整性校验
python test_concurrent_tools.py    # 场景8：并发工具调用
python test_hitl.py                # 场景9：Human-in-the-loop 人机交互
```

> key 从环境变量 `DEEPSEEK_API_KEY` 读取，未设置时脚本会报错提示；
> `DEEPSEEK_BASE_URL` 默认 `https://api.deepseek.com`，可用于代理/网关。
> 测试默认忽略 shell 的 `http_proxy`/`all_proxy` 等代理变量（httpx 遇到
> `socks://` 等不支持的 scheme 会在构造客户端时直接报错），需要走代理时
> 显式设置 `DEEPSEEK_PROXY=http://127.0.0.1:7892`。

## 用例清单

| 文件 | 场景 | 验证点 |
|---|---|---|
| `debug_deepseek.py` | 基础单轮 | `reply_stream` + `TEXT_BLOCK_DELTA` |
| `test_multi_turn.py` | 多轮对话 | 上下文跨轮次保持 |
| `test_streaming.py` | 流式/非流式 | `stream=True` 增量 vs `stream=False` 一次性 |
| `test_tool_call.py` | 工具调用 | `FunctionTool` + `Toolkit` 消费工具结果 |
| `test_structured_output.py` | 结构化输出 | Pydantic schema 约束 |
| `test_custom_url.py` | 自定义 base_url | 代理/网关参数透传 |
| `test_error_handling.py` | 错误处理 | 错误 key 触发鉴权异常 |
| `test_event_sequence.py` | 事件序列 | REPLY_START → MODEL_CALL_START → TEXT_BLOCK_* → MODEL_CALL_END → REPLY_END 骨架顺序 + reply_id 一致性 |
| `test_concurrent_tools.py` | 并发工具 | 多个 `is_concurrency_safe=True` 工具同批并发执行，结果写回上下文 |
| `test_hitl.py` | HITL | `RequireUserConfirmEvent` 暂停 → `UserConfirmResultEvent` 恢复 |