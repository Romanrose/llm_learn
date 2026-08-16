<script setup lang="ts">
import { computed } from 'vue'
import { withBase } from 'vitepress'

const props = defineProps<{
  eyebrow: string
  title: string
  description?: string
  status?: string
  startRoute?: string
  referenceRoute?: string
  watchUrl?: string
  previewUrl?: string
  links?: Array<{ label: string; url: string }>
  details?: Array<{ label: string; value: string }>
}>()

const extraActions = computed(() => (props.links ?? []).filter((link) => (
  link.url !== props.watchUrl && !/官方视频|课程视频|课堂视频/i.test(link.label)
)))

const previewImage = computed(() => {
  if (!props.previewUrl) return ''
  try {
    const source = new URL(props.previewUrl)
    const id = source.hostname.includes('youtu.be') ? source.pathname.slice(1) : source.searchParams.get('v')
    return id ? `https://i.ytimg.com/vi/${encodeURIComponent(id)}/hqdefault.jpg` : ''
  } catch {
    return ''
  }
})
</script>

<template>
  <section class="course-hero">
    <div class="course-hero__intro">
      <div class="course-hero__topline">
        <span class="ll-eyebrow">{{ eyebrow }}</span>
        <span v-if="status" class="status-pill">{{ status }}</span>
      </div>
      <h1>{{ title }}</h1>
      <p v-if="description">{{ description }}</p>
      <div class="course-hero__buttons">
        <a v-if="startRoute" class="course-button course-button--primary" :href="withBase(startRoute)">开始学习 <span aria-hidden="true">→</span></a>
        <a v-if="referenceRoute" class="course-button" :href="withBase(referenceRoute)">参考资料库 <span aria-hidden="true">→</span></a>
        <a v-if="watchUrl" class="course-button" :href="watchUrl" target="_blank" rel="noreferrer">观看官方课程 <span aria-hidden="true">↗</span></a>
        <a v-for="link in extraActions" :key="link.url" class="course-button" :href="link.url" target="_blank" rel="noreferrer">{{ link.label }} <span aria-hidden="true">↗</span></a>
      </div>
      <dl v-if="details?.length" class="course-hero__details">
        <div v-for="detail in details" :key="detail.label">
          <dt>{{ detail.label }}</dt>
          <dd>{{ detail.value }}</dd>
        </div>
      </dl>
    </div>
    <div class="course-hero__media">
      <a v-if="watchUrl" :href="watchUrl" target="_blank" rel="noreferrer" class="course-hero__play">
        <img v-if="previewImage" :src="previewImage" alt="CS336 官方课程预览" />
        <span aria-hidden="true">▶</span>
        <strong>在 YouTube 观看课程</strong>
        <small>打开 CS336 官方播放列表</small>
      </a>
    </div>
  </section>
</template>
