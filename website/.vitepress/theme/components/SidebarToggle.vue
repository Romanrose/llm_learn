<script setup lang="ts">
import { onMounted, ref } from 'vue'

const collapsed = ref(false)

function applyState() {
  document.documentElement.classList.toggle('ll-sidebar-collapsed', collapsed.value)
}

function toggleSidebar() {
  collapsed.value = !collapsed.value
  localStorage.setItem('ll-sidebar-collapsed', collapsed.value ? '1' : '0')
  applyState()
}

onMounted(() => {
  collapsed.value = localStorage.getItem('ll-sidebar-collapsed') === '1'
  applyState()
})
</script>

<template>
  <button
    class="sidebar-toggle"
    :class="{ collapsed }"
    type="button"
    :aria-label="collapsed ? '展开左侧导航' : '收起左侧导航'"
    :title="collapsed ? '展开左侧导航' : '收起左侧导航'"
    @click="toggleSidebar"
  >
    <span aria-hidden="true">{{ collapsed ? '›' : '‹' }}</span>
  </button>
</template>
