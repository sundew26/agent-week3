---
kind: design
name: 前端采用 Vue 3 + Vue Flow 替代原 React 方案
source: session
category: adr
---

# 前端采用 Vue 3 + Vue Flow 替代原 React 方案

_来源：fff0a99 → acb081d 提交周期内记录的编码计划——内容为规划时意图，实现可能滞后或有出入。_

**状态：** accepted

## 背景
原始 spec 指定使用 React（@xyflow/react、zustand、Next.js App Router）构建可视化工作流编辑器，但用户明确要求改为 Vue。项目需从零搭建前后端完整实现。

## 决策驱动
- 用户技术栈偏好
- Vue Flow 生态与 @vue-flow/* 组件库匹配度
- Pinia 作为 Vue 官方状态管理方案

## 备选方案
- **React + @xyflow/react + zustand** _（已否决）_ — 优点：原 spec 设计基于此栈，生态成熟；缺点：与用户要求冲突，需整体重写
- **Vue 3 + @vue-flow/core + Pinia + Vite** — 优点：满足用户需求，Vue Flow 提供画布/背景/控件/小地图等配套，Pinia 与 Vue 3 深度集成；缺点：需要重新映射所有组件和状态逻辑

## 决策
采用 Vue 3 + @vue-flow/core（含 background/controls/minimap）+ Pinia + Vite 单页应用，将 react hooks 替换为 Vue composables，lucide-react 替换为 lucide-vue-next。

## 影响
前端代码完全基于 Vue 生态，后续新增节点类型或交互需遵循 Vue 组件模式；与后端通过 /api 代理通信，SSE 事件由 useWorkflowSSE composable 统一消费。