<template>
  <g>
    <path
      :class="edgeClasses"
      :style="edgeStyle"
      :d="path"
      :id="id"
      fill="none"
    />
    <circle v-if="animated" r="4" :fill="color">
      <animateMotion :dur="`${duration}s`" repeatCount="indefinite" :path="path" />
    </circle>
  </g>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { getBezierPath, type EdgeProps } from '@vue-flow/core'

const props = defineProps<EdgeProps & { animated?: boolean }>()

const path = computed(() => {
  const [edgePath] = getBezierPath({
    sourceX: props.sourceX,
    sourceY: props.sourceY,
    sourcePosition: props.sourcePosition,
    targetX: props.targetX,
    targetY: props.targetY,
    targetPosition: props.targetPosition,
  })
  return edgePath
})

const animated = computed(() => props.animated ?? false)
const color = computed(() => animated.value ? '#3b82f6' : '#94a3b8')
const duration = 1.5

const edgeClasses = computed(() => [
  'vue-flow__edge-path',
  animated.value ? 'stroke-blue-500' : 'stroke-gray-400',
])

const edgeStyle = computed(() => ({
  stroke: color.value,
  strokeWidth: '2',
}))
</script>
