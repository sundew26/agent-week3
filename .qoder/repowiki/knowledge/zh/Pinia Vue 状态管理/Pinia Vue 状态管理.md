---
kind: external_dependency
name: Pinia Vue 状态管理
slug: pinia
category: external_dependency
category_hints:
    - framework_behavior
scope:
    - '**'
---

Vue 3 官方推荐的状态管理库，项目中使用 Pinia store（`stores/workflow.ts`）集中管理工作流节点、边、执行状态等全局数据，配合 composable `useWorkflowSSE` 处理 SSE 事件。