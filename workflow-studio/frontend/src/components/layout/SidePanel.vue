<template>
  <ChatInput :on-submit="startWorkflow" :disabled="isRunning" />

  <!-- 审核弹窗 -->
  <ReviewDialog
    v-if="isInterrupted"
    :on-submit="submitReview"
  />

  <!-- 流式输出 -->
  <div v-if="streamingText && !finalReport" class="border rounded-lg p-3 bg-gray-50 max-h-40 overflow-y-auto">
    <p class="text-xs text-gray-500 mb-1">实时输出：</p>
    <p class="text-sm whitespace-pre-wrap">{{ streamingText }}</p>
  </div>

  <!-- 最终报告 -->
  <div v-if="finalReport" ref="reportRef" class="border rounded-lg p-4 bg-white shadow-sm">
    <div class="flex items-center justify-between mb-3">
      <div class="flex items-center gap-2">
        <span class="text-lg">✅</span>
        <h3 class="font-semibold text-gray-800">研究报告</h3>
      </div>
      <button
        class="flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-white bg-blue-500 rounded-lg hover:bg-blue-600 transition-colors"
        @click="exportPDF"
      >
        <Download class="h-3.5 w-3.5" />
        导出 PDF
      </button>
    </div>
    <div class="prose prose-sm max-h-96 overflow-y-auto whitespace-pre-wrap text-sm text-gray-700 leading-relaxed">
      {{ finalReport }}
    </div>
  </div>

  <!-- 节点详情 -->
  <NodeDetail v-if="selectedNode" :node-id="selectedNode" />

  <!-- 执行日志 -->
  <Timeline :logs="logs" />
</template>

<script setup lang="ts">
import { ref } from 'vue'
import html2pdf from 'html2pdf.js'
import { Download } from '@lucide/vue'
import ChatInput from '../panels/ChatInput.vue'
import ReviewDialog from '../panels/ReviewDialog.vue'
import NodeDetail from '../panels/NodeDetail.vue'
import Timeline from '../panels/Timeline.vue'

const props = defineProps<{
  isRunning: boolean
  isInterrupted: boolean
  streamingText: string
  finalReport: string
  logs: string[]
  selectedNode: string | null
  startWorkflow: (question: string) => void
  submitReview: (status: string, feedback: string) => void
}>()

const reportRef = ref<HTMLElement | null>(null)

async function exportPDF() {
  if (!reportRef.value) return
  const today = new Date().toISOString().slice(0, 10)
  html2pdf()
    .set({
      margin: 10,
      filename: `研究报告_${today}.pdf`,
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: { scale: 2 },
      jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
    })
    .from(reportRef.value)
    .save()
}
</script>
