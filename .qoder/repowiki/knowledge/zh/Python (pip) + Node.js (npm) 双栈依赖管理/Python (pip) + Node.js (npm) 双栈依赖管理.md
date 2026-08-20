---
kind: dependency_management
name: Python (pip) + Node.js (npm) 双栈依赖管理
category: dependency_management
scope:
    - '**'
source_files:
    - workflow-studio/backend/requirements.txt
    - workflow-studio/frontend/package.json
    - workflow-studio/frontend/package-lock.json
    - workflow-studio/README.md
---

## 1. 使用的系统/工具

本项目为前后端分离的 Python + Vue 工程，采用两套独立的包管理器：
- **后端（Python）**：使用 `pip` + `requirements.txt` 声明依赖，通过本地 `venv/` 虚拟环境隔离运行。
- **前端（Node.js）**：使用 `npm` + `package.json` 声明依赖，并通过 `package-lock.json`（lockfileVersion: 1）锁定精确版本。

## 2. 关键文件

- `workflow-studio/backend/requirements.txt`：后端全部运行时依赖清单。
- `workflow-studio/frontend/package.json`：前端运行时与开发时依赖清单。
- `workflow-studio/frontend/package-lock.json`：前端依赖树与精确版本的锁定文件。
- `workflow-studio/backend/.env.example` / `frontend/.env.example`：环境变量模板（非依赖文件，但配合依赖读取配置）。
- `README.md`：安装说明中明确 `pip install -r requirements.txt` 与 `npm install` 流程。

## 3. 架构与约定

### 后端（Python）
- 依赖以“宽松下限”形式声明，例如 `langgraph>=0.2.60`、`fastapi>=0.115.0`、`uvicorn[standard]>=0.0.30` 等，仅规定最低兼容版本，不锁定上限。
- 未使用 `poetry`、`Pipfile`、`pyproject.toml`、`pip freeze > requirements.txt` 生成的锁文件；每次安装由 pip 自行解析并缓存到本地 pip cache。
- 运行依赖通过 `venv/` 虚拟环境隔离，不在仓库中提交 `venv/` 内容（目录存在但为空占位）。
- 核心依赖集中在 LangGraph 生态（`langgraph`、`langchain-core`、`langchain-openai`、`langgraph-checkpoint-sqlite`），Web 层使用 FastAPI + Uvicorn，SSE 使用 `sse-starlette`，HTTP 客户端使用 `httpx`，配置加载使用 `python-dotenv`。

### 前端（Node.js）
- 依赖分为 `dependencies`（运行时：Vue 3、@vue-flow/*、Pinia、Lucide、Tailwind 相关）和 `devDependencies`（构建期：Vite、TypeScript、vue-tsc、Tailwind CSS、PostCSS、Autoprefixer）。
- 所有依赖版本号均使用 `^` 前缀（如 `vue: ^3.5.0`、`vite: ^5.4.0`），允许 npm 在语义化版本范围内自动升级。
- `package-lock.json` 记录了完整依赖树及每个包的精确版本与 sha512 integrity hash，来源镜像指向 `https://registry.npmmirror.com`（淘宝 npm 镜像），表明构建/安装时使用了国内镜像源。
- 无 `node_modules/` 提交（仅存在于本地），符合 npm 标准工作流。

## 4. 约定与约束

- **后端**：依赖版本策略为“只设下限（`>=X.Y.Z`）”，便于跟随上游库演进，但不保证跨环境可重复构建——缺少 `requirements.lock`/`Pipfile.lock` 类锁文件。
- **前端**：依赖版本策略为“语义化范围（`^X.Y.Z`）+ lockfile”，通过 `package-lock.json` 保证多环境一致安装。
- **虚拟环境**：Python 依赖通过 `venv/` 隔离，不纳入版本控制；Node 依赖通过 `node_modules/` 隔离，同样不纳入版本控制。
- **镜像源**：前端 `package-lock.json` 中 `resolved` 字段显示使用 `registry.npmmirror.com`，说明项目已适配国内 npm 镜像。
- **安装入口**：`README.md` 明确后端使用 `pip install -r requirements.txt`，前端使用 `npm install`（脚本见 `package.json` 中的 `dev/build/preview`）。