<template>
  <div class="border rounded-lg p-3 bg-gray-50">
    <h3 class="text-sm font-medium text-gray-600 mb-2">📄 节点详情</h3>
    <div class="text-sm">
      <p class="text-gray-500">节点: <span class="font-medium text-gray-700">{{ nodeId }}</span></p>
      <p class="text-gray-500 mt-1">
        状态: <span :class="statusClass">{{ status }}</span>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useWorkflowStore } from '@/stores/workflow'

const props = defineProps<{
  nodeId: string
}>()

const store = useWorkflowStore()

const status = computed(() => store.nodeStatuses[props.nodeId] || 'idle')

const statusClass = computed(() => {
  const classes: Record<string, string> = {
    idle: 'text-gray-500',
    running: 'text-blue-600 font-medium',
    completed: 'text-green-600 font-medium',
    error: 'text-red-600 font-medium',
    waiting: 'text-amber-600 font-medium',
  }
  return classes[status.value] || classes.idle
})
</script>
