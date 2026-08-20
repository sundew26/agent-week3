---
kind: external_dependency
name: SQLite 检查点持久化
slug: sqlite-checkpoint
category: external_dependency
category_hints:
    - framework_behavior
scope:
    - '**'
---

通过 `langgraph-checkpoint-sqlite` 的 `AsyncSqliteSaver` 将 LangGraph 工作流执行状态持久化到 SQLite，实现刷新页面后从检查点恢复执行进度。