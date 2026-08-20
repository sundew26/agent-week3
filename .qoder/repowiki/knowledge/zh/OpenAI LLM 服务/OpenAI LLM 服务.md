---
kind: external_dependency
name: OpenAI LLM 服务
slug: openai
category: external_dependency
category_hints:
    - auth_protocol
    - client_constraint
scope:
    - '**'
---

通过 `langchain-openai` 调用 OpenAI ChatGPT（默认模型 `gpt-4o-mini`）。密钥与环境变量：`OPENAI_API_KEY`、`OPENAI_BASE_URL`（可替换为兼容端点）、`LLM_MODEL`。当前搜索工具使用 mock 数据，不依赖真实 OpenAI 即可运行；启用真实 LLM 需配置上述环境变量。