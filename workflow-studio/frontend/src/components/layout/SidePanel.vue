<template>
  <ChatInput :on-submit="startWorkflow" :disabled="isRunning" />

  <!-- 审核弹窗 -->
  <ReviewDialog
    v-if="isInterrupted"
    :on-submit="submitReview"
  />

  <!-- 流式输出 -->
  <div v-if="streamingText" class="border rounded-lg p-3 bg-gray-50 max-h-40 overflow-y-auto">
    <p class="text-xs text-gray-500 mb-1">实时输出：</p>
    <p class="text-sm whitespace-pre-wrap">{{ streamingText }}</p>
  </div>

  <!-- 节点详情 -->
  <NodeDetail v-if="selectedNode" :node-id="selectedNode" />

  <!-- 执行日志 -->
  <Timeline :logs="logs" />
</template>

<script setup lang="ts">
import ChatInput from '../panels/ChatInput.vue'
import ReviewDialog from '../panels/ReviewDialog.vue'
import NodeDetail from '../panels/NodeDetail.vue'
import Timeline from '../panels/Timeline.vue'

defineProps<{
  isRunning: boolean
  isInterrupted: boolean
  streamingText: string
  logs: string[]
  selectedNode: string | null
  startWorkflow: (question: string) => void
  submitReview: (status: string, feedback: string) => void
}>()
</script>
