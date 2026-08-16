<script setup lang="ts">
import { withBase } from 'vitepress'

function isExternal(url: string) {
  return /^https?:\/\//.test(url)
}

function linkHref(url: string) {
  return isExternal(url) ? url : withBase(url)
}

defineProps<{
  eyebrow: string
  title: string
  courseRoute?: string
  description?: string
  status?: string
  links?: Array<{ label: string; url: string }>
  details?: Array<{ label: string; value: string }>
}>()
</script>

<template>
  <header class="course-header">
    <a v-if="courseRoute" class="course-header__back" :href="withBase(courseRoute)">← 返回课程学习路径</a>
    <div class="course-header__copy">
      <div class="course-header__topline">
        <span class="ll-eyebrow">{{ eyebrow }}</span>
        <span v-if="status" class="status-pill">{{ status }}</span>
      </div>
      <h1>{{ title }}</h1>
      <p v-if="description">{{ description }}</p>
      <dl v-if="details?.length" class="course-header__details">
        <div v-for="detail in details" :key="detail.label">
          <dt>{{ detail.label }}</dt>
          <dd>{{ detail.value }}</dd>
        </div>
      </dl>
    </div>
    <nav v-if="links?.length" class="course-header__actions" aria-label="本讲资源">
      <a
        v-for="link in links"
        :key="link.url"
        class="course-button"
        :href="linkHref(link.url)"
        :target="isExternal(link.url) ? '_blank' : undefined"
        :rel="isExternal(link.url) ? 'noreferrer' : undefined"
      >
        {{ link.label }} <span aria-hidden="true">↗</span>
      </a>
    </nav>
  </header>
</template>
