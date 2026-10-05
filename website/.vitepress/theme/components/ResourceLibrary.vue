<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { withBase } from 'vitepress'
import catalog from '../../generated/catalog.json'
import settings from '../../generated/site.json'
import data from '../../generated/resources.json'

type Association = { courseId: string; courseTitle: string; lectureId: string | null; lectureTitle: string; route: string; type: string }
type Resource = { label: string; url: string; type?: string; note?: string; practiceSource?: string; associations: Association[] }
const resources = data as Resource[]
const courseIds = settings.sections.flatMap(section => section.items.flatMap(item => [item.courseId, ...('versions' in item ? item.versions.map(version => version.courseId) : [])]))
const courses = [...catalog].sort((a, b) => courseIds.indexOf(a.id) - courseIds.indexOf(b.id))
const rank = new Map(courses.map((course, index) => [course.id, index]))
const byId = new Map(courses.map(course => [course.id, course]))
const query = ref('')
const selectedCourse = ref('')
const selectedType = ref('')
const scope = ref('all')
const page = ref(1)
const pageSize = 60
let mounted = false
const typeLabels: Record<string, string> = {
  assignment: 'Lab / 作业', slides: '讲义', docs: '文档', book: '教材', paper: '论文',
  code: '代码', video: '视频', blog: '文章', reference: '参考资料', collection: '配套阅读',
}
const types = Object.entries(typeLabels).filter(([type]) => resources.some(resource => resource.type === type || resource.associations.some(association => association.type === type)))
const typeRank = new Map(Object.keys(typeLabels).map((type, index) => [type, index]))
const collator = new Intl.Collator('zh-CN', { numeric: true })
const searchText = new Map(resources.map(resource => [resource.url, [
  resource.label, resource.url, resource.note ?? '', typeLabels[resource.type ?? ''] ?? '',
  ...resource.associations.flatMap(association => [association.courseId, association.courseTitle, association.lectureTitle, typeLabels[association.type] ?? '']),
].join(' ').toLocaleLowerCase()]))

function associations(resource: Resource) {
  return resource.associations.filter(association => (
    (!selectedCourse.value || association.courseId === selectedCourse.value)
    && (scope.value === 'practice' ? association.type === 'assignment' : !selectedType.value || association.type === selectedType.value)
  )).sort((a, b) => (rank.get(a.courseId) ?? 99) - (rank.get(b.courseId) ?? 99))
}
function typeOf(resource: Resource) { return associations(resource)[0]?.type ?? resource.type ?? 'reference' }
function titleOf(resource: Resource) {
  const association = associations(resource)[0]
  const label = resource.label.replace(/^Fall \d{4}\s*·\s*/, '').trim()
  if (association && /^(\(?slides\)?|\(?examples\)?|pdf|pptx|code|tar|handout|writeup|课程视频|lecture \d+ slides \(PDF\))$/i.test(label)) {
    return `${association.lectureTitle} · ${typeLabels[typeOf(resource)] ?? label}${/pptx/i.test(label) ? ' PPTX' : ''}`
  }
  if (association && /^\d+(?:\.\d+)+$/.test(label)) return `${association.lectureTitle} · 教材 ${label}`
  return resource.label
}
function sourceOf(resource: Resource) {
  try {
    const host = new URL(resource.url).hostname.replace(/^www\./, '')
    if (host === 'github.com') return 'GitHub'
    if (host === 'github.mit.edu') return 'MIT GitHub'
    if (host.includes('youtube') || host === 'youtu.be') return 'YouTube'
    if (host.includes('panopto')) return 'Panopto'
    if (host === 'arxiv.org') return 'arXiv'
    return host
  } catch { return '站内资料' }
}
const filtered = computed(() => {
  const terms = query.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean)
  return resources.filter(resource => {
    const categoryMatches = resource.type === 'collection'
      ? scope.value !== 'practice' && (!selectedCourse.value || selectedCourse.value === 'reading') && (!selectedType.value || selectedType.value === 'collection')
      : associations(resource).length > 0
    return categoryMatches && terms.every(term => searchText.get(resource.url)?.includes(term))
  }).sort((a, b) => {
    const courseOrder = (rank.get(associations(a)[0]?.courseId) ?? 99) - (rank.get(associations(b)[0]?.courseId) ?? 99)
    return courseOrder || (typeRank.get(typeOf(a)) ?? 99) - (typeRank.get(typeOf(b)) ?? 99) || collator.compare(titleOf(a), titleOf(b))
  })
})
const browsing = computed(() => !query.value.trim() && !selectedCourse.value && !selectedType.value && scope.value === 'all')
const pageCount = computed(() => Math.max(1, Math.ceil(filtered.value.length / pageSize)))
function previewItems(items: Resource[]) {
  const counts = new Map<string, number>()
  const preview = items.filter(resource => {
    const type = typeOf(resource)
    const count = counts.get(type) ?? 0
    counts.set(type, count + 1)
    return count < 2
  }).slice(0, 6)
  return [...preview, ...items.filter(resource => !preview.includes(resource))].slice(0, 6)
}
const groups = computed(() => {
  const rows = browsing.value ? filtered.value : filtered.value.slice((page.value - 1) * pageSize, page.value * pageSize)
  const grouped = new Map<string, Resource[]>()
  for (const resource of rows) {
    const id = associations(resource)[0]?.courseId ?? 'reading'
    if (!grouped.has(id)) grouped.set(id, [])
    grouped.get(id)!.push(resource)
  }
  return [...grouped].map(([id, items]) => ({
    id, title: byId.get(id)?.shortTitle ?? byId.get(id)?.title ?? '配套阅读',
    route: id === 'reading' ? '' : `/generated/courses/${id}/`,
    count: items.length, items: browsing.value ? previewItems(items) : items,
  }))
})
function readUrl() {
  const params = new URLSearchParams(location.search)
  query.value = (params.get('q') ?? '').slice(0, 256)
  selectedCourse.value = byId.has(params.get('course') ?? '') || params.get('course') === 'reading' ? params.get('course')! : ''
  selectedType.value = typeLabels[params.get('type') ?? ''] ? params.get('type')! : ''
  scope.value = params.get('scope') === 'practice' ? 'practice' : 'all'
}
function clear() { query.value = ''; selectedCourse.value = ''; selectedType.value = ''; scope.value = 'all' }
watch(scope, () => { if (scope.value === 'practice' && selectedCourse.value === 'reading') selectedCourse.value = '' })
watch([query, selectedCourse, selectedType, scope], () => {
  page.value = 1
  if (!mounted) return
  const url = new URL(location.href)
  for (const [key, value] of [['q', query.value.trim()], ['course', selectedCourse.value], ['type', scope.value === 'practice' ? '' : selectedType.value], ['scope', scope.value === 'practice' ? 'practice' : '']]) {
    if (value) url.searchParams.set(key, value)
    else url.searchParams.delete(key)
  }
  history.replaceState(history.state, '', url.pathname + url.search + url.hash)
})
onMounted(() => { readUrl(); mounted = true; window.addEventListener('popstate', readUrl) })
onBeforeUnmount(() => window.removeEventListener('popstate', readUrl))
</script>

<template>
  <section class="resource-library" aria-label="课程资料检索">
    <form class="resource-search" role="search" @submit.prevent>
      <input v-model="query" type="search" maxlength="256" aria-label="检索资料" placeholder="搜索资料名称、课程、主题或作业…" />
      <button type="submit">检索</button>
    </form>
    <div class="resource-toolbar">
      <div class="resource-scopes" aria-label="资料范围">
        <button type="button" :aria-pressed="scope === 'all'" @click="scope = 'all'">全部资料</button>
        <button type="button" :aria-pressed="scope === 'practice'" @click="scope = 'practice'">Lab 与作业</button>
      </div>
      <select v-model="selectedCourse" aria-label="按课程筛选资料">
        <option value="">全部课程</option>
        <option v-for="course in courses" :key="course.id" :value="course.id">{{ course.shortTitle ?? course.title }}</option>
        <option v-if="scope !== 'practice'" value="reading">配套阅读</option>
      </select>
      <select v-if="scope !== 'practice'" v-model="selectedType" aria-label="按类型筛选资料">
        <option value="">全部类型</option>
        <option v-for="[type, label] in types" :key="type" :value="type">{{ label }}</option>
      </select>
      <button v-if="query || selectedCourse || selectedType || scope !== 'all'" class="resource-clear" type="button" @click="clear">清除筛选</button>
      <span class="resource-count" role="status">{{ filtered.length }} 条</span>
    </div>
    <p v-if="!filtered.length" class="resource-empty">没有找到匹配资料，请调整关键词或筛选条件。</p>
    <section v-for="group in groups" :key="group.id" class="resource-group" :aria-label="group.title">
      <header>
        <h2><a v-if="group.route" :href="withBase(group.route)">{{ group.title }}</a><span v-else>{{ group.title }}</span></h2>
        <span>{{ group.count }} 条</span>
        <button v-if="browsing && group.count > group.items.length" type="button" @click="selectedCourse = group.id">查看该课程资料 →</button>
      </header>
      <div class="resource-columns" aria-hidden="true"><span>资料名称</span><span>类型</span><span>关联讲次</span><span>来源</span></div>
      <div v-for="resource in group.items" :key="resource.url" class="resource-row">
        <a class="resource-title" :href="withBase(resource.url)" :title="`${titleOf(resource)}${resource.note ? ' — ' + resource.note : ''}`" target="_blank" rel="noreferrer">{{ titleOf(resource) }} <span aria-hidden="true">↗</span></a>
        <span class="resource-type">{{ typeLabels[typeOf(resource)] ?? '参考资料' }}</span>
        <div class="resource-context" :title="associations(resource).map(a => `${a.courseTitle} · ${a.lectureTitle}`).join('；')">
          <a v-if="associations(resource).length" :href="withBase(associations(resource)[0].route)">{{ associations(resource)[0].lectureTitle }}</a>
          <span v-else>配套阅读</span>
          <small v-if="associations(resource).length > 1"> +{{ associations(resource).length - 1 }}</small>
        </div>
        <div class="resource-source" :title="resource.url">
          <a v-if="resource.practiceSource" :href="resource.practiceSource" :title="`课程官网公布的作业入口：${resource.practiceSource}`" target="_blank" rel="noreferrer">{{ sourceOf(resource) }} · 官网</a>
          <span v-else>{{ sourceOf(resource) }}</span>
        </div>
      </div>
    </section>
    <nav v-if="!browsing && pageCount > 1" class="resource-pages" aria-label="资料结果分页">
      <button type="button" :disabled="page === 1" @click="page--">上一页</button>
      <span>{{ page }} / {{ pageCount }}</span>
      <button type="button" :disabled="page === pageCount" @click="page++">下一页</button>
    </nav>
  </section>
</template>

<style scoped>
.resource-library { margin: 16px 0 32px; }
.resource-search { display: flex; gap: 12px; align-items: center; }
.resource-search input { flex: 1; min-width: 0; padding: 8px 10px; border: 1px solid var(--ll-line); border-radius: 4px; color: var(--vp-c-text-1); background: var(--vp-c-bg); font: inherit; font-size: 14px; }
.resource-search button, .resource-clear, .resource-group header button, .resource-pages button { color: var(--vp-c-brand-1); font-size: 13px; }
.resource-toolbar { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 14px; padding: 10px 0; border-bottom: 1px solid var(--ll-line); font-size: 12px; }
.resource-scopes { display: flex; gap: 12px; }
.resource-scopes button { color: var(--vp-c-text-3); }
.resource-scopes button[aria-pressed="true"] { color: var(--vp-c-brand-1); text-decoration: underline; text-underline-offset: 5px; }
.resource-toolbar select { max-width: 220px; padding: 3px 20px 3px 6px; border: 1px solid var(--ll-line); border-radius: 3px; color: var(--vp-c-text-1); background: var(--vp-c-bg); font: inherit; appearance: auto; }
.resource-count { margin-left: auto; color: var(--vp-c-text-3); }
.resource-group { margin: 18px 0 22px; }
.resource-group header { display: flex; flex-wrap: wrap; align-items: baseline; gap: 10px; margin-bottom: 5px; }
.resource-group h2 { margin: 0; padding: 0; border: 0; font-size: 15px; line-height: 1.6; }
.resource-group h2 a { color: var(--vp-c-text-1); text-decoration: none; }
.resource-group header > span { color: var(--vp-c-text-3); font-size: 12px; }
.resource-group header button { margin-left: auto; }
.resource-columns, .resource-row { display: grid; grid-template-columns: minmax(0, 1fr) 70px minmax(100px, 170px) 105px; gap: 12px; align-items: center; }
.resource-columns { padding: 3px 0 5px; color: var(--vp-c-text-3); border-bottom: 1px solid var(--ll-line); font-size: 11px; }
.resource-row { min-height: 34px; padding: 6px 0; border-bottom: 1px solid var(--ll-line); }
.resource-title { min-width: 0; overflow-wrap: anywhere; font-size: 13px; line-height: 1.5; font-weight: 500; text-decoration: none; }
.resource-title > span { color: var(--vp-c-text-3); font-size: 11px; }
.resource-type, .resource-context, .resource-source { min-width: 0; color: var(--vp-c-text-3); font-size: 11px; line-height: 1.5; }
.resource-context a, .resource-source a { color: var(--vp-c-text-3); font-weight: 400; }
.resource-context { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.resource-source > span, .resource-source a { display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.resource-pages { display: flex; justify-content: center; gap: 18px; margin-top: 20px; font-size: 13px; }
.resource-pages button:disabled { color: var(--vp-c-text-3); cursor: default; }
.resource-empty { color: var(--vp-c-text-3); font-size: 14px; }
@media (max-width: 640px) {
  .resource-columns { display: none; }
  .resource-row { grid-template-columns: minmax(0, 1fr) auto; gap: 2px 10px; padding: 7px 0; }
  .resource-title { grid-column: 1 / -1; }
  .resource-type { grid-column: 2; grid-row: 2; }
  .resource-context { grid-column: 1; }
  .resource-source { display: flex; gap: 8px; grid-column: 1 / -1; }
  .resource-toolbar select { max-width: 100%; }
}
</style>
