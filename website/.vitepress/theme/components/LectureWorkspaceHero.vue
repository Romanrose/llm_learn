<script setup lang="ts">
import { computed } from 'vue'
import { withBase } from 'vitepress'

const props = defineProps<{
  eyebrow: string
  title: string
  description?: string
  status?: string
  courseRoute: string
  videoUrl?: string
  details?: Array<{ label: string; value: string }>
  links?: Array<{ label: string; url: string }>
}>()

function isExternal(url: string) {
  return /^https?:\/\//.test(url)
}

function href(url: string) {
  return isExternal(url) ? url : withBase(url)
}

const thumbnailUrl = computed(() => {
  if (!props.videoUrl) return ''
  try {
    const source = new URL(props.videoUrl)
    const id = source.hostname.includes('youtu.be') ? source.pathname.slice(1) : source.searchParams.get('v')
    return id ? `https://i.ytimg.com/vi/${encodeURIComponent(id)}/hqdefault.jpg` : ''
  } catch {
    return ''
  }
})

const resourceLinks = computed(() => (props.links ?? []).filter((link) => {
  if (!props.videoUrl) return true
  return link.url !== props.videoUrl && !/课程视频|课堂视频|lecture video/i.test(link.label)
}))

const heroLinks = computed(() => {
  const links = [...resourceLinks.value]
  if (props.videoUrl) links.push({ label: '视频原页', url: props.videoUrl })
  return links
})
</script>

<template>
  <section class="workspace-hero">
    <div class="workspace-hero__copy">
      <a class="workspace-hero__back" :href="withBase(courseRoute)">← 返回课程</a>
      <div class="workspace-hero__topline">
        <span class="ll-eyebrow">{{ eyebrow }}</span>
        <span v-if="status" class="status-pill">{{ status }}</span>
      </div>
      <h1>{{ title }}</h1>
      <p v-if="description">{{ description }}</p>
      <dl v-if="details?.length">
        <div v-for="detail in details" :key="detail.label"><dt>{{ detail.label }}</dt><dd>{{ detail.value }}</dd></div>
      </dl>
      <nav v-if="heroLinks.length" class="workspace-hero__resources" aria-label="本讲课程资源">
        <span>本讲资源</span>
        <div>
          <a
            v-for="link in heroLinks"
            :key="link.url"
            :href="href(link.url)"
            :target="isExternal(link.url) ? '_blank' : undefined"
            :rel="isExternal(link.url) ? 'noreferrer' : undefined"
          >{{ link.label }} <b aria-hidden="true">↗</b></a>
        </div>
      </nav>
    </div>
    <div class="workspace-hero__video">
      <a v-if="videoUrl" class="workspace-hero__watch" :href="videoUrl" target="_blank" rel="noreferrer">
        <img v-if="thumbnailUrl" :src="thumbnailUrl" :alt="`${title} 视频封面`" />
        <span><b aria-hidden="true">▶</b><strong>在 YouTube 观看</strong><small>打开 CS336 官方录播</small></span>
      </a>
      <div v-else class="workspace-hero__empty"><span>视频待接入</span><small>官方资源发布后会自动出现在这里</small></div>
    </div>
  </section>
</template>
