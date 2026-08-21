---
kind: design
name: 前后端通过 FastAPI SSE 实时推送工作流执行事件
source: session
category: adr
---

# 前后端通过 FastAPI SSE 实时推送工作流执行事件

_来源：fff0a99 → acb081d 提交周期内记录的编码计划——内容为规划时意图，实现可能滞后或有出入。_

**状态：** accepted

## 背景
可视化工作流编辑器需要在前端画布上实时反映后端 LangGraph 各节点的执行进度（运行中、完成、失败），传统 HTTP 请求无法满足增量更新需求。

## 决策驱动
- 实时性：节点逐个亮起反馈执行进度
- 单向推送：后端主动推送事件到多个前端连接
- 兼容性：浏览器原生 EventSource 即可消费

## 备选方案
- **WebSocket 双向通信** _（已否决）_ — 优点：全双工，适合复杂交互；缺点：需要额外的连接管理和重连逻辑，Vite 代理需特殊配置
- **轮询（polling）** _（已否决）_ — 优点：实现简单；缺点：延迟高、浪费带宽，无法做到节点级实时反馈
- **Server-Sent Events (SSE)** — 优点：单向推送，media_type='text/event-stream' 配合 sse-starlette 实现，浏览器原生支持，Vite 代理设置 changeOrigin: true 即可转发；缺点：仅服务端→客户端单向，审核提交走独立 POST 接口

## 决策
后端使用 sse-starlette 暴露 SSE 端点，禁用缓冲并以 text/event-stream 格式推送 astream_events v2 事件；前端通过 useWorkflowSSE composable 消费事件并更新 Pinia store；Vite 代理 /api → localhost:8000 时启用 changeOrigin: true。

## 影响
前端可实时渲染节点状态变化和时间线；审核结果通过独立的 ReviewRequest POST 接口提交，与 SSE 流解耦；需确保代理层不缓冲 SSE 响应体。