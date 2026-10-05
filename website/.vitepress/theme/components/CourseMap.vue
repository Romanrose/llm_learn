<script setup lang="ts">
import { withBase } from 'vitepress'
import catalog from '../../generated/catalog.json'
import settings from '../../generated/site.json'

type MapItem = { id: string; courseId?: string; title: string; subtitle?: string; detail?: string; route: string; versions?: Array<{ courseId: string; label: string; route: string }> }
type MapSection = { id: string; title: string; description?: string; items: MapItem[] }

const sections = (settings.sections ?? []) as MapSection[]
const courseById = new Map(catalog.map((course) => [course.id, course]))

function itemDetail(item: MapItem) {
  if (!item.courseId) return item.detail ?? '专题内容'
  const course = courseById.get(item.courseId)
  if (!course) return item.detail ?? '课程整理中'
  const published = course.items.filter((lecture) => lecture.status === 'published' || lecture.generation?.state === 'reviewed').length
  const pending = course.items.filter((unit) => unit.reviewPreview).length
  if (pending) return `${pending}/${course.items.length} ${course.unitLabel ?? '讲'} · 候选稿待审核`
  if (course.publishOutputs === false) return `${course.items.length} ${course.unitLabel ?? '讲'} · 官方资源入口`
  return `${published}/${course.items.length} ${course.unitLabel ?? '讲'}已整理`
}

</script>

<template>
  <section class="course-library" aria-labelledby="course-map">
    <header class="course-library__header">
      <div>
        <h2 id="course-map">课程目录</h2>
        <p>按学习方向浏览课程，进入课程后查看讲义、代码、阅读资料与已整理的笔记。</p>
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
            <small>{{ section.items.length }} 门课程</small>
          </header>
          <div class="course-list">
            <template v-for="item in section.items" :key="item.id">
              <a :href="withBase(item.route)" class="course-entry">
                <span class="course-list__kind">课程</span>
                <span class="course-list__main">
                  <strong>{{ item.title }}</strong>
                  <small v-if="item.subtitle">{{ item.subtitle }}</small>
                  <em>{{ itemDetail(item) }}</em>
                </span>
              </a>
              <p v-if="item.versions?.length" class="course-versions">
                <a v-for="version in item.versions" :key="version.courseId" :href="withBase(version.route)">{{ version.label }}</a>
              </p>
            </template>
          </div>
        </section>
      </div>
    </div>
  </section>
</template>

<style scoped>
.course-versions { margin: 0 0 5px 40px; font-size: 13px; }
.course-versions a { color: var(--vp-c-text-3); font-weight: 400; }
</style>
