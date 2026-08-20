import type { Node, Edge } from '@vue-flow/core'

// 节点执行状态
export type NodeStatus = 'idle' | 'running' | 'completed' | 'error' | 'waiting'

// 节点类型
export type NodeType = 'plan' | 'search' | 'analyze' | 'write' | 'review' | 'revision' | 'output'

// 自定义节点数据
export interface WorkflowNodeData {
  label: string
  status: NodeStatus
  nodeType: NodeType
  output?: string
  startTime?: number
  endTime?: number
  [key: string]: unknown
}

export type WorkflowNode = Node<WorkflowNodeData>

// SSE 事件类型
export interface SSEEvent {
  type: 'node_start' | 'node_end' | 'token' | 'tool_result' | 'interrupted' | 'completed' | 'error'
  node?: string
  content?: string
  output?: string
  data?: unknown
  at?: string
  message?: string
  workflow_id?: string
}

// 工作流状态
export interface WorkflowState {
  nodeStatuses: Record<string, NodeStatus>
  logs: string[]
  isRunning: boolean
  isInterrupted: boolean
  interruptedAt: string | null
  streamingText: string
  workflowId: string | null
}

// 图结构（从后端获取）
export interface GraphStructureNode {
  id: string
  label: string
  type: NodeType
  position: { x: number; y: number }
}

export interface GraphStructureEdge {
  id: string
  source: string
  target: string
  label?: string
}

export interface GraphStructure {
  nodes: GraphStructureNode[]
  edges: GraphStructureEdge[]
}
