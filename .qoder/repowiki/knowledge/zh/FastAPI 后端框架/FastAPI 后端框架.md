---
kind: external_dependency
name: FastAPI 后端框架
slug: fastapi
category: external_dependency
category_hints:
    - framework_behavior
scope:
    - '**'
---

后端 Web 框架，通过 uvicorn 启动（`uvicorn app.main:app --reload --port 1994`），提供 REST API 与 SSE 实时推送。默认端口在 README 中记为 1994，但对话中曾改为 8000/1993，部署时需以实际启动参数为准。