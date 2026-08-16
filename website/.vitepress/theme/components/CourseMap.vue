<script setup lang="ts">
import { withBase } from 'vitepress'
import catalog from '../../generated/catalog.json'
import settings from '../../generated/site.json'

type MapItem = { id: string; courseId?: string; title: string; subtitle?: string; detail?: string; route: string }
type MapSection = { id: string; title: string; description?: string; items: MapItem[] }

const sections = (settings.sections ?? []) as MapSection[]
const courseById = new Map(catalog.map((course) => [course.id, course]))

function itemDetail(item: MapItem) {
  if (!item.courseId) return item.detail ?? '专题内容'
  const course = courseById.get(item.courseId)
  if (!course) return item.detail ?? '课程整理中'
  const published = course.items.filter((lecture) => lecture.status === 'published' || lecture.generation?.state === 'reviewed').length
  return `${published}/${course.items.length} 讲已整理`
}

function itemType(item: MapItem) {
  if (item.courseId) return 'course'
  if (item.route.includes('/topics/papers')) return 'paper'
  if (item.route.includes('/topics/interviews')) return 'talk'
  return 'project'
}

function itemTypeLabel(item: MapItem) {
  return ({ course: '课程', project: '项目', paper: '论文 / 文章', talk: '演讲 / 访谈' } as const)[itemType(item)]
}

</script>

<template>
  <section class="course-library" aria-labelledby="course-map">
    <header class="course-library__header">
      <div>
        <h2 id="course-map">课程与专题</h2>
        <p>按方向归档的课程、项目、论文与演讲；进入条目后可继续阅读相应的学习资料。</p>
      </div>
    </header>

    <div class="course-library__body">
      <div class="course-library__groups">
        <section v-for="section in sections" :key="section.id" :id="section.id" class="course-group">
          <header>
            <div>
              <h3>{{ section.title }}</h3>
              <p v-if="section.description">{{ section.description }}</p>
            </div>
            <small>{{ section.items.length }} 项</small>
          </header>
          <div class="course-list">
            <a v-for="item in section.items" :key="item.id" :href="withBase(item.route)" class="course-entry">
              <span class="course-list__kind">{{ itemTypeLabel(item) }}</span>
              <span class="course-list__main">
                <strong>{{ item.title }}</strong>
                <small v-if="item.subtitle">{{ item.subtitle }}</small>
                <em>{{ itemDetail(item) }}</em>
              </span>
            </a>
          </div>
        </section>
      </div>
    </div>
  </section>
</template>
