<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'

const props = defineProps<{
  items: Array<{ id: string; label: string; available?: boolean }>
}>()

const active = ref(props.items.find((item) => item.available !== false)?.id ?? 'overview')

function show(id: string, updateHash = true) {
  const target = props.items.find((item) => item.id === id && item.available !== false)
  if (!target) return
  active.value = id
  document.querySelectorAll<HTMLElement>('[data-workspace-pane]').forEach((pane) => {
    const selected = pane.dataset.workspacePane === id
    pane.classList.toggle('is-active', selected)
    pane.hidden = !selected
  })
  if (updateHash) history.replaceState(null, '', `#content-${id}`)
  window.dispatchEvent(new CustomEvent('workspace-pane-change', { detail: { id } }))
  document.querySelector('.lecture-workspace-tabs')?.scrollIntoView({ block: 'nearest' })
}

function syncFromHash() {
  const id = location.hash.replace('#content-', '')
  show(props.items.some((item) => item.id === id) ? id : active.value, false)
}

onMounted(() => {
  syncFromHash()
  window.addEventListener('hashchange', syncFromHash)
})

onBeforeUnmount(() => window.removeEventListener('hashchange', syncFromHash))
</script>

<template>
  <nav class="lecture-workspace-tabs" aria-label="本讲学习内容">
    <button
      v-for="item in items"
      :key="item.id"
      type="button"
      :class="{ active: active === item.id }"
      :disabled="item.available === false"
      :aria-selected="active === item.id"
      @click="show(item.id)"
    >{{ item.label }}</button>
  </nav>
</template>
