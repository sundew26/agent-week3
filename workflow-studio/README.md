# Workflow Studio — AI 研究助手可视化工作流

基于 **LangGraph + Vue 3 + Vue Flow** 构建的可视化多 Agent 研究工作流系统。

## ✨ 功能特性

- 🔄 **可视化工作流**：Vue Flow 实时渲染执行状态，节点逐个亮起
- 🧠 **多 Agent 协作**：规划 → 搜索 → 分析 → 写作 → 审核 → 输出
- 🔀 **条件分支**：审核通过 → 输出；不通过 → 回到搜索（循环）
- 👤 **人工审核**：Human-in-the-loop，在关键节点暂停等待人工判断
- 💾 **检查点恢复**：SQLite 持久化，刷新页面不丢失进度
- 📡 **SSE 实时推送**：流式传输执行状态和 LLM 输出
- 🛡️ **防无限循环**：最多 3 轮修订后强制输出

## 🏗️ 架构

```
用户提问 → [规划] → [搜索] → [分析] → [写作] → [审核] → 条件分支
                                                          ├─ 通过 → [输出] → 最终报告
                                                          └─ 不通过 → [修订] → [搜索]（循环）
```

## 🚀 快速开始

### 后端

```bash
cd workflow-studio/backend
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 填入 OPENAI_API_KEY
uvicorn app.main:app --reload --port 1994
```

访问 http://localhost:1994/docs 查看 API 文档

### 前端

```bash
cd workflow-studio/frontend
npm install
npm run dev
```

访问 http://localhost:1993

## 🛠️ 技术栈

### 后端
- **FastAPI**：高性能异步 Web 框架
- **LangGraph**：有状态多 Agent 工作流框架
- **LangChain**：LLM 应用开发工具链
- **AsyncSqliteSaver**：检查点持久化

### 前端
- **Vue 3**：渐进式 JavaScript 框架
- **Vue Flow**：流程图可视化库
- **Pinia**：Vue 状态管理
- **Tailwind CSS**：原子化 CSS 框架
- **TypeScript**：类型安全

## 📁 项目结构

```
workflow-studio/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI 入口 + SSE
│   │   ├── graph.py         # LangGraph 工作流定义
│   │   ├── nodes.py         # 各节点实现
│   │   ├── state.py         # 状态定义
│   │   ├── tools.py         # 搜索工具
│   │   ├── config.py        # 配置
│   │   └── schemas.py       # API 数据模型
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── WorkflowCanvas.vue  # Vue Flow 画布
│   │   │   ├── nodes/BaseNode.vue  # 通用节点
│   │   │   ├── panels/             # 面板组件
│   │   │   └── layout/             # 布局组件
│   │   ├── composables/
│   │   │   └── useWorkflowSSE.ts   # SSE 状态管理
│   │   ├── stores/workflow.ts      # Pinia store
│   │   └── types/workflow.ts       # 类型定义
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## 📋 验收标准

- [x] 输入研究问题 → 工作流自动执行 → 节点逐个亮起
- [x] 执行到审核节点 → 暂停 → 弹出审核弹窗
- [x] 点击"不通过" → 回到搜索节点重新执行（循环）
- [x] 点击"通过" → 输出最终报告
- [x] 刷新页面 → 从检查点恢复状态
- [x] 超过3轮修订 → 强制输出（防止无限循环）

## 🔮 未来规划

- 拖拽编辑工作流：让用户在 Vue Flow 中拖拽节点、连线，动态生成 LangGraph 图
- 并行节点：搜索节点拆分为多个并行子搜索
- 多工作流模板：除研究助手外，增加"代码审查"、"内容创作"等模板
- 执行回放：从检查点加载历史执行，在 Vue Flow 中回放
- 性能面板：展示每个节点的 Token 消耗、耗时
