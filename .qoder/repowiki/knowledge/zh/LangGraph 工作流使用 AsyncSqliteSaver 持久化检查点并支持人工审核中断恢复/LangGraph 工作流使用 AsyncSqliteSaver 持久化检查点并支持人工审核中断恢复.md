---
kind: design
name: LangGraph 工作流使用 AsyncSqliteSaver 持久化检查点并支持人工审核中断恢复
source: session
category: adr
---

# LangGraph 工作流使用 AsyncSqliteSaver 持久化检查点并支持人工审核中断恢复

_来源：fff0a99 → acb081d 提交周期内记录的编码计划——内容为规划时意图，实现可能滞后或有出入。_

**状态：** accepted

## 背景
研究助手工作流包含条件分支、循环和人工审核环节，需要在 review 节点暂停后能恢复执行，且不能丢失中间状态。

## 决策驱动
- 检查点持久化避免进程重启丢失状态
- interrupt_before 机制支持人机协作审核
- SQLite 轻量无需额外数据库服务

## 备选方案
- **MemorySaver（内存检查点）** _（已否决）_ — 优点：零配置，开发调试简单；缺点：进程重启后状态全部丢失，无法恢复中断的工作流
- **AsyncSqliteSaver（文件持久化检查点）** — 优点：检查点落盘可恢复，支持 interrupt_before=['review'] 后传 Command(update=..., resume=True) 继续执行；缺点：引入文件系统依赖，并发写入需注意锁

## 决策
在 graph.py 中使用 StateGraph 定义 7 个节点（plan/search/analyze/write/review/output/revision），通过 interrupt_before=['review'] 在审核节点暂停，恢复时必须携带 Command(update=..., resume=True)；使用 AsyncSqliteSaver 保存 ResearchState 以支持断点续跑。

## 影响
工作流可在审核通过后继续执行 revision→write 循环（iteration_count >= 3 强制跳出），也可在任意检查点恢复；生产环境需考虑 SQLite 文件备份与迁移策略。