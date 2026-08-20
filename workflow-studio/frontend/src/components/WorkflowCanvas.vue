<template>
  <div class="flex h-screen">
    <!-- 左侧：Vue Flow 画布 -->
    <div class="flex-1">
      <VueFlow
        v-model:nodes="nodes"
        v-model:edges="edges"
        :node-types="nodeTypes"
        :default-edge-options="defaultEdgeOptions"
        fit-view
        class="bg-gray-50"
        @node-click="onNodeClick"
      >
        <Background :gap="20" />
        <Controls />
        <MiniMap />
      </VueFlow>
    </div>

    <!-- 右侧：控制面板 -->
    <div class="w-96 border-l bg-white p-4 overflow-y-auto flex flex-col gap-4">
      <SidePanel
        :is-running="isRunning"
        :is-interrupted="isInterrupted"
        :streaming-text="streamingText"
        :logs="logs"
        :selected-node="selectedNodeId"
        :start-workflow="startWorkflow"
        :submit-review="submitReview"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, markRaw } from 'vue'
import { VueFlow } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import { MiniMap } from '@vue-flow/minimap'
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'

import BaseNode from './nodes/BaseNode.vue'
import SidePanel from './layout/SidePanel.vue'
import { useWorkflowSSE } from '@/composables/useWorkflowSSE'
import type { WorkflowNode, NodeStatus } from '@/types/workflow'
import type { Edge, NodeMouseEvent } from '@vue-flow/core'

// 注册自定义节点类型
const nodeTypes = {
  custom: markRaw(BaseNode),
}

// 初始节点布局
const initialNodes: WorkflowNode[] = [
  { id: 'plan', type: 'custom', position: { x: 250, y: 0 }, data: { label: '📋 规划', status: 'idle', nodeType: 'plan' } },
  { id: 'search', type: 'custom', position: { x: 250, y: 120 }, data: { label: '🔍 搜索', status: 'idle', nodeType: 'search' } },
  { id: 'analyze', type: 'custom', position: { x: 250, y: 240 }, data: { label: '📊 分析', status: 'idle', nodeType: 'analyze' } },
  { id: 'write', type: 'custom', position: { x: 250, y: 360 }, data: { label: '✍️ 写作', status: 'idle', nodeType: 'write' } },
  { id: 'review', type: 'custom', position: { x: 250, y: 480 }, data: { label: '👤 审核', status: 'idle', nodeType: 'review' } },
  { id: 'revision', type: 'custom', position: { x: 500, y: 300 }, data: { label: '🔄 修订', status: 'idle', nodeType: 'revision' } },
  { id: 'output', type: 'custom', position: { x: 250, y: 600 }, data: { label: '✅ 输出', status: 'idle', nodeType: 'output' } },
]

const initialEdges: Edge[] = [
  { id: 'e1', source: 'plan', target: 'search', animated: false },
  { id: 'e2', source: 'search', target: 'analyze', animated: false },
  { id: 'e3', source: 'analyze', target: 'write', animated: false },
  { id: 'e4', source: 'write', target: 'review', animated: false },
  { id: 'e5', source: 'review', target: 'output', label: '通过', type: 'default' },
  { id: 'e6', source: 'review', target: 'revision', label: '不通过', style: { stroke: '#f59e0b' } },
  { id: 'e7', source: 'revision', target: 'search', style: { stroke: '#f59e0b', strokeDasharray: '5 5' } },
]

const defaultEdgeOptions = {
  type: 'default',
  animated: false,
}

const nodes = ref<WorkflowNode[]>([...initialNodes])
const edges = ref<Edge[]>([...initialEdges])
const selectedNodeId = ref<string | null>(null)

const {
  nodeStatuses,
  isRunning,
  isInterrupted,
  streamingText,
  logs,
  startWorkflow,
  submitReview,
} = useWorkflowSSE()

// 根据 SSE 状态更新节点样式
watch(
  () => nodeStatuses.value,
  (newStatuses: Record<string, NodeStatus>) => {
    nodes.value = nodes.value.map((node: WorkflowNode) => ({
      ...node,
      data: {
        ...node.data,
        status: newStatuses[node.id] || 'idle',
      },
    }))

    // 更新边的动画状态
    edges.value = edges.value.map((edge: Edge) => ({
      ...edge,
      animated: isRunning.value && (
        newStatuses[edge.source] === 'running' ||
        newStatuses[edge.source] === 'completed'
      ),
    }))
  },
  { deep: true }
)

watch(isRunning, (running: boolean) => {
  edges.value = edges.value.map((edge: Edge) => ({
    ...edge,
    animated: running && (
      nodeStatuses.value[edge.source] === 'running' ||
      nodeStatuses.value[edge.source] === 'completed'
    ),
  }))
})

function onNodeClick(event: NodeMouseEvent) {
  selectedNodeId.value = event.node.id
}
</script>
