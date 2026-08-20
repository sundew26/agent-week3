---
kind: external_dependency
name: Vue Flow 流程图可视化库
slug: vue-flow
category: external_dependency
category_hints:
    - sdk_real_api
scope:
    - '**'
---

前端流程图渲染核心，配合 `@vue-flow/background`、`@vue-flow/controls`、`@vue-flow/minimap` 子包使用。通过 `v-model:nodes` / `v-model:edges` 双向绑定节点与边，自定义节点组件放在 `components/nodes/`，自定义边放在 `components/edges/`。