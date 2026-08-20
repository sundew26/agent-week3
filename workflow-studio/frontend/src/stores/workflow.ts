import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { NodeStatus, GraphStructure } from '@/types/workflow'

export const useWorkflowStore = defineStore('workflow', () => {
  // 状态
  const workflowId = ref<string | null>(null)
  const nodeStatuses = ref<Record<string, NodeStatus>>({})
  const logs = ref<string[]>([])
  const isRunning = ref(false)
  const isInterrupted = ref(false)
  const interruptedAt = ref<string | null>(null)
  const streamingText = ref('')
  const graphStructure = ref<GraphStructure | null>(null)
  const selectedNode = ref<string | null>(null)

  // Getters
  const isNodeRunning = computed(() => {
    return (nodeId: string) => nodeStatuses.value[nodeId] === 'running'
  })

  const isNodeCompleted = computed(() => {
    return (nodeId: string) => nodeStatuses.value[nodeId] === 'completed'
  })

  const completedNodes = computed(() => {
    return Object.entries(nodeStatuses.value)
      .filter(([, status]) => status === 'completed')
      .map(([id]) => id)
  })

  // Actions
  function setNodeStatus(nodeId: string, status: NodeStatus) {
    nodeStatuses.value = { ...nodeStatuses.value, [nodeId]: status }
  }

  function resetState() {
    nodeStatuses.value = {}
    logs.value = []
    isRunning.value = false
    isInterrupted.value = false
    interruptedAt.value = null
    streamingText.value = ''
    workflowId.value = null
    selectedNode.value = null
  }

  function addLog(log: string) {
    logs.value = [...logs.value, log]
  }

  function setGraphStructure(structure: GraphStructure) {
    graphStructure.value = structure
  }

  return {
    workflowId,
    nodeStatuses,
    logs,
    isRunning,
    isInterrupted,
    interruptedAt,
    streamingText,
    graphStructure,
    selectedNode,
    isNodeRunning,
    isNodeCompleted,
    completedNodes,
    setNodeStatus,
    resetState,
    addLog,
    setGraphStructure,
  }
})
