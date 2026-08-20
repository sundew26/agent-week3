---
kind: build_system
name: 前后端分离的本地开发构建流程（无 CI/容器化）
category: build_system
scope:
    - '**'
source_files:
    - workflow-studio/README.md
    - workflow-studio/backend/requirements.txt
    - workflow-studio/frontend/package.json
    - workflow-studio/frontend/vite.config.ts
---

## 1. 使用的系统与方法

本项目采用**前后端分离 + 本地脚本驱动**的轻量构建方式，没有 Makefile、Dockerfile、CI 流水线或发布脚本。构建与运行完全通过各自生态的原生命令完成：
- **后端（Python/FastAPI）**：使用 `pip` + `requirements.txt` 管理依赖，通过 `uvicorn` 直接启动。
- **前端（Vue 3 + Vite）**：使用 `npm` + `package.json` 管理依赖，通过 `vite` 提供开发服务器并执行 TypeScript 类型检查后打包。

## 2. 关键文件

- `workflow-studio/backend/requirements.txt` — 后端 Python 依赖清单（langgraph、fastapi、uvicorn、sse-starlette、httpx、python-dotenv 等）。
- `workflow-studio/frontend/package.json` — 前端依赖与脚本入口，定义 `dev` / `build` / `preview` 三个 npm scripts。
- `workflow-studio/frontend/vite.config.ts` — Vite 构建配置，包含 `@` 路径别名、开发端口 `1993`、以及将 `/api` 请求代理到后端 `http://localhost:1994` 的跨域代理规则。
- `workflow-studio/README.md` — 唯一的项目级构建说明，描述了后端与前端各自的启动步骤。

## 3. 架构与约定

- **双进程本地开发**：后端固定监听 `1994` 端口（FastAPI + SSE），前端开发服务器固定监听 `1993` 端口并通过 Vite proxy 转发 `/api` 请求到后端，形成“前端 dev server → 后端 API”的本地联调模式。
- **环境变量隔离**：后端通过 `python-dotenv` 加载 `.env`（模板见 `backend/.env.example`），前端通过 `frontend/.env.example` 提供前端环境变量模板；两者均要求开发者手动复制为 `.env` 后再运行。
- **构建产物位置**：前端 `npm run build` 输出至 `frontend/dist/`（已在目录树中出现），后端无编译步骤，直接以源码形式由 uvicorn 加载 `app.main:app`。
- **版本策略**：`package.json` 中声明 `version: "1.0.0"`，但仓库中未见任何版本号递增、tag 或 release 脚本，当前处于单版本原型阶段。

## 4. 约定与约束

- **依赖锁定**：后端依赖通过 `requirements.txt` 中的 `>=` 宽松版本声明（如 `langgraph>=0.2.60`），未使用 `pip freeze` 或 `requirements.lock` 进行精确锁定；前端通过 `package-lock.json` 锁定 npm 依赖。
- **开发命令约定**：所有启动命令集中在 README 中，项目内无 `Makefile`、`docker-compose.yml`、`.github/workflows`、`Dockerfile` 或 `build.sh` 等自动化脚本——开发者需按 README 手动先后启动后端与前端。
- **端口约定**：后端固定 `1994`，前端开发服务器固定 `1993`，Vite 配置中硬编码了该代理目标，修改后端端口需要同步更新两处。
- **TypeScript 校验前置构建**：前端 `build` 脚本为 `vue-tsc && vite build`，即先执行类型检查再打包，类型错误会阻止构建产物生成。
- **无 CI/CD**：经搜索未发现 GitHub Actions、Jenkins、Docker 或其他持续集成/部署配置，该项目目前仅支持本地手动构建与运行。