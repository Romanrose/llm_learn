import { existsSync, mkdirSync, readFileSync, readdirSync, rmSync, writeFileSync } from 'node:fs'
import { dirname, extname, join, normalize, relative, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { parse } from 'yaml'

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), '../..')
const catalogRoot = join(repoRoot, 'website', 'catalog-data')
const outputRoot = join(repoRoot, 'website', 'generated')
const configGeneratedRoot = join(repoRoot, 'website', '.vitepress', 'generated')
const courseSettings = parse(readFileSync(join(repoRoot, 'website', 'course.yaml'), 'utf8'))

function collectYamlFiles(directory) {
  return readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const path = join(directory, entry.name)
    if (entry.isDirectory()) return collectYamlFiles(path)
    return /\.ya?ml$/i.test(entry.name) ? [path] : []
  })
}

function ensureParent(path) {
  mkdirSync(dirname(path), { recursive: true })
}

function write(path, content) {
  ensureParent(path)
  writeFileSync(path, content.trimStart(), 'utf8')
}

function frontmatter({ title, description = '', search = true, aside, outline, pageClass }) {
  const extra = [
    ...(aside === undefined ? [] : [`aside: ${aside}`]),
    ...(outline === undefined ? [] : [`outline: ${outline}`]),
    ...(pageClass ? [`pageClass: ${pageClass}`] : []),
  ].join('\n')
  return `---\ntitle: ${JSON.stringify(title)}\ndescription: ${JSON.stringify(description)}\nsearch: ${search}${extra ? `\n${extra}` : ''}\n---\n\n`
}

function statusLabel(status) {
  return ({
    updating: '持续更新',
    published: '已发布',
    draft: '草稿',
    scheduled: '课程表已同步',
    'resources-discovered': '资源待审核',
  })[status] ?? status
}

function resourceTypeLabel(type) {
  return ({
    slides: '讲义 / Slides',
    video: '视频',
    code: '代码',
    reference: '课程资料',
    paper: '论文',
    blog: '技术文章',
    docs: '文档',
    book: '书籍 / 教程',
  })[type] ?? type
}

function assignmentStateLabel(state) {
  return ({ out: '已发布', due: '截止' })[state] ?? state
}

function preparationLabel(state) {
  return ({
    'subtitle-ready': '字幕已准备',
    'needs-audio-authorization': '等待音频授权',
  })[state] ?? state
}

function itemStatusLabel(item) {
  if (item.generation?.state === 'draft-ready') return '草稿待校对'
  if (item.generation?.state === 'reviewed' || item.status === 'published') return '已发布'
  return item.preparation?.state ? preparationLabel(item.preparation.state) : statusLabel(item.status)
}

function vueProp(value) {
  return `'${JSON.stringify(value).replaceAll("'", '&#39;')}'`
}

function withoutMarkdownExtension(path) {
  return /\.md$/i.test(path) ? path.slice(0, -extname(path).length) : path
}

function normalizeOutputs(course, item) {
  const outputs = [...(item.outputs ?? [])]
  const transcriptEnSource = normalize(join(course.paths?.notes ?? `llm/${course.id}/notes`, item.id, 'transcript.en.md'))
  if (existsSync(resolve(repoRoot, transcriptEnSource)) && !outputs.some((output) => output.id === 'transcript-en')) {
    outputs.push({
      id: 'transcript-en',
      label: '英文逐字稿',
      source: transcriptEnSource,
      searchable: false,
      reviewStatus: 'source',
    })
  }
  const order = new Map([
    ['lecture-note', 0],
    ['blog', 1],
    ['transcript-zh', 2],
    ['transcript-en', 3],
  ])
  return outputs.sort((a, b) => (order.get(a.id) ?? 99) - (order.get(b.id) ?? 99))
}

function readSource(source, outputs) {
  const path = resolve(repoRoot, source)
  if (!path.startsWith(`${repoRoot}/`)) throw new Error(`Source must stay inside repository: ${source}`)
  if (!existsSync(path)) return `# 内容待生成\n\n尚未找到源文件：\`${source}\`。`
  const routeBySource = new Map(outputs.map((output) => [withoutMarkdownExtension(normalize(output.source)), output.route]))
  return readFileSync(path, 'utf8')
    .replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n/, '')
    .replace(/\]\(([^)]+)\)/g, (match, target) => {
      if (/^(?:[a-z]+:|#|\/)/i.test(target)) return match
      const [targetPath, anchor = ''] = target.split('#', 2)
      const resolvedTarget = withoutMarkdownExtension(normalize(join(dirname(source), decodeURI(targetPath))))
      const route = routeBySource.get(resolvedTarget)
      return route ? `](${route}${anchor ? `#${anchor}` : ''})` : match
    })
}

const records = collectYamlFiles(catalogRoot)
  .map((path) => ({ ...parse(readFileSync(path, 'utf8')), metadataFile: relative(repoRoot, path) }))
  .filter((record) => record.kind === 'course')
  .sort((a, b) => a.title.localeCompare(b.title, 'zh-CN'))

rmSync(outputRoot, { recursive: true, force: true })
mkdirSync(outputRoot, { recursive: true })
mkdirSync(configGeneratedRoot, { recursive: true })

const generatedCatalog = records.map((course) => {
  const items = [...(course.items ?? [])]
    .sort((a, b) => (a.order ?? 0) - (b.order ?? 0))
    .map((item) => {
      const route = `/generated/courses/${course.id}/${item.id}/`
      const outputs = normalizeOutputs(course, item).map((output) => ({
        ...output,
        route: `/generated/courses/${course.id}/${item.id}/${output.id}`,
      }))
      const tabs = [
        { id: 'overview', label: '课程简介', route: `${route}#content-overview` },
        ...outputs.map(({ id, label }) => ({ id, label, route: `${route}#content-${id}` })),
      ]
      const workspaceTabs = [
        { id: 'overview', label: '课程简介', available: true },
        ...[
          ['lecture-note', '课程笔记'],
          ['blog', 'Blog 解读'],
          ['transcript-zh', '中文逐字稿'],
          ['transcript-en', '英文逐字稿'],
        ].map(([id, label]) => ({ id, label, available: outputs.some((output) => output.id === id) })),
      ]
      const exportLinks = item.exports ?? []
      const lectureVideo = (item.official ?? []).find((link) => /youtu(?:\.be|be\.com)/.test(link.url))
      const learningResources = [...(item.resources ?? []), ...(item.readings ?? [])]
      const details = [
        ...(item.date ? [{ label: '日期', value: item.date }] : []),
        ...(item.instructors?.length ? [{ label: '讲师', value: item.instructors.join(' / ') }] : []),
        { label: '课程资料', value: `${learningResources.length} 项` },
        { label: '内容产物', value: `${outputs.length} 项` },
      ]

      for (const output of outputs) {
        const links = [
          ...(course.official ?? []).filter((link) => !/youtube\.com\/playlist/.test(link.url)),
          ...(item.official ?? []),
        ]
        const page = [
          frontmatter({
            title: `${course.shortTitle ?? course.title} · ${item.title} · ${output.label}`,
            description: item.subtitle ?? course.description,
            search: output.searchable !== false,
            aside: false,
            outline: false,
          }),
          `<CourseHeader eyebrow=${JSON.stringify(`${course.shortTitle ?? course.title} · Lecture ${item.order ?? ''}`)} title=${JSON.stringify(item.title)} courseRoute=${JSON.stringify(`/generated/courses/${course.id}/`)} description=${JSON.stringify(item.subtitle ?? '')} status=${JSON.stringify(itemStatusLabel(item))} :details=${vueProp(details)} :links=${vueProp([...links, ...exportLinks])} />`,
          ...(lectureVideo ? [`<LectureVideo title=${JSON.stringify(`Lecture ${item.order ?? ''} · ${item.title}`)} url=${JSON.stringify(lectureVideo.url)} />`] : []),
          `<CourseTabs active=${JSON.stringify(output.id)} :items=${vueProp(tabs)} />`,
          `<div class="source-note">本页由 <code>${output.source}</code> 自动生成；原始笔记位置保持不变。</div>`,
          readSource(output.source, outputs),
        ].join('\n\n')
        write(join(outputRoot, 'courses', course.id, item.id, `${output.id}.md`), page)
      }

      const assignmentRows = (item.assignments ?? []).map((assignment) => (
        `<div><span>${assignment.id}</span><strong>${assignmentStateLabel(assignment.state)}</strong></div>`
      )).join('\n')
      const lectureLinks = [...(course.official?.slice(0, 1) ?? []), ...(item.official ?? []), ...exportLinks]
      const resourceCards = learningResources.map((resource) => (
        `<a href="${resource.url}" target="_blank" rel="noreferrer"><strong>${resourceTypeLabel(resource.type)}</strong><span>${resource.label}</span><small>${resource.note ?? '打开链接'}</small><b>↗</b></a>`
      )).join('\n')
      const outputPanes = [
        ['lecture-note', '课程笔记'],
        ['blog', 'Blog 解读'],
        ['transcript-zh', '中文逐字稿'],
        ['transcript-en', '英文逐字稿'],
      ].map(([id, label]) => {
        const output = outputs.find((candidate) => candidate.id === id)
        return [
          `<section id="content-${id}" class="workspace-pane" data-workspace-pane="${id}" hidden>`,
          output ? readSource(output.source, outputs) : `## ${label}\n\n本讲的${label}尚未生成。`,
          '</section>',
        ].join('\n\n')
      }).join('\n\n')
      const lecturePage = [
        frontmatter({
          title: `${course.shortTitle ?? course.title} · Lecture ${item.order ?? ''} · ${item.title}`,
          description: item.subtitle ?? `${item.date ?? ''} ${item.instructors?.join(' / ') ?? ''}`.trim(),
          aside: false,
          outline: false,
          pageClass: 'lecture-workspace-page',
        }),
        `<LectureWorkspaceHero eyebrow=${JSON.stringify(`${course.shortTitle ?? course.title} · Lecture ${item.order ?? ''}`)} title=${JSON.stringify(item.title)} status=${JSON.stringify(itemStatusLabel(item))} courseRoute=${JSON.stringify(`/generated/courses/${course.id}/`)} videoUrl=${JSON.stringify(lectureVideo?.url ?? '')} :details=${vueProp(details)} :links=${vueProp(lectureLinks)} />`,
        `<LectureWorkspaceTabs :items=${vueProp(workspaceTabs)} />`,
        '<LectureWorkspaceOutline />',
        '<div class="workspace-panes">',
        '<section id="content-overview" class="workspace-pane is-active" data-workspace-pane="overview">',
        '## 课程简介',
        `<div class="workspace-course-intro">${item.overview ?? item.subtitle ?? `本讲由 ${item.instructors?.join(' / ') || '课程讲师'} 主讲，属于 ${course.shortTitle ?? course.title} 的第 ${item.order ?? ''} 讲。`}</div>`,
        '<section class="workspace-info-panel">',
        '<header class="workspace-info-panel__header"><span>COURSE MATERIALS</span><strong>官方资料与延伸阅读</strong></header>',
        resourceCards ? `<div class="workspace-resource-cards">\n${resourceCards}\n</div>` : '<p class="workspace-info-panel__empty">本讲的课程资料与延伸阅读尚未同步。</p>',
        '</section>',
        ...(assignmentRows ? [
          '<section class="workspace-info-panel">',
          '<header class="workspace-info-panel__header"><span>ASSIGNMENTS</span><strong>作业节点</strong></header>',
          `<div class="workspace-assignment-rows">\n${assignmentRows}\n</div>`,
          '</section>',
        ] : []),
        '</section>',
        outputPanes,
        '</div>',
      ].join('\n\n')
      write(join(outputRoot, 'courses', course.id, item.id, 'index.md'), lecturePage)

      return { ...item, route, outputs }
    })

  const playlist = (course.official ?? []).find((link) => /youtube\.com\/playlist/.test(link.url))
  const previewVideo = items
    .flatMap((item) => item.official ?? [])
    .find((link) => /youtu(?:\.be|be\.com)/.test(link.url))
  const firstLecture = items.find((item) => item.outputs.length)?.route ?? items[0]?.route
  const publishedCount = items.filter((item) => itemStatusLabel(item) === '已发布').length
  const outputCount = items.reduce((total, item) => total + item.outputs.length, 0)
  const referenceRoute = `/generated/courses/${course.id}/references/`
  const referenceGroups = items
    .filter((item) => item.readings?.length)
    .map((item) => ({ id: item.id, order: item.order, title: item.title, readings: item.readings }))
  const referenceCount = referenceGroups.reduce((total, group) => total + group.readings.length, 0)
  const uniqueReferenceCount = new Set(referenceGroups.flatMap((group) => group.readings.map((reading) => reading.url))).size
  const referenceGridItem = {
    id: 'references',
    order: 0,
    title: '课程参考资料',
    subtitle: '按课程目录汇总论文、技术文章、官方文档与代码仓库。',
    instructors: [],
    status: '持续更新',
    route: referenceRoute,
    resourceCount: uniqueReferenceCount,
    outputCount: 1,
    outputLabels: [`${uniqueReferenceCount} 项`],
  }
  const lectureGrid = [referenceGridItem, ...items.map((item) => ({
    id: item.id,
    order: item.order,
    date: item.date,
    title: item.title,
    subtitle: item.subtitle,
    instructors: item.instructors,
    status: itemStatusLabel(item),
    route: item.route,
    resourceCount: (item.resources?.length ?? 0) + (item.readings?.length ?? 0),
    outputCount: item.outputs.length,
    outputLabels: item.outputs.map((output) => output.label),
  }))]

  write(join(outputRoot, 'courses', course.id, 'references', 'index.md'), [
    frontmatter({
      title: `${course.shortTitle ?? course.title} · 课程参考资料`,
      description: `按课程目录整理的 ${uniqueReferenceCount} 条论文、技术文章、文档与代码。`,
      aside: false,
      outline: false,
      pageClass: 'course-reference-page',
    }),
    '# L00 · 课程参考资料',
    '本页按 CS336 的课程顺序汇总各讲涉及的论文、技术文章、官方文档、教程和代码仓库。每讲页面仍保留与本讲直接相关的资料入口。',
    `<CourseReferenceLibrary :groups=${vueProp(referenceGroups)} :total=${JSON.stringify(referenceCount)} :uniqueTotal=${JSON.stringify(uniqueReferenceCount)} />`,
  ].join('\n\n'))

  const overview = [
    frontmatter({ title: course.title, description: course.description, aside: false, outline: false }),
    `<CourseHero eyebrow=${JSON.stringify(`Stanford · Language Modeling from Scratch · ${course.year ?? ''}`)} title=${JSON.stringify(course.shortTitle ?? course.title)} description=${JSON.stringify(course.description)} status=${JSON.stringify(statusLabel(course.status))} startRoute=${JSON.stringify(firstLecture ?? '')} referenceRoute=${JSON.stringify(referenceRoute)} watchUrl=${JSON.stringify(playlist?.url ?? '')} previewUrl=${JSON.stringify(previewVideo?.url ?? '')} :details=${vueProp([{ label: '讲次', value: `${items.length} 讲` }, { label: '发布', value: `${publishedCount} 讲` }, { label: '内容', value: `${outputCount} 份` }, { label: '资料', value: `${uniqueReferenceCount} 条` }])} :links=${vueProp(course.official ?? [])} />`,
    '## 课程学习路径',
    lectureGrid.length ? `<LectureGrid :items=${vueProp(lectureGrid)} />` : '课程条目正在整理中。',
  ].join('\n\n')
  write(join(outputRoot, 'courses', course.id, 'index.md'), overview)

  return { ...course, referenceRoute, items }
})

write(join(outputRoot, 'catalog', 'index.md'), [
  frontmatter({ title: '知识地图', description: 'llm_learn 的课程与专题目录', aside: false, outline: false }),
  '# 知识地图',
  '课程、专题和论文通过元数据组织，原始文件仍保留在它们最自然的位置。',
  '<CourseMap />',
].join('\n\n'))

writeFileSync(join(configGeneratedRoot, 'catalog.json'), `${JSON.stringify(generatedCatalog, null, 2)}\n`, 'utf8')
writeFileSync(join(configGeneratedRoot, 'site.json'), `${JSON.stringify(courseSettings, null, 2)}\n`, 'utf8')
console.log(`Generated ${generatedCatalog.length} course(s) in website/generated`)
