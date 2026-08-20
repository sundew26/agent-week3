---
kind: external_dependency
name: LangGraph 多 Agent 工作流框架
slug: langgraph
category: external_dependency
category_hints:
    - framework_behavior
scope:
    - '**'
---

有状态多 Agent 工作流引擎，用于定义规划→搜索→分析→写作→审核→输出的条件分支流程，并通过 AsyncSqliteSaver 做检查点持久化，支持刷新页面恢复执行进度。节点实现位于 `backend/app/nodes.py`，图定义在 `graph.py`。