<script setup lang="ts">
import { withBase } from 'vitepress'

defineProps<{
  items: Array<{
    id: string
    order?: number
    date?: string
    title: string
    subtitle?: string
    instructors?: string[]
    status: string
    route: string
    resourceCount: number
    outputCount: number
    outputLabels: string[]
  }>
}>()
</script>

<template>
  <ol class="lecture-timeline">
    <li v-for="item in items" :key="item.id">
      <a class="lecture-row" :href="withBase(item.route)">
        <div class="lecture-row__index">
          <strong>{{ String(item.order ?? '').padStart(2, '0') }}</strong>
          <time v-if="item.date">{{ item.date }}</time>
        </div>
        <div class="lecture-row__content">
          <h3>{{ item.title }}</h3>
          <p v-if="item.subtitle">{{ item.subtitle }}</p>
          <span v-if="item.instructors?.length" class="lecture-row__instructor">
            {{ item.instructors.join(' / ') }}
          </span>
        </div>
        <div class="lecture-row__summary">
          <span class="lecture-row__status">{{ item.status }}</span>
          <small>{{ item.resourceCount }} 项资料</small>
          <small :class="{ ready: item.outputCount }">
            {{ item.outputCount ? `${item.outputCount} 项笔记` : '笔记待生成' }}
          </small>
        </div>
        <span class="lecture-row__arrow" aria-hidden="true">→</span>
      </a>
    </li>
  </ol>
</template>
