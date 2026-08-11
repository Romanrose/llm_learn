<script setup lang="ts">
import { withBase } from 'vitepress'

defineProps<{
  active?: string
  items: Array<{ id: string; label: string; route: string; available?: boolean }>
}>()
</script>

<template>
  <nav class="course-tabs" aria-label="课程内容类型">
    <a
      v-for="item in items"
      :key="item.id"
      :href="withBase(item.route)"
      :class="{ active: item.id === active, disabled: item.available === false }"
      :aria-current="item.id === active ? 'page' : undefined"
    >
      {{ item.label }}
    </a>
  </nav>
</template>
