<template>
  <div class="flex-1">
    <h3 class="text-sm font-medium text-gray-600 mb-2">📝 执行日志</h3>
    <div class="space-y-1 text-xs font-mono max-h-64 overflow-y-auto">
      <p
        v-for="(log, i) in logs"
        :key="i"
        class="text-gray-600 border-b border-gray-100 pb-1"
      >
        {{ log }}
      </p>
      <p v-if="logs.length === 0" class="text-gray-400 italic">暂无日志...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  logs: string[]
}>()
</script>
