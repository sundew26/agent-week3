# 审核节点 (review_node)

<cite>
**本文引用的文件**
- [nodes.py](file://workflow-studio/backend/app/nodes.py)
- [graph.py](file://workflow-studio/backend/app/graph.py)
- [state.py](file://workflow-studio/backend/app/state.py)
- [main.py](file://workflow-studio/backend/app/main.py)
- [ReviewDialog.vue](file://workflow-studio/frontend/src/components/panels/ReviewDialog.vue)
- [useWorkflowSSE.ts](file://workflow-studio/frontend/src/composables/useWorkflowSSE.ts)
- [workflow.ts](file://workflow-studio/frontend/src/types/workflow.ts)
</cite>

## 目录
1. [简介](#简介)
2. [项目结构](#项目结构)
3. [核心组件](#核心组件)
4. [架构总览](#架构总览)
5. [详细组件分析](#详细组件分析)
6. [依赖关系分析](#依赖关系分析)
7. [性能考虑](#性能考虑)
8. [故障排查指南](#故障排查指南)
9. [结论](#结论)
10. [附录](#附录)

## 简介
本技术文档聚焦于研究工作流中的“审核节点”（review_node），深入解析其 Human-in-the-loop（人在回路）机制的实现原理。重点说明：
- LangGraph 的 interrupt_before 机制如何在 review 节点暂停工作流执行，等待人工干预
- review_status 字段的状态管理，从 pending 到 approved 或 rejected 的状态转换
- 前端审核界面的集成方式、用户决策的提交流程与后端恢复执行的交互
- 审核结果的持久化存储机制（基于检查点）
- 审核流程的自定义配置与批量审核扩展指南

## 项目结构
本项目采用前后端分离架构：
- 后端使用 FastAPI + LangGraph 构建研究工作流，提供 SSE 事件流接口用于实时状态推送与人工审核提交
- 前端使用 Vue 3 + TypeScript，通过 SSE 接收事件并渲染审核对话框，调用审核接口恢复执行

```mermaid
graph TB
subgraph "前端"
FE_Review["审核对话框<br/>ReviewDialog.vue"]
FE_SSE["SSE 客户端<br/>useWorkflowSSE.ts"]
FE_Types["类型定义<br/>workflow.ts"]
end
subgraph "后端"
API_Start["启动工作流<br/>/api/workflow/start"]
API_Review["提交审核<br/>/api/workflow/review"]
Graph_Build["构建图<br/>build_research_graph()"]
Nodes["节点实现<br/>nodes.py"]
State["状态定义<br/>state.py"]
Checkpoint["检查点持久化<br/>AsyncSqliteSaver"]
end
FE_SSE --> API_Start
FE_SSE --> API_Review
API_Start --> Graph_Build
API_Review --> Graph_Build
Graph_Build --> Nodes
Graph_Build --> State
Graph_Build --> Checkpoint
FE_Review --> FE_SSE
```

**图表来源**
- [main.py:35-103](file://workflow-studio/backend/app/main.py#L35-L103)
- [main.py:107-154](file://workflow-studio/backend/app/main.py#L107-L154)
- [graph.py:23-77](file://workflow-studio/backend/app/graph.py#L23-L77)
- [nodes.py:100-108](file://workflow-studio/backend/app/nodes.py#L100-L108)
- [state.py:5-30](file://workflow-studio/backend/app/state.py#L5-L30)
- [ReviewDialog.vue:1-54](file://workflow-studio/frontend/src/components/panels/ReviewDialog.vue#L1-L54)
- [useWorkflowSSE.ts:74-157](file://workflow-studio/frontend/src/composables/useWorkflowSSE.ts#L74-L157)

**章节来源**
- [main.py:35-103](file://workflow-studio/backend/app/main.py#L35-L103)
- [graph.py:23-77](file://workflow-studio/backend/app/graph.py#L23-L77)
- [nodes.py:100-108](file://workflow-studio/backend/app/nodes.py#L100-L108)
- [state.py:5-30](file://workflow-studio/backend/app/state.py#L5-L30)
- [ReviewDialog.vue:1-54](file://workflow-studio/frontend/src/components/panels/ReviewDialog.vue#L1-L54)
- [useWorkflowSSE.ts:74-157](file://workflow-studio/frontend/src/composables/useWorkflowSSE.ts#L74-L157)

## 核心组件
- 审核节点（review_node）：负责在生成草稿报告后暂停执行，设置审核状态为 pending，并通过消息提示等待人工审核
- 条件路由（route_after_review）：根据 review_status 决定下一步是输出最终报告还是进入修订循环
- 中断机制（interrupt_before）：LangGraph 编译时配置在 review 节点前暂停，等待外部注入审核结果
- 前端审核界面（ReviewDialog.vue）：提供通过/不通过按钮与反馈输入框，触发审核提交
- SSE 客户端（useWorkflowSSE.ts）：处理事件流，识别 interrupted 事件并展示审核对话框，提交审核后恢复执行
- 状态模型（ResearchState）：定义 review_status 等审核相关字段，支持 pending/approved/rejected 状态

**章节来源**
- [nodes.py:100-108](file://workflow-studio/backend/app/nodes.py#L100-L108)
- [graph.py:11-20](file://workflow-studio/backend/app/graph.py#L11-L20)
- [graph.py:65-77](file://workflow-studio/backend/app/graph.py#L65-L77)
- [state.py:22-24](file://workflow-studio/backend/app/state.py#L22-L24)
- [ReviewDialog.vue:1-54](file://workflow-studio/frontend/src/components/panels/ReviewDialog.vue#L1-L54)
- [useWorkflowSSE.ts:19-72](file://workflow-studio/frontend/src/composables/useWorkflowSSE.ts#L19-L72)

## 架构总览
审核节点的工作流整体流程如下：
1. 前端调用 /api/workflow/start 启动工作流
2. 后端构建图并在 compile 时设置 interrupt_before=["review"]
3. 工作流执行至 review 节点前被暂停，返回 interrupted 事件
4. 前端收到 interrupted 事件后显示审核对话框
5. 用户选择通过或不通过并提交审核
6. 后端通过 Command(update=update, resume=True) 恢复执行，更新 review_status 和 review_feedback
7. 条件路由根据 review_status 决定输出或修订

```mermaid
sequenceDiagram
participant FE as "前端"
participant API as "后端API"
participant LG as "LangGraph"
participant CK as "检查点"
FE->>API : POST /api/workflow/start
API->>LG : astream_events(initial_state)
LG-->>API : node_start/node_end/token/tool_result
API-->>FE : SSE 事件流
Note over LG : 到达 review 前中断
LG-->>API : state.next = ["review"]
API-->>FE : type=interrupted
FE->>FE : 显示审核对话框
FE->>API : POST /api/workflow/review {status, feedback}
API->>LG : Command(update=update, resume=True)
LG->>CK : 读取检查点状态
LG-->>API : 继续执行后续节点
API-->>FE : 继续事件流直至完成或再次中断
```

**图表来源**
- [main.py:35-103](file://workflow-studio/backend/app/main.py#L35-L103)
- [main.py:107-154](file://workflow-studio/backend/app/main.py#L107-L154)
- [graph.py:65-77](file://workflow-studio/backend/app/graph.py#L65-L77)

## 详细组件分析

### 审核节点（review_node）实现逻辑
- 职责：在草稿报告生成后暂停执行，设置当前步骤为 review，并将审核状态置为 pending
- 行为：返回包含 current_step、review_status、messages 的状态更新，供后续路由判断
- 关键点：本身不执行业务逻辑，仅作为中断标记点

```mermaid
flowchart TD
Start(["进入 review_node"]) --> SetStep["设置 current_step='review'"]
SetStep --> SetStatus["设置 review_status='pending'"]
SetStatus --> AddMsg["添加等待审核消息"]
AddMsg --> Return["返回状态更新"]
```

**图表来源**
- [nodes.py:100-108](file://workflow-studio/backend/app/nodes.py#L100-L108)

**章节来源**
- [nodes.py:100-108](file://workflow-studio/backend/app/nodes.py#L100-L108)

### LangGraph 中断机制（interrupt_before）
- 配置位置：在编译图时通过 interrupt_before=["review"] 指定在 review 节点前暂停
- 效果：工作流执行到 review 节点前会停止，state.next 指向待执行节点
- 恢复方式：通过 Command(update=update, resume=True) 注入审核结果并恢复执行
- 持久化：使用 AsyncSqliteSaver 保存检查点，支持页面刷新后恢复

```mermaid
classDiagram
class GraphBuilder {
+build_research_graph()
+get_compiled_graph()
}
class CompiledGraph {
+astream_events()
+aget_state()
}
class Checkpointer {
+save_checkpoint()
+load_checkpoint()
}
GraphBuilder --> CompiledGraph : "compile()"
CompiledGraph --> Checkpointer : "使用"
```

**图表来源**
- [graph.py:23-77](file://workflow-studio/backend/app/graph.py#L23-L77)

**章节来源**
- [graph.py:65-77](file://workflow-studio/backend/app/graph.py#L65-L77)
- [main.py:65-77](file://workflow-studio/backend/app/main.py#L65-L77)

### 审核状态管理（review_status）
- 初始状态：空字符串或 pending
- 转换规则：
  - pending → approved：用户点击“通过”，状态变为 approved，路由到 output 节点
  - pending → rejected：用户点击“不通过”并提供反馈，状态变为 rejected，路由到 revision 节点
  - rejected → pending：修订后重新搜索和分析，再次进入 review 节点
- 防循环：iteration_count 限制最多3轮修订，超过则强制输出

```mermaid
stateDiagram-v2
[*] --> Pending : "初始状态"
Pending --> Approved : "用户批准"
Pending --> Rejected : "用户拒绝"
Rejected --> Pending : "修订后重新审核"
Approved --> Output : "输出最终报告"
Rejected --> Revision : "进入修订循环"
Revision --> Pending : "重新审核"
```

**图表来源**
- [state.py:22-24](file://workflow-studio/backend/app/state.py#L22-L24)
- [graph.py:11-20](file://workflow-studio/backend/app/graph.py#L11-L20)

**章节来源**
- [state.py:22-24](file://workflow-studio/backend/app/state.py#L22-L24)
- [graph.py:11-20](file://workflow-studio/backend/app/graph.py#L11-L20)

### 前端审核界面集成
- ReviewDialog.vue：提供审核输入框和通过/不通过按钮
- useWorkflowSSE.ts：处理 interrupted 事件，显示审核对话框，调用 submitReview 方法
- workflow.ts：定义 NodeStatus、SSEEvent 等类型，确保类型安全

```mermaid
sequenceDiagram
participant UI as "ReviewDialog"
participant SSE as "useWorkflowSSE"
participant API as "/api/workflow/review"
UI->>SSE : handleApprove()/handleReject()
SSE->>SSE : setNodeStatus('review', 'waiting')
SSE->>API : POST {workflow_id, status, feedback}
API-->>SSE : SSE 事件流
SSE->>UI : 更新状态和日志
```

**图表来源**
- [ReviewDialog.vue:1-54](file://workflow-studio/frontend/src/components/panels/ReviewDialog.vue#L1-L54)
- [useWorkflowSSE.ts:116-157](file://workflow-studio/frontend/src/composables/useWorkflowSSE.ts#L116-L157)

**章节来源**
- [ReviewDialog.vue:1-54](file://workflow-studio/frontend/src/components/panels/ReviewDialog.vue#L1-L54)
- [useWorkflowSSE.ts:19-72](file://workflow-studio/frontend/src/composables/useWorkflowSSE.ts#L19-L72)
- [workflow.ts:22-32](file://workflow-studio/frontend/src/types/workflow.ts#L22-L32)

### 用户决策提交流程
1. 用户在前端选择“通过”或“不通过”
2. 如果是“不通过”，必须填写反馈内容
3. 前端调用 /api/workflow/review 提交审核结果
4. 后端使用 Command(update=update, resume=True) 恢复执行
5. 工作流根据新状态继续执行或再次中断

```mermaid
flowchart TD
UserAction["用户操作"] --> Validate{"是否拒绝？"}
Validate --> |否| SubmitApproved["提交 approved"]
Validate --> |是| InputFeedback["输入反馈"]
InputFeedback --> SubmitRejected["提交 rejected + feedback"]
SubmitApproved --> BackendUpdate["后端更新状态"]
SubmitRejected --> BackendUpdate
BackendUpdate --> ResumeFlow["恢复工作流执行"]
```

**图表来源**
- [ReviewDialog.vue:42-52](file://workflow-studio/frontend/src/components/panels/ReviewDialog.vue#L42-L52)
- [main.py:107-154](file://workflow-studio/backend/app/main.py#L107-L154)

**章节来源**
- [ReviewDialog.vue:42-52](file://workflow-studio/frontend/src/components/panels/ReviewDialog.vue#L42-L52)
- [main.py:107-154](file://workflow-studio/backend/app/main.py#L107-L154)

### 审核结果持久化存储
- 检查点机制：使用 AsyncSqliteSaver 保存工作流状态，包括 review_status 和 review_feedback
- 恢复能力：页面刷新后可通过 /api/workflow/state/{workflow_id} 获取当前状态
- 线程隔离：每个工作流有独立的 thread_id，确保状态隔离

```mermaid
graph LR
State["工作流状态"] --> Checkpoint["检查点存储"]
Checkpoint --> SQLite["SQLite 数据库"]
Restore["状态恢复"] --> Checkpoint
```

**图表来源**
- [graph.py:69-77](file://workflow-studio/backend/app/graph.py#L69-L77)
- [main.py:157-173](file://workflow-studio/backend/app/main.py#L157-L173)

**章节来源**
- [graph.py:69-77](file://workflow-studio/backend/app/graph.py#L69-L77)
- [main.py:157-173](file://workflow-studio/backend/app/main.py#L157-L173)

## 依赖关系分析
- nodes.py 依赖 state.py 中的 ResearchState 类型定义
- graph.py 依赖 nodes.py 中的各个节点函数
- main.py 依赖 graph.py 中的图构建和编译
- 前端依赖后端提供的 SSE 接口和类型定义

```mermaid
graph TD
nodes_py["nodes.py"] --> state_py["state.py"]
graph_py["graph.py"] --> nodes_py
main_py["main.py"] --> graph_py
frontend_vue["ReviewDialog.vue"] --> sse_ts["useWorkflowSSE.ts"]
sse_ts --> types_ts["workflow.ts"]
```

**图表来源**
- [nodes.py:1-8](file://workflow-studio/backend/app/nodes.py#L1-L8)
- [graph.py:1-8](file://workflow-studio/backend/app/graph.py#L1-L8)
- [main.py:1-12](file://workflow-studio/backend/app/main.py#L1-L12)
- [ReviewDialog.vue:32-38](file://workflow-studio/frontend/src/components/panels/ReviewDialog.vue#L32-L38)
- [useWorkflowSSE.ts:1-3](file://workflow-studio/frontend/src/composables/useWorkflowSSE.ts#L1-L3)
- [workflow.ts:1-32](file://workflow-studio/frontend/src/types/workflow.ts#L1-L32)

**章节来源**
- [nodes.py:1-8](file://workflow-studio/backend/app/nodes.py#L1-L8)
- [graph.py:1-8](file://workflow-studio/backend/app/graph.py#L1-L8)
- [main.py:1-12](file://workflow-studio/backend/app/main.py#L1-L12)

## 性能考虑
- 检查点存储：SQLite 适用于开发环境，生产环境建议迁移到 PostgreSQL 以提高并发性能
- 中断频率：频繁的中断会增加状态同步开销，应合理设计审核节点位置
- 流式传输：SSE 事件流适合实时交互，但需注意网络稳定性和错误重连机制
- 内存占用：大量工作流实例同时运行时，需监控内存使用情况

## 故障排查指南
- 工作流未中断：检查 interrupt_before 配置是否正确，确认 review 节点已添加到图中
- 审核提交失败：验证 workflow_id 是否正确，检查网络连接和后端服务状态
- 状态不同步：确认检查点存储正常，尝试重启服务清理临时文件
- 前端无响应：检查 SSE 连接是否建立，查看浏览器控制台错误信息

**章节来源**
- [graph.py:65-77](file://workflow-studio/backend/app/graph.py#L65-L77)
- [main.py:107-154](file://workflow-studio/backend/app/main.py#L107-L154)
- [useWorkflowSSE.ts:74-157](file://workflow-studio/frontend/src/composables/useWorkflowSSE.ts#L74-L157)

## 结论
审核节点通过 LangGraph 的 interrupt_before 机制实现了高效的人机协作流程。review_status 字段的状态管理确保了审核流程的可控性和可追溯性。前端审核界面提供了直观的用户交互体验，SSE 事件流保证了实时状态同步。检查点机制支持工作流的持久化和恢复，为复杂业务流程提供了可靠的基础设施。

## 附录

### 自定义配置指南
- 修改中断位置：在 graph.py 中调整 interrupt_before 参数
- 自定义审核规则：在 route_after_review 中添加新的条件分支
- 扩展审核字段：在 state.py 中添加新的审核相关字段

### 批量审核功能扩展
- 批量提交：在前端增加多选功能，支持多个工作流同时审核
- 模板审核：预定义审核模板，提高审核效率
- 审核历史：记录每次审核的操作历史和结果变更

**章节来源**
- [graph.py:65-77](file://workflow-studio/backend/app/graph.py#L65-L77)
- [graph.py:11-20](file://workflow-studio/backend/app/graph.py#L11-L20)
- [state.py:22-24](file://workflow-studio/backend/app/state.py#L22-L24)