import { existsSync, mkdirSync, readFileSync, readdirSync, rmSync, writeFileSync } from 'node:fs'
import { dirname, extname, join, normalize, relative, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { parse } from 'yaml'

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), '../..')
const catalogRoot = join(repoRoot, 'website', 'catalog-data')
const previewRootIndex = process.argv.indexOf('--preview-root')
if (previewRootIndex !== -1 && (!process.argv.includes('--review') || !process.argv[previewRootIndex + 1] || process.argv[previewRootIndex + 1].startsWith('--'))) {
  throw new Error('--preview-root 必须与 --review 和临时目录一起使用')
}
const websiteOutputRoot = previewRootIndex === -1 ? join(repoRoot, 'website') : resolve(process.argv[previewRootIndex + 1])
const outputRoot = join(websiteOutputRoot, 'generated')
const configGeneratedRoot = join(websiteOutputRoot, '.vitepress', 'generated')
const courseSettings = parse(readFileSync(join(repoRoot, 'website', 'course.yaml'), 'utf8'))
const reviewPreview = process.argv.includes('--review')

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
    'resources-approved': '官方资料已接入',
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

function learningMaterials(item) {
  const resources = new Map()
  const videos = (item.official ?? [])
    .filter((link) => /youtu(?:\.be|be\.com)|\.hosted\.panopto\.com/.test(link.url))
    .map((link) => ({ ...link, type: 'video', note: link.label }))
  for (const resource of [...(item.resources ?? []), ...(item.readings ?? []), ...videos]) {
    if (resource.url && !resources.has(resource.url)) resources.set(resource.url, resource)
  }
  return [...resources.values()]
}

function resourceHref(url) {
  return url.startsWith('/') && !url.startsWith('//')
    ? `${courseSettings.site.base.replace(/\/$/, '')}${url}` : url
}

function assignmentStateLabel(state) {
  return ({ out: '已发布', due: '截止' })[state] ?? state
}

function preparationLabel(state) {
  return ({
    'subtitle-ready': '字幕已准备',
    'needs-audio-authorization': '等待音频授权',
    'source-unavailable': '等待公开资料',
    'slides-ready': '讲义已准备',
  })[state] ?? state
}

function itemStatusLabel(item) {
  if (item.reviewPreview) return '待用户审核'
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
  const outputs = course.publishOutputs === false || item.publishOutputs === false ? [] : [...(item.outputs ?? [])]
  if (reviewPreview) {
    const references = resolve(repoRoot, course.paths.notes, item.id, 'references')
    const manifests = [
      ...['deepseek', 'deepseek-slides', 'codex'].map((provider) => join(references, provider, 'run.yaml')),
      ...(item.reviewCandidates ?? []).map((candidate) => resolve(repoRoot, candidate.manifest)),
    ]
    for (const manifestPath of new Set(manifests)) {
      if (!manifestPath.startsWith(`${repoRoot}/`) || !existsSync(manifestPath)) continue
      const manifest = parse(readFileSync(manifestPath, 'utf8'))
      if (manifest.state !== 'candidate-ready' || manifest.review?.state === 'approved') continue
      const directory = dirname(manifestPath)
      for (const [id, label, file, key] of [
        ['lecture-note', 'Lecture Note', 'note.md', 'note'], ['blog', 'Blog 解读', 'blog.md', 'blog'],
        ['transcript-zh', '中文逐字稿', 'transcript.zh-CN.md', 'transcriptZh'], ['transcript-en', '英文逐字稿', 'transcript.en.md', 'transcriptEn'],
      ]) {
        if (!manifest.outputs?.[key] || resolve(repoRoot, manifest.outputs[key]) !== join(directory, file)) continue
        if (outputs.some((output) => output.id === id) || !existsSync(join(directory, file))) continue
        outputs.push({ id, label, source: relative(repoRoot, join(directory, file)), searchable: false, reviewStatus: 'draft' })
      }
    }
  }
  const order = new Map([['lecture-note', 0], ['blog', 1], ['transcript-zh', 2], ['transcript-en', 3]])
  return outputs.sort((a, b) => (order.get(a.id) ?? 99) - (order.get(b.id) ?? 99))
}

function readSource(source, outputs) {
  const path = resolve(repoRoot, source)
  if (!path.startsWith(`${repoRoot}/`)) throw new Error(`Source must stay inside repository: ${source}`)
  if (!existsSync(path)) return `# 内容待生成\n\n尚未找到源文件：\`${source}\`。`
  const routeBySource = new Map(outputs.map((output) => [withoutMarkdownExtension(normalize(output.source)), output.route]))
  return readFileSync(path, 'utf8')
    // Caption unknown-word markers are text, not Vue/HTML elements.
    .replaceAll('<unk>', '&lt;unk&gt;')
    // Angle-bracket Markdown destinations must be normalized before bare links.
    .replace(/\]\(<(\/[^<>\s]+)>\)/g, ']($1)')
    .replace(/<(\/references\/[^<>\s]+)>/g, '[$1]($1)')
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
  const unitLabel = course.unitLabel ?? '讲'
  const items = [...(course.items ?? [])]
    .sort((a, b) => (a.order ?? 0) - (b.order ?? 0))
    .map((item) => {
      const unitHeading = item.unitLabel ?? course.unitLabel ?? 'Lecture'
      const unitNumber = item.displayOrder ?? item.order ?? ''
      const route = `/generated/courses/${course.id}/${item.id}/`
      const sourcesPath = course.paths?.notes ? join(repoRoot, course.paths.notes, item.id, 'sources.yaml') : null
      const sources = sourcesPath && existsSync(sourcesPath) ? parse(readFileSync(sourcesPath, 'utf8')) : {}
      const transcriptReferences = (item.transcriptReferences ?? []).filter((ref) => /^https?:\/\//.test(ref.url ?? ''))
      const referencesFor = (id) => transcriptReferences.filter((ref) => id === 'transcript-en' ? ref.language?.startsWith('en') : id === 'transcript-zh' ? ref.language?.startsWith('zh') : false)
      const transcriptReason = sources?.caption?.reason ?? ''
      const outputs = normalizeOutputs(course, item).map((output) => ({
        ...output,
        route: `/generated/courses/${course.id}/${item.id}/${output.id}`,
      }))
      item.reviewPreview = outputs.some((output) => output.reviewStatus === 'draft')
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
        ].map(([id, label]) => ({
          id,
          label: !outputs.some((output) => output.id === id) && referencesFor(id).length ? label.replace('逐字稿', '逐字资料') : label,
          available: outputs.some((output) => output.id === id) || referencesFor(id).length > 0,
        })),
      ]
      const exportLinks = item.exports ?? []
      const lectureVideo = (item.official ?? []).find((link) => /youtu(?:\.be|be\.com)|\.hosted\.panopto\.com/.test(link.url))
      const learningResources = learningMaterials(item)
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
          `<CourseHeader eyebrow=${JSON.stringify(`${course.shortTitle ?? course.title} · ${unitHeading} ${unitNumber}`)} title=${JSON.stringify(item.title)} courseRoute=${JSON.stringify(`/generated/courses/${course.id}/`)} description=${JSON.stringify(item.subtitle ?? '')} status=${JSON.stringify(itemStatusLabel(item))} :details=${vueProp(details)} :links=${vueProp([...links, ...exportLinks])} />`,
          ...(lectureVideo ? [`<LectureVideo title=${JSON.stringify(`${unitHeading} ${unitNumber} · ${item.title}`)} url=${JSON.stringify(lectureVideo.url)} />`] : []),
          `<CourseTabs active=${JSON.stringify(output.id)} :items=${vueProp(tabs)} />`,
          `<div class="source-note">本页由 <code>${output.source}</code> 自动生成；原始笔记位置保持不变。</div>`,
          readSource(output.source, outputs),
        ].join('\n\n')
        write(join(outputRoot, 'courses', course.id, item.id, `${output.id}.md`), page)
      }

      const assignmentRows = (item.assignments ?? []).map((assignment) => {
        const practice = (course.practice ?? []).find((entry) => entry.id === assignment.id)
        const link = practice
          ? `<a href="${practice.url}" target="_blank" rel="noreferrer">${practice.title}</a>`
          : `<span>${assignment.id}</span>`
        return `<div>${link}<strong>${assignmentStateLabel(assignment.state)}</strong></div>`
      }).join('\n')
      const lectureLinks = [...(course.official?.slice(0, 1) ?? []), ...(item.official ?? []), ...exportLinks]
      const resourceCards = learningResources.map((resource) => (
        `<a href="${resourceHref(resource.url)}" target="_blank" rel="noreferrer"><strong>${resourceTypeLabel(resource.type)}</strong><span>${resource.label}</span><small>${resource.note ?? '打开链接'}</small><b>↗</b></a>`
      )).join('\n')
      const outputPanes = [
        ['lecture-note', '课程笔记'],
        ['blog', 'Blog 解读'],
        ['transcript-zh', '中文逐字稿'],
        ['transcript-en', '英文逐字稿'],
      ].map(([id, label]) => {
        const output = outputs.find((candidate) => candidate.id === id)
        const references = referencesFor(id)
        const externalText = references.length ? [
          `## ${label.replace('逐字稿', '逐字资料入口')}`,
          '以下为官方或平台的外部字幕、逐字文本入口。补充材料的版本与原课不同；完整本地逐字稿尚未接入。',
          ...references.map((ref) => `### ${ref.label}\n\n[打开原始字幕或逐字文本](${ref.url})\n\n${ref.note ?? ''}`),
        ].join('\n\n') : ''
        return [
          `<section id="content-${id}" class="workspace-pane" data-workspace-pane="${id}" hidden>`,
          output ? readSource(output.source, outputs) : externalText || `## ${label}\n\n${id.startsWith('transcript-') && transcriptReason ? transcriptReason : `本单元的${label}尚未生成。`}`,
          '</section>',
        ].join('\n\n')
      }).join('\n\n')
      const lecturePage = [
        frontmatter({
          title: `${course.shortTitle ?? course.title} · ${unitHeading} ${unitNumber} · ${item.title}`,
          description: item.subtitle ?? `${item.date ?? ''} ${item.instructors?.join(' / ') ?? ''}`.trim(),
          aside: false,
          outline: false,
          pageClass: 'lecture-workspace-page',
        }),
        `<LectureWorkspaceHero eyebrow=${JSON.stringify(`${course.shortTitle ?? course.title} · ${unitHeading} ${unitNumber}`)} title=${JSON.stringify(item.title)} status=${JSON.stringify(itemStatusLabel(item))} courseRoute=${JSON.stringify(`/generated/courses/${course.id}/`)} videoUrl=${JSON.stringify(lectureVideo?.url ?? '')} :details=${vueProp(details)} :links=${vueProp(lectureLinks)} />`,
        `<LectureWorkspaceTabs :items=${vueProp(workspaceTabs)} />`,
        '<LectureWorkspaceOutline />',
        '<div class="workspace-panes">',
        '<section id="content-overview" class="workspace-pane is-active" data-workspace-pane="overview">',
        ...(item.reviewPreview ? [`> 本地审核预览：${outputs.filter((output) => output.reviewStatus === 'draft').map((output) => output.label).join('、')}为待审核候选稿，不代表正式发布内容；已有批准记录的正文保持原状态。`] : []),
        '## 课程简介',
        ...(transcriptReason ? [`> 逐字稿来源状态：${transcriptReason}`] : []),
        ...(transcriptReferences.length ? [`> 已接入 ${transcriptReferences.length} 项外部逐字资料，可在相应语言标签中查看。`] : []),
        `<div class="workspace-course-intro">${item.overview ?? item.subtitle ?? `本讲由 ${item.instructors?.join(' / ') || '课程讲师'} 主讲，属于 ${course.shortTitle ?? course.title} 的第 ${item.order ?? ''} ${unitLabel}。`}</div>`,
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
  const publishedCount = items.filter((item) => itemStatusLabel(item) === '已发布' || (reviewPreview && item.reviewPreview)).length
  const outputCount = items.reduce((total, item) => total + item.outputs.length, 0)
  const referenceRoute = `/generated/courses/${course.id}/references/`
  const referenceGroups = items
    .map((item) => ({ id: item.id, order: item.order, title: item.title, readings: learningMaterials(item) }))
    .filter((group) => group.readings.length)
  const referenceCount = referenceGroups.reduce((total, group) => total + group.readings.length, 0)
  const uniqueReferenceCount = new Set(referenceGroups.flatMap((group) => group.readings.map((reading) => reading.url))).size
  const referenceGridItem = {
    id: 'references',
    order: 0,
    title: '课程参考资料',
    subtitle: '按课程目录汇总讲义、视频、代码与延伸阅读。',
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
    resourceCount: learningMaterials(item).length,
    outputCount: item.outputs.length,
    outputLabels: item.outputs.map((output) => output.label),
  }))]

  write(join(outputRoot, 'courses', course.id, 'references', 'index.md'), [
    frontmatter({
      title: `${course.shortTitle ?? course.title} · 课程参考资料`,
      description: `按课程目录整理的 ${uniqueReferenceCount} 条讲义、视频、代码与延伸阅读。`,
      aside: false,
      outline: false,
      pageClass: 'course-reference-page',
    }),
    '# L00 · 课程参考资料',
    `本页按 ${course.shortTitle ?? course.title} 的课程顺序汇总各讲涉及的讲义、视频、代码与延伸阅读。每讲页面仍保留与本讲直接相关的资料入口。`,
    `<CourseReferenceLibrary :groups=${vueProp(referenceGroups)} :total=${JSON.stringify(referenceCount)} :uniqueTotal=${JSON.stringify(uniqueReferenceCount)} />`,
  ].join('\n\n'))

  const overview = [
    frontmatter({ title: course.title, description: course.description, aside: false, outline: false }),
    `<CourseHero eyebrow=${JSON.stringify(course.eyebrow ?? `${course.title} · ${course.year ?? ''}`)} title=${JSON.stringify(course.shortTitle ?? course.title)} description=${JSON.stringify(course.description)} status=${JSON.stringify(statusLabel(course.status))} startRoute=${JSON.stringify(firstLecture ?? '')} referenceRoute=${JSON.stringify(referenceRoute)} practiceRoute=${JSON.stringify(course.practice?.length ? '#lab-与作业' : '')} watchUrl=${JSON.stringify(playlist?.url ?? previewVideo?.url ?? '')} previewUrl=${JSON.stringify(previewVideo?.url ?? '')} :details=${vueProp([{ label: course.unitLabel ?? '讲次', value: `${items.length} ${unitLabel}` }, { label: reviewPreview ? '可审阅' : '发布', value: `${publishedCount} ${unitLabel}` }, { label: '内容', value: `${outputCount} 份` }, { label: '资料', value: `${uniqueReferenceCount} 条` }])} :links=${vueProp(course.official ?? [])} />`,
    ...(reviewPreview ? ['> 本地审核预览：候选内容标记为“待用户审核”；正式发布仍需人工审核并显式开放 outputs。'] : []),
    ...(course.practice?.length ? [
      '## Lab 与作业',
      '入口按本课程官网公布的作业登记；代码、题目版本及访问要求以原站为准。',
      ...course.practice.map((practice) => `- [${practice.title}](${practice.url})${/github\.com\//.test(practice.url) ? ' · GitHub' : ''}${practice.note ? ` — ${practice.note}` : ''} · [课程来源](${practice.source})`),
    ] : []),
    '## 课程学习路径',
    lectureGrid.length ? `<LectureGrid :items=${vueProp(lectureGrid)}${course.unitLabel ? ` unitLabel=${JSON.stringify(course.unitLabel)}` : ''}${course.learningModules ? ` :modules=${vueProp(course.learningModules)}` : ''} />` : '课程条目正在整理中。',
  ].join('\n\n')
  write(join(outputRoot, 'courses', course.id, 'index.md'), overview)

  return { ...course, referenceRoute, items }
})

write(join(outputRoot, 'catalog', 'index.md'), [
  frontmatter({ title: '课程目录', description: 'llm_learn 的课程学习目录', aside: false, outline: false }),
  '# 课程目录',
  '按学习方向浏览课程。',
  '<CourseMap />',
].join('\n\n'))

const resourceByUrl = new Map()
for (const course of generatedCatalog) {
  for (const item of course.items) {
    for (const material of learningMaterials(item)) {
      const resource = resourceByUrl.get(material.url) ?? { ...material, associations: [] }
      resource.associations.push({
        courseId: course.id,
        courseTitle: course.shortTitle ?? course.title,
        lectureId: item.id,
        lectureTitle: item.title,
        route: item.route,
        type: material.type ?? 'reference',
      })
      resourceByUrl.set(material.url, resource)
    }
  }
  for (const practice of course.practice ?? []) {
    const resource = resourceByUrl.get(practice.url) ?? { associations: [] }
    Object.assign(resource, { label: practice.title, url: practice.url, note: practice.note ?? '', type: 'assignment', practiceSource: practice.source })
    const associations = resource.associations.filter((association) => association.courseId === course.id)
    for (const association of associations) association.type = 'assignment'
    if (!associations.length) resource.associations.push({ courseId: course.id, courseTitle: course.shortTitle ?? course.title, lectureId: null, lectureTitle: 'Lab 与作业', route: `/generated/courses/${course.id}/#lab-与作业`, type: 'assignment' })
    resourceByUrl.set(practice.url, resource)
  }
}
for (const collection of courseSettings.referenceCollections ?? []) {
  if (!resourceByUrl.has(collection.route)) {
    resourceByUrl.set(collection.route, {
      label: collection.title,
      url: collection.route,
      note: collection.description,
      type: 'collection',
      associations: [],
    })
  }
}
write(join(outputRoot, 'resources', 'index.md'), [
  frontmatter({ title: '资料库', description: '按课程和类型查找讲义、视频、代码与延伸阅读', aside: false, outline: false, pageClass: 'course-reference-page' }),
  '# 资料库',
  '检索课程资料，或直接查看各课程官网公布的 Lab 与作业。',
  '<ResourceLibrary />',
].join('\n\n'))

writeFileSync(join(configGeneratedRoot, 'resources.json'), `${JSON.stringify([...resourceByUrl.values()], null, 2)}\n`, 'utf8')
writeFileSync(join(configGeneratedRoot, 'catalog.json'), `${JSON.stringify(generatedCatalog, null, 2)}\n`, 'utf8')
writeFileSync(join(configGeneratedRoot, 'site.json'), `${JSON.stringify(courseSettings, null, 2)}\n`, 'utf8')
console.log(`Generated ${generatedCatalog.length} course(s) in website/generated`)
