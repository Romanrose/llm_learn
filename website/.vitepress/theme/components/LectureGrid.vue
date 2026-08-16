<script setup lang="ts">
import { computed } from 'vue'
import { withBase } from 'vitepress'

type Lecture = {
  id: string; order?: number; date?: string; title: string; subtitle?: string; instructors?: string[]
  status: string; route: string; resourceCount: number; outputCount: number; outputLabels: string[]
}

const props = defineProps<{ items: Lecture[] }>()

const moduleDefinitions = [
  { id: 'course-references', title: '00 · Course References', description: '按讲次整理的论文、技术文章、文档与代码', from: 0, to: 0 },
  { id: 'foundations', title: '01 · Foundations', description: 'Tokenization、PyTorch 与模型架构', from: 1, to: 4 },
  { id: 'training-systems', title: '02 · Training Systems', description: 'GPU、Kernel 与分布式并行', from: 5, to: 8 },
  { id: 'scaling-inference', title: '03 · Scaling & Inference', description: 'Scaling Laws 与推理系统', from: 9, to: 11 },
  { id: 'evaluation-data', title: '04 · Evaluation & Data', description: '评估、数据来源与数据治理', from: 12, to: 14 },
  { id: 'post-training', title: '05 · Post-training & Alignment', description: 'SFT、RLHF、RLVR 与多模态对齐', from: 15, to: 17 },
  { id: 'guest-lectures', title: '06 · Guest Lectures', description: '外部研究者专题分享', from: 18, to: 99 },
]

const modules = computed(() => moduleDefinitions.map((module) => ({
  ...module,
  items: props.items.filter((item) => (item.order ?? 0) >= module.from && (item.order ?? 0) <= module.to),
})).filter((module) => module.items.length))

function shortLabel(label: string) {
  return ({ 'Lecture Note': '笔记', 'Blog 解读': 'Blog', '中文逐字稿': '中文', '英文逐字稿': 'EN' } as Record<string, string>)[label] ?? label
}
</script>

<template>
  <div class="learning-path">
    <section v-for="module in modules" :key="module.id" :id="module.id" class="learning-module">
      <header class="learning-module__header">
        <div><h3>{{ module.title }}</h3><p>{{ module.description }}</p></div>
        <span>{{ module.items.length }} lectures</span>
      </header>
      <ol class="lecture-timeline">
        <li v-for="item in module.items" :key="item.id">
          <a class="lecture-row" :href="withBase(item.route)">
            <div class="lecture-row__index"><strong>{{ String(item.order ?? '').padStart(2, '0') }}</strong></div>
            <div class="lecture-row__content">
              <h4>{{ item.title }}</h4>
              <p v-if="item.subtitle">{{ item.subtitle }}</p>
              <span>{{ [item.date, item.instructors?.join(' / ')].filter(Boolean).join(' · ') }}</span>
            </div>
            <div class="lecture-row__assets" aria-label="可用内容">
              <span v-for="label in item.outputLabels" :key="label">{{ shortLabel(label) }}</span>
              <span v-if="!item.outputLabels.length" class="is-pending">待接入</span>
            </div>
            <span class="lecture-row__arrow" aria-hidden="true">→</span>
          </a>
        </li>
      </ol>
    </section>
  </div>
</template>
