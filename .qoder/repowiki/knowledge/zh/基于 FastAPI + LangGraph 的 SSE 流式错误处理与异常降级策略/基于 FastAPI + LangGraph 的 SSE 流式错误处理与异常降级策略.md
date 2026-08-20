---
kind: error_handling
name: 基于 FastAPI + LangGraph 的 SSE 流式错误处理与异常降级策略
category: error_handling
scope:
    - '**'
source_files:
    - workflow-studio/backend/app/main.py
    - workflow-studio/backend/app/graph.py
    - workflow-studio/backend/app/nodes.py
    - workflow-studio/frontend/src/composables/useWorkflowSSE.ts
    - workflow-studio/frontend/src/stores/workflow.ts
---

## 1. 整体方案

后端采用 **FastAPI** 作为 Web 框架，工作流引擎使用 **LangGraph**（`StateGraph` + `interrupt_before` 人工审核中断机制）。错误处理贯穿两条路径：
- **HTTP 层**：通过 FastAPI 的 `HTTPException` 返回结构化错误响应。
- **SSE 流式事件层**：在 `StreamingResponse` 内部用 `try/except Exception` 捕获所有异常，并以统一的 `{type: 'error', message: str(e)}` 事件推送到前端。

前端通过 `fetch` + `ReadableStream` 消费 SSE，对每个事件行做 `JSON.parse` 并 `catch` 解析错误后忽略；网络级异常则记录到日志状态中。

## 2. 关键文件与位置

| 文件 | 职责 |
|---|---|
| `backend/app/main.py` | FastAPI 路由、全局图实例、SSE 事件流、统一异常转事件 |
| `backend/app/graph.py` | LangGraph 图构建、`interrupt_before=['review']` 中断点配置、SQLite 检查点持久化 |
| `backend/app/nodes.py` | 各节点实现，含 JSON 解析失败时的降级逻辑 |
| `backend/app/tools.py` | 工具函数（模拟搜索），无显式错误抛出 |
| `frontend/src/composables/useWorkflowSSE.ts` | SSE 客户端，事件分发、网络异常捕获、错误事件渲染 |
| `frontend/src/stores/workflow.ts` | Pinia store，维护运行态、日志、节点状态 |

## 3. 架构与约定

### 3.1 后端异常 → SSE 事件映射
- `start_workflow` 和 `submit_review` 两个长连接端点在各自的 `event_stream()` 生成器内包裹 `try/except Exception as e`，将任何未捕获异常转换为 `data: {"type":"error","message":...}` 事件推送给前端，保证 SSE 连接不会因异常而静默断开。
- 正常完成时发送 `{type:"completed"}`；被 LangGraph 中断时发送 `{type:"interrupted", at:"review", workflow_id:...}`，由前端切换到“等待人工审核”状态。
- 非流式接口 `/api/workflow/state/{workflow_id}` 在找不到线程时直接 `raise HTTPException(404, "工作流不存在")`，走 FastAPI 默认 JSON 错误响应。

### 3.2 工作流内部降级
- `plan_node` 调用 LLM 后尝试 `json.loads(response.content)`，若解析失败或结果不是 list，则回退为 `[question]`，避免整个工作流崩溃。
- 审核分支 `route_after_review` 内置防环保护：当 `iteration_count >= 3` 时强制走向 `output`，防止拒绝循环无限迭代。

### 3.3 前端错误处理约定
- SSE 事件类型集中定义在 `@/types/workflow`（`SSEEvent` 联合类型），`handleSSEEvent` 用 `switch` 分派，新增事件需在此扩展。
- 网络层异常（`fetch` 抛错）在 `startWorkflow` / `submitReview` 的 `catch` 中设置 `isRunning=false` 并追加日志。
- 每行 SSE 数据 `JSON.parse` 失败时 `catch` 后直接忽略，容忍部分损坏的事件片段。
- 错误信息以日志形式展示（`logs.value.push('❌ 错误: ...')`），没有独立的错误弹窗组件。

## 4. 约束与规则

- **SSE 必须保持连接存活**：所有事件流内部必须用 `try/except Exception` 包裹，禁止让异常冒泡到 `StreamingResponse` 外层导致连接中断。（依据：`main.py` 两处 `event_stream` 均如此实现）
- **HTTP 错误使用 FastAPI 标准异常**：非流式接口应通过 `raise HTTPException(status_code, detail)` 返回，而非手动构造 Response。（依据：`get_workflow_state` 中对缺失工作流的 404 处理）
- **LLM/工具调用需具备降级路径**：节点内外部依赖失败时应回退到保守结果，而不是向上抛出异常。（依据：`plan_node` 的 JSON 解析降级）
- **审核循环必须有上限**：`iteration_count` 达到阈值后强制输出，避免死循环。（依据：`graph.py` 中 `route_after_review` 的硬编码保护）
- **前端 SSE 解析容错**：单行 JSON 解析失败不中断流，仅忽略该行。（依据：`useWorkflowSSE.ts` 中 `try/JSON.parse` 的 catch 注释“忽略解析错误”）

## 5. 缺失与改进空间

- 没有自定义异常类型或错误码枚举，错误信息以字符串形式透传，不利于前端分类处理。
- 工具函数（`tools.py`）未做任何参数校验或异常处理，若未来接入真实 API 可能成为隐患点。
- 前端缺少统一的错误提示 UI（如 Toast），错误仅体现在日志面板中，用户感知较弱。
- 未使用 FastAPI 的 `exception_handler` 注册全局异常处理器来统一格式化错误响应。