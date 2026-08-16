<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'

type OutlineItem = { id: string; level: number; text: string }

const items = ref<OutlineItem[]>([])

function refresh() {
  nextTick(() => {
    const pane = document.querySelector<HTMLElement>('[data-workspace-pane].is-active')
    if (!pane) {
      items.value = []
      return
    }
    items.value = [...pane.querySelectorAll<HTMLElement>('h2[id], h3[id], h4[id]')]
      .map((heading) => ({
        id: heading.id,
        level: Number(heading.tagName.slice(1)),
        text: heading.childNodes[0]?.textContent?.trim() || heading.textContent?.replace('#', '').trim() || '',
      }))
      .filter((item) => item.text)
  })
}

onMounted(() => {
  refresh()
  window.addEventListener('workspace-pane-change', refresh)
})

onBeforeUnmount(() => window.removeEventListener('workspace-pane-change', refresh))
</script>

<template>
  <aside v-if="items.length" class="lecture-workspace-outline" aria-label="当前内容目录">
    <strong>当前内容</strong>
    <nav>
      <a
        v-for="item in items"
        :key="item.id"
        :class="`level-${item.level}`"
        :href="`#${item.id}`"
      >{{ item.text }}</a>
    </nav>
  </aside>
</template>
