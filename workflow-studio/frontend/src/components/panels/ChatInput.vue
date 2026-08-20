<template>
  <div>
    <h2 class="text-lg font-bold mb-2">🔬 AI 研究助手</h2>
    <textarea
      v-model="question"
      placeholder="输入研究问题，如：分析2026年AI Agent技术趋势..."
      class="w-full border rounded-lg p-3 text-sm resize-none h-20 focus:outline-none focus:ring-2 focus:ring-blue-400"
      :disabled="disabled"
    />
    <button
      :disabled="disabled || !question.trim()"
      class="mt-2 w-full bg-blue-600 text-white py-2 rounded-lg flex items-center justify-center gap-2 disabled:opacity-50 hover:bg-blue-700 transition-colors"
      @click="handleSubmit"
    >
      <Loader2 v-if="disabled" class="h-4 w-4 animate-spin" />
      <Send v-else class="h-4 w-4" />
      {{ disabled ? '执行中...' : '启动工作流' }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Send, Loader2 } from '@lucide/vue'

const props = defineProps<{
  onSubmit: (question: string) => void
  disabled: boolean
}>()

const question = ref('')

function handleSubmit() {
  if (question.value.trim()) {
    props.onSubmit(question.value)
    question.value = ''
  }
}
</script>
