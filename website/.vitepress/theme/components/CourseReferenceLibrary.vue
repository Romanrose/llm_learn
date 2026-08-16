<script setup lang="ts">
type Reading = { label: string; type?: string; url: string; note?: string }
type Group = { id: string; order: number; title: string; readings: Reading[] }

defineProps<{ groups: Group[]; total: number; uniqueTotal: number }>()

function typeLabel(type?: string) {
  return ({
    paper: '论文', blog: '技术文章', docs: '文档', code: '代码', book: '书籍 / 教程',
  } as Record<string, string>)[type ?? ''] ?? '参考资料'
}
</script>

<template>
  <section class="reference-library">
    <header class="reference-library__intro">
      <div>
        <span>资料索引</span>
        <p>按课程顺序整理论文、技术文章、文档和代码；每一项都保留在对应讲次下。</p>
      </div>
      <p class="reference-library__count"><strong>{{ uniqueTotal }}</strong> 条资料 · {{ groups.length }} 讲 · {{ total }} 次关联</p>
    </header>

    <nav class="reference-library__index" aria-label="参考资料章节索引">
      <a v-for="group in groups" :key="group.id" :href="`#references-${group.id}`">
        {{ String(group.order).padStart(2, '0') }}
      </a>
    </nav>

    <section
      v-for="group in groups"
      :id="`references-${group.id}`"
      :key="group.id"
      class="reference-group"
    >
      <header>
        <span>{{ String(group.order).padStart(2, '0') }}</span>
        <div><h2>{{ group.title }}</h2></div>
        <p>{{ group.readings.length }} 条资料</p>
      </header>
      <div class="reference-group__items">
        <a v-for="reading in group.readings" :key="reading.url" :href="reading.url" target="_blank" rel="noreferrer">
          <span>{{ typeLabel(reading.type) }}</span>
          <strong>{{ reading.label }}</strong>
          <small>{{ reading.note ?? '延伸阅读' }}</small>
          <b aria-hidden="true">↗</b>
        </a>
      </div>
    </section>
  </section>
</template>
