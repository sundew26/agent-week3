<template>
  <div class="border-2 border-amber-300 rounded-xl p-4 bg-amber-50">
    <h3 class="font-medium text-amber-800 mb-2 flex items-center gap-2">
      <MessageSquare class="h-4 w-4" />
      人工审核
    </h3>
    <p class="text-sm text-amber-700 mb-3">报告已生成，请审核质量：</p>

    <textarea
      v-model="feedback"
      placeholder="审核意见（不通过时必填）..."
      class="w-full border rounded-lg p-2 text-sm h-16 mb-3 focus:outline-none focus:ring-2 focus:ring-amber-400"
    />

    <div class="flex gap-2">
      <button
        class="flex-1 bg-green-600 text-white py-2 rounded-lg text-sm flex items-center justify-center gap-1 hover:bg-green-700 transition-colors"
        @click="handleApprove"
      >
        <CheckCircle class="h-4 w-4" /> 通过
      </button>
      <button
        class="flex-1 bg-red-600 text-white py-2 rounded-lg text-sm flex items-center justify-center gap-1 hover:bg-red-700 transition-colors"
        @click="handleReject"
      >
        <XCircle class="h-4 w-4" /> 不通过
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { CheckCircle, XCircle, MessageSquare } from '@lucide/vue'

const props = defineProps<{
  onSubmit: (status: string, feedback: string) => void
}>()

const feedback = ref('')

function handleApprove() {
  props.onSubmit('approved', '')
  feedback.value = ''
}

function handleReject() {
  if (feedback.value.trim()) {
    props.onSubmit('rejected', feedback.value)
    feedback.value = ''
  }
}
</script>
