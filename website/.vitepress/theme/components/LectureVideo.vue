<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  title: string
  url: string
}>()

const thumbnailUrl = computed(() => {
  try {
    const source = new URL(props.url)
    const id = source.hostname.includes('youtu.be')
      ? source.pathname.slice(1)
      : source.searchParams.get('v')
    return id ? `https://i.ytimg.com/vi/${encodeURIComponent(id)}/hqdefault.jpg` : ''
  } catch {
    return ''
  }
})
</script>

<template>
  <section v-if="url" class="lecture-video">
    <header>
      <div><span class="ll-eyebrow">Lecture video</span><strong>{{ title }}</strong></div>
      <a :href="url" target="_blank" rel="noreferrer">在 YouTube 打开 ↗</a>
    </header>
    <a class="lecture-video__frame" :href="url" target="_blank" rel="noreferrer">
      <img v-if="thumbnailUrl" :src="thumbnailUrl" :alt="`${title} 视频封面`" />
      <span><b aria-hidden="true">▶</b><strong>在 YouTube 播放</strong></span>
    </a>
  </section>
</template>
