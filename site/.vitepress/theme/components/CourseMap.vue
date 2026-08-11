<script setup lang="ts">
import { computed } from 'vue'
import { withBase } from 'vitepress'
import catalog from '../../generated/catalog.json'
import settings from '../../generated/site.json'

type MapItem = {
  id: string
  courseId?: string
  title: string
  subtitle?: string
  detail?: string
  route: string
}

type MapSection = {
  id: string
  title: string
  description?: string
  items: MapItem[]
}

const sections = (settings.sections ?? []) as MapSection[]
const courseById = new Map(catalog.map((course) => [course.id, course]))

function itemDetail(item: MapItem) {
  if (!item.courseId) return item.detail
  const course = courseById.get(item.courseId)
  if (!course) return item.detail ?? '课程整理中'
  const lectures = course.items.length
  const outputs = course.items.reduce((total, lecture) => total + lecture.outputs.length, 0)
  return `${lectures} 讲 · ${outputs} 项内容`
}

const stats = computed(() => {
  const lectures = catalog.reduce((total, course) => total + course.items.length, 0)
  const outputs = catalog.reduce(
    (total, course) => total + course.items.reduce((count, item) => count + item.outputs.length, 0),
    0,
  )
  const collections = sections.reduce((total, section) => total + section.items.length, 0)
  return [
    { value: catalog.length, label: '门结构化课程' },
    { value: lectures, label: '节已接入 Lecture' },
    { value: outputs, label: '份可阅读内容' },
    { value: collections, label: '个课程与专题入口' },
  ]
})
</script>

<template>
  <div class="map-stats" aria-label="内容规模">
    <div v-for="stat in stats" :key="stat.label">
      <strong>{{ stat.value }}</strong>
      <span>{{ stat.label }}</span>
    </div>
  </div>

  <h2 id="course-map">课程地图</h2>
  <section v-for="section in sections" :key="section.id" class="map-section">
    <h3 :id="section.id">{{ section.title }} <small>({{ section.items.length }})</small></h3>
    <p v-if="section.description" class="map-section__description">{{ section.description }}</p>
    <div class="course-map-grid">
      <a v-for="item in section.items" :key="item.id" :href="withBase(item.route)">
        <strong>{{ item.title }}</strong>
        <span v-if="item.subtitle">{{ item.subtitle }}</span>
        <small>{{ itemDetail(item) }}</small>
      </a>
    </div>
  </section>
</template>
