import { ref, computed } from 'vue'
import type { NodeStatus, SSEEvent } from '@/types/workflow'

export function useWorkflowSSE() {
  const nodeStatuses = ref<Record<string, NodeStatus>>({})
  const logs = ref<string[]>([])
  const isRunning = ref(false)
  const isInterrupted = ref(false)
  const interruptedAt = ref<string | null>(null)
  const streamingText = ref('')
  const workflowId = ref<string | null>(null)

  const currentWorkflowId = computed(() => workflowId.value)

  function setNodeStatus(nodeId: string, status: NodeStatus) {
    nodeStatuses.value = { ...nodeStatuses.value, [nodeId]: status }
  }

  function handleSSEEvent(event: SSEEvent) {
    switch (event.type) {
      case 'node_start':
        if (event.node) {
          setNodeStatus(event.node, 'running')
          logs.value = [...logs.value, `▶️ 开始执行: ${event.node}`]
        }
        break

      case 'node_end':
        if (event.node) {
          setNodeStatus(event.node, 'completed')
          logs.value = [...logs.value, `✅ 完成: ${event.node}`]
        }
        break

      case 'token':
        if (event.content) {
          streamingText.value += event.content
        }
        break

      case 'tool_result':
        if (event.data) {
          logs.value = [...logs.value, `🔧 工具结果: ${String(event.data).slice(0, 100)}`]
        }
        break

      case 'interrupted':
        isRunning.value = false
        isInterrupted.value = true
        interruptedAt.value = event.at || 'review'
        if (event.at) {
          setNodeStatus(event.at, 'waiting')
        }
        if (event.workflow_id) {
          workflowId.value = event.workflow_id
        }
        logs.value = [...logs.value, `⏸️ 工作流暂停，等待人工审核 (${event.at})`]
        break

      case 'completed':
        isRunning.value = false
        isInterrupted.value = false
        logs.value = [...logs.value, '🎉 工作流执行完成！']
        break

      case 'error':
        isRunning.value = false
        isInterrupted.value = false
        logs.value = [...logs.value, `❌ 错误: ${event.message}`]
        break
    }
  }

  async function startWorkflow(question: string) {
    // 重置状态
    nodeStatuses.value = {}
    logs.value = [`🚀 启动工作流: "${question}"`]
    isRunning.value = true
    isInterrupted.value = false
    interruptedAt.value = null
    streamingText.value = ''
    workflowId.value = null

    try {
      const response = await fetch('/api/workflow/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      })

      const reader = response.body!.getReader()
      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const text = decoder.decode(value)
        const lines = text.split('\n').filter((l) => l.startsWith('data: '))

        for (const line of lines) {
          try {
            const data = JSON.parse(line.slice(6))
            handleSSEEvent(data)
          } catch {
            // 忽略解析错误
          }
        }
      }
    } catch (err) {
      isRunning.value = false
      logs.value = [...logs.value, `❌ 错误: ${err}`]
    }
  }

  async function submitReview(status: string, feedback: string) {
    if (!workflowId.value) return

    isRunning.value = true
    isInterrupted.value = false
    logs.value = [...logs.value, `👤 审核提交: ${status}${feedback ? ` (${feedback})` : ''}`]

    try {
      const response = await fetch('/api/workflow/review', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          workflow_id: workflowId.value,
          status,
          feedback,
        }),
      })

      const reader = response.body!.getReader()
      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const text = decoder.decode(value)
        const lines = text.split('\n').filter((l) => l.startsWith('data: '))

        for (const line of lines) {
          try {
            const data = JSON.parse(line.slice(6))
            handleSSEEvent(data)
          } catch {
            // 忽略解析错误
          }
        }
      }
    } catch (err) {
      isRunning.value = false
      logs.value = [...logs.value, `❌ 错误: ${err}`]
    }
  }

  return {
    nodeStatuses,
    logs,
    isRunning,
    isInterrupted,
    interruptedAt,
    streamingText,
    currentWorkflowId,
    startWorkflow,
    submitReview,
    setNodeStatus,
  }
}
