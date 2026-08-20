---
kind: frontend_style
name: 基于 Tailwind CSS 的原子化样式体系与 Vue Flow 主题定制
category: frontend_style
scope:
    - '**'
source_files:
    - workflow-studio/frontend/tailwind.config.js
    - workflow-studio/frontend/postcss.config.js
    - workflow-studio/frontend/src/styles/main.css
    - workflow-studio/frontend/package.json
    - workflow-studio/frontend/src/components/nodes/BaseNode.vue
    - workflow-studio/frontend/src/components/WorkflowCanvas.vue
    - workflow-studio/frontend/src/components/panels/ChatInput.vue
---

## 1. 系统与方法论

前端采用 **Tailwind CSS v3** 作为核心样式框架，配合 **PostCSS + Autoprefixer** 构建管线（`postcss.config.js`），通过 `@tailwind base/components/utilities` 指令在 `src/styles/main.css` 中引入基础层、组件层和工具层。项目未使用任何 UI 组件库（如 Element Plus / Ant Design），所有视觉样式均通过 Tailwind 原子类组合实现，属于典型的 **原子化 CSS 风格**。

图标统一来自 `@lucide/vue`（如 `Loader2`、`CheckCircle`、`Send` 等），并通过 `clsx` + `tailwind-merge` 进行条件类名拼接，避免冲突。

## 2. 关键文件

- `frontend/tailwind.config.js`：仅配置扫描路径（`./src/**/*.{vue,js,ts,jsx,tsx}`）并保留空的 `theme.extend`，未自定义颜色/字体/间距等设计令牌。
- `frontend/src/styles/main.css`：全局样式入口，重置默认 margin/padding/box-sizing，设置系统字体栈，并覆盖 Vue Flow 的节点光标、边线宽度及动画效果。
- `frontend/postcss.config.js`：启用 `tailwindcss` 与 `autoprefixer` 插件。
- `frontend/package.json`：声明依赖 `tailwindcss ^3.4`、`@vue-flow/core` 及其扩展（background、controls、minimap）、`@lucide/vue`、`clsx`、`tailwind-merge`。
- `frontend/src/components/nodes/BaseNode.vue`：状态驱动样式的典型实现——用 `statusConfig` 映射 `idle/running/completed/error/waiting` 到 Tailwind 类。
- `frontend/src/components/WorkflowCanvas.vue`：导入 `@vue-flow/core/dist/style.css` 与 `theme-default.css`，并在模板中使用 Tailwind 类布局画布与侧栏。

## 3. 架构与约定

- **无全局主题变量**：`tailwind.config.js` 的 `theme.extend` 为空，项目中不存在自定义色板、字号阶梯或断点；所有颜色直接使用 Tailwind 内置语义色（如 `bg-blue-50`、`text-red-700`、`border-gray-300`）。
- **状态即样式**：节点状态（`NodeStatus`）集中定义在 `BaseNode.vue` 的 `statusConfig` 对象中，每个状态对应一组边框、背景、文字色和动画类，通过 `computed` + `clsx` 动态组装到根容器上。
- **Vue Flow 集成**：通过 `import '@vue-flow/core/dist/theme-default.css'` 加载默认主题，再在 `main.css` 中以 `.vue-flow__node`、`.vue-flow__edge-path`、`.vue-flow__edge.animated` 等选择器做局部覆盖（如加粗边线、添加虚线流动动画 `dashdraw` keyframes）。
- **布局策略**：主界面采用 Flexbox 双栏布局（左侧画布 `flex-1`，右侧面板固定 `w-96` 带左边框），响应式行为完全依赖 Tailwind 的响应式前缀（当前未见显式断点）。整体为桌面端优先的单页应用。
- **组件级样式组织**：没有 SCSS/Less 预处理，也没有按模块划分的 CSS 文件；全局样式集中在 `src/styles/main.css`，组件内样式以 `<style>` 块或直接通过 class 字符串注入。

## 4. 约定与约束

- 所有可见样式必须通过 Tailwind 原子类编写，禁止新增全局 CSS 规则（除 `main.css` 中的 reset 与 Vue Flow 覆盖）。
- 组件内部不维护独立样式文件，样式直接写在模板的 `class` 属性或通过 `clsx` 计算生成。
- 第三方库（Vue Flow、Lucide）的样式通过 npm 包直接引入，不在仓库中二次维护。
- 未定义设计令牌（design tokens）：颜色、圆角、阴影等全部沿用 Tailwind 默认值，因此跨组件的一致性依赖于对同一组语义类的复用（如 `rounded-xl`、`shadow-sm`、`border-2`）。
- 动画通过 Tailwind 内置 `animate-spin`、`animate-pulse` 以及 `main.css` 中自定义 `@keyframes dashdraw` 实现，遵循“少量自定义动画 + 大量原子类”的组合方式。