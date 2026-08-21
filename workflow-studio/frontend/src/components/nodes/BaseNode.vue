<template>
  <div :class="containerClasses">
    <Handle type="target" :position="Position.Top" class="!bg-gray-400" />

    <div class="flex items-center gap-2">
      <span :class="textClasses">{{ data.label }}</span>
      <component
        :is="statusIcon"
        :class="iconClasses"
      />
    </div>

    <!-- 执行耗时 -->
    <p v-if="data.startTime && data.endTime" class="text-xs text-gray-400 mt-1">
      ⏱️ {{ ((data.endTime - data.startTime) / 1000).toFixed(1) }}s
    </p>

    <Handle type="source" :position="Position.Bottom" class="!bg-gray-400" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Handle, Position } from '@vue-flow/core'
import { Loader2, CheckCircle, XCircle, Clock, Circle } from '@lucide/vue'
import { clsx } from 'clsx'
import type { NodeProps } from '@vue-flow/core'
import type { WorkflowNodeData, NodeStatus } from '@/types/workflow'

const props = defineProps<NodeProps<WorkflowNodeData>>()

const statusConfig: Record<NodeStatus, { color: string; textColor: string; animate?: boolean }> = {
  idle: { color: 'border-gray-300 bg-white', textColor: 'text-gray-600' },
  running: { color: 'border-blue-400 bg-blue-50 shadow-lg shadow-blue-100', textColor: 'text-blue-700', animate: true },
  completed: { color: 'border-green-400 bg-green-50', textColor: 'text-green-700' },
  error: { color: 'border-red-400 bg-red-50', textColor: 'text-red-700' },
  waiting: { color: 'border-amber-400 bg-amber-50 animate-pulse', textColor: 'text-amber-700' },
}

const statusIcons: Record<NodeStatus, typeof Loader2> = {
  idle: Circle,
  running: Loader2,
  completed: CheckCircle,
  error: XCircle,
  waiting: Clock,
}

const config = computed(() => statusConfig[props.data.status] || statusConfig.idle)
const statusIcon = computed(() => statusIcons[props.data.status] || statusIcons.idle)

const containerClasses = computed(() =>
  clsx(
    'px-4 py-3 rounded-xl border-2 shadow-sm min-w-[140px] transition-all duration-300',
    config.value.color
  )
)

const textClasses = computed(() =>
  clsx('font-medium text-sm', config.value.textColor)
)

const iconClasses = computed(() =>
  clsx(
    'h-4 w-4 ml-auto',
    config.value.textColor,
    config.value.animate && 'animate-spin'
  )
)
</script>
