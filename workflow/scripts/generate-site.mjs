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

function frontmatter({ title, description = '', search = true }) {
  return `---\ntitle: ${JSON.stringify(title)}\ndescription: ${JSON.stringify(description)}\nsearch: ${search}\n---\n\n`
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
  return ({ slides: '讲义 / Slides', video: '视频', code: '代码', reference: '课程资料' })[type] ?? type
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
      const outputs = (item.outputs ?? []).map((output) => ({
        ...output,
        route: `/generated/courses/${course.id}/${item.id}/${output.id}`,
      }))
      const tabs = [
        { id: 'overview', label: '课程资料', route },
        ...outputs.map(({ id, label, route }) => ({ id, label, route })),
      ]
      const exportLinks = item.exports ?? []
      const details = [
        ...(item.date ? [{ label: '日期', value: item.date }] : []),
        ...(item.instructors?.length ? [{ label: '讲师', value: item.instructors.join(' / ') }] : []),
        { label: '官方资料', value: `${item.resources?.length ?? 0} 项` },
        { label: '内容产物', value: `${outputs.length} 项` },
      ]

      for (const output of outputs) {
        const links = [...(course.official ?? []), ...(item.official ?? [])]
        const page = [
          frontmatter({
            title: `${course.shortTitle ?? course.title} · ${item.title} · ${output.label}`,
            description: item.subtitle ?? course.description,
            search: output.searchable !== false,
          }),
          `<CourseHeader eyebrow=${JSON.stringify(`${course.shortTitle ?? course.title} · Lecture ${item.order ?? ''}`)} title=${JSON.stringify(item.title)} description=${JSON.stringify(item.subtitle ?? '')} status=${JSON.stringify(itemStatusLabel(item))} :details=${vueProp(details)} :links=${vueProp([...links, ...exportLinks])} />`,
          `<CourseTabs active=${JSON.stringify(output.id)} :items=${vueProp(tabs)} />`,
          `<div class="source-note">本页由 <code>${output.source}</code> 自动生成；原始笔记位置保持不变。</div>`,
          readSource(output.source, outputs),
        ].join('\n\n')
        write(join(outputRoot, 'courses', course.id, item.id, `${output.id}.md`), page)
      }

      const resources = (item.resources ?? []).map((resource) => (
        `- [${resource.label}](${resource.url}) · ${resourceTypeLabel(resource.type)} · ${resource.status === 'approved' ? '已审核' : '待审核'}`
      )).join('\n')
      const outputLinks = outputs.map((output) => `- [${output.label}](${output.route}) · 来源：\`${output.source}\``).join('\n')
      const assignments = (item.assignments ?? []).map((assignment) => (
        `- ${assignment.id} · ${assignmentStateLabel(assignment.state)}`
      )).join('\n')
      const lectureLinks = [...(course.official?.slice(0, 1) ?? []), ...(item.official ?? []), ...exportLinks]
      const lecturePage = [
        frontmatter({
          title: `${course.shortTitle ?? course.title} · Lecture ${item.order ?? ''} · ${item.title}`,
          description: item.subtitle ?? `${item.date ?? ''} ${item.instructors?.join(' / ') ?? ''}`.trim(),
        }),
        `<CourseHeader eyebrow=${JSON.stringify(`${course.shortTitle ?? course.title} · Lecture ${item.order ?? ''}`)} title=${JSON.stringify(item.title)} description=${JSON.stringify(item.subtitle ?? '')} status=${JSON.stringify(itemStatusLabel(item))} :details=${vueProp(details)} :links=${vueProp(lectureLinks)} />`,
        `<CourseTabs active="overview" :items=${vueProp(tabs)} />`,
        ...(item.preparation ? [
          '## 自动化准备',
          `当前状态：**${preparationLabel(item.preparation.state)}**。来源清单：\`${item.preparation.manifest}\`。${item.preparation.state === 'subtitle-ready' ? '字幕已经提取并清洗，下一步生成中文逐字稿、讲义解读和 Blog 草稿。' : '视频没有可用字幕，下载音频并运行 ASR 前需要明确授权。'}`,
        ] : []),
        ...(item.generation ? [
          '## 内容生成',
          `当前状态：**${item.generation.state === 'draft-ready' ? '草稿待校对' : item.generation.state}**。生成清单：\`${item.generation.manifest}\`。`,
        ] : []),
        '## 官方资料',
        resources || '本讲的官方资料尚未同步。',
        '## 内容产物',
        outputLinks || '本讲已建立资料入口，逐字稿、讲义解读和 Blog 尚待生成。',
        ...(exportLinks.length ? ['## PDF 与 LaTeX', exportLinks.map((link) => `- [${link.label}](${link.url})`).join('\n')] : []),
        ...(assignments ? ['## 作业节点', assignments] : []),
      ].join('\n\n')
      write(join(outputRoot, 'courses', course.id, item.id, 'index.md'), lecturePage)

      return { ...item, route, outputs }
    })

  const officialLinks = (course.official ?? []).map((link) => `- [${link.label}](${link.url})`).join('\n')
  const lectureGrid = items.map((item) => ({
    id: item.id,
    order: item.order,
    date: item.date,
    title: item.title,
    subtitle: item.subtitle,
    instructors: item.instructors,
    status: itemStatusLabel(item),
    route: item.route,
    resourceCount: item.resources?.length ?? 0,
    outputCount: item.outputs.length,
    outputLabels: item.outputs.map((output) => output.label),
  }))
  const overview = [
    frontmatter({ title: course.title, description: course.description }),
    `<CourseHeader eyebrow=${JSON.stringify(`课程 · ${course.year ?? ''}`)} title=${JSON.stringify(course.title)} description=${JSON.stringify(course.description)} status=${JSON.stringify(statusLabel(course.status))} :links=${vueProp(course.official ?? [])} />`,
    '## 官方资源',
    officialLinks || '官方资源待审核。',
    '## 课程内容',
    lectureGrid.length ? `<LectureGrid :items=${vueProp(lectureGrid)} />` : '课程条目正在整理中。',
    '## 生成说明',
    `本课程页面由 \`${course.metadataFile}\` 生成。添加 Lecture 时只需更新元数据并提供对应源文件。`,
  ].join('\n\n')
  write(join(outputRoot, 'courses', course.id, 'index.md'), overview)

  return { ...course, items }
})

write(join(outputRoot, 'catalog', 'index.md'), [
  frontmatter({ title: '知识地图', description: 'llm_learn 的课程与专题目录' }),
  '# 知识地图',
  '课程、专题和论文通过元数据组织，原始文件仍保留在它们最自然的位置。',
  '<CourseMap />',
].join('\n\n'))

writeFileSync(join(configGeneratedRoot, 'catalog.json'), `${JSON.stringify(generatedCatalog, null, 2)}\n`, 'utf8')
writeFileSync(join(configGeneratedRoot, 'site.json'), `${JSON.stringify(courseSettings, null, 2)}\n`, 'utf8')
console.log(`Generated ${generatedCatalog.length} course(s) in website/generated`)
