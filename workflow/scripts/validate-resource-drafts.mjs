#!/usr/bin/env node
import { existsSync, readFileSync, writeFileSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { parse, stringify } from 'yaml'

// Checks resource-based candidate drafts without approving or publishing them.
const root = resolve(dirname(fileURLToPath(import.meta.url)), '../..')
const courseIds = process.argv.slice(2)
if (!courseIds.length) throw Error('用法：node workflow/scripts/validate-resource-drafts.mjs <course-id...>')
const read = path => existsSync(path) ? readFileSync(path, 'utf8') : ''
let failed = false
for (const courseId of courseIds) {
  const course = parse(read(join(root, 'website/catalog-data/courses', `${courseId}.yaml`)))
  if (!course?.items) throw Error(`课程不存在：${courseId}`)
  const summary = { course: courseId, units: course.items.length, notes: 0, blogs: 0, transcripts: 0, failed: 0 }
  for (const item of course.items) {
    const unitDir = join(root, course.paths.notes, item.id)
    const candidate = item.generation?.manifest ? dirname(resolve(root, item.generation.manifest)) : join(unitDir, 'references/codex')
    const manifest = parse(read(join(candidate, 'run.yaml'))) ?? {}
    const sourcesText = read(join(unitDir, 'sources.yaml'))
    const sources = parse(sourcesText) ?? {}
    const errors = []
    const warnings = []
    if (manifest.state !== 'candidate-ready') errors.push('候选稿尚未完成')
    if (manifest.provider !== 'codex') errors.push('候选稿 provider 不一致')
    const approved = manifest.review?.state === 'approved'
    if (!approved && manifest.review?.state !== 'pending') errors.push('候选稿缺少审核状态')
    if (approved && !manifest.review?.authorization) errors.push('已批准稿缺少用户授权记录')
    if (!sourcesText || !/https?:\/\//.test(sourcesText)) errors.push('缺少可追溯的来源链接')
    if (!approved && (course.publishOutputs !== false || item.outputs?.length)) errors.push('未批准候选稿不得直接发布')
    if (approved && (!item.outputs?.length || item.outputs.some(output => !existsSync(resolve(root, output.source))))) errors.push('已批准稿缺少正式输出')
    for (const kind of ['note', 'blog']) {
      const text = read(join(candidate, `${kind}.md`))
      if (!text.trim()) errors.push(`${kind} 缺失`)
      const declaredPath = manifest.outputs?.[kind]
      if (!declaredPath || resolve(root, declaredPath) !== join(candidate, `${kind}.md`)) errors.push(`${kind} 输出路径与 manifest 不一致`)
      else {
        summary[kind === 'note' ? 'notes' : 'blogs']++
        if (!/^# /m.test(text) || !text.includes('待审核候选稿')) errors.push(`${kind} 缺少标题或候选稿声明`)
        if (!/\]\(https?:\/\//.test(text)) errors.push(`${kind} 缺少来源链接`)
        if (/^\[\d{2}:\d{2}/m.test(text)) errors.push(`${kind} 错用了逐字稿段首时间戳`)
        if (/\/Users\/|127\.0\.0\.1|localhost|sk-[A-Za-z0-9]{20,}/.test(text)) errors.push(`${kind} 包含本地地址或疑似凭据`)
        for (const match of text.matchAll(/\]\(([^)]+)\)/g)) {
          const target = match[1].split('#')[0]
          if (target && !/^(?:[a-z]+:|\/)/i.test(target) && !existsSync(resolve(candidate, target))) errors.push(`${kind} 相对链接不存在：${target}`)
        }
        if (text.length < 1000) warnings.push(`${kind} 内容较短，请人工检查教学深度`)
      }
    }
    const en = manifest.outputs?.transcriptEn ? read(join(candidate, 'transcript.en.md')) : ''
    const zh = manifest.outputs?.transcriptZh ? read(join(candidate, 'transcript.zh-CN.md')) : ''
    if (en || zh) {
      summary.transcripts++
      if (/reading|assignment|public-outline/.test(manifest.evidenceMode ?? '')) errors.push('阅读或作业来源不能充当课堂逐字稿')
      const stamps = text => [...text.matchAll(/^\[([\d:.]+)\]/gm)].map(x => x[1])
      const a = stamps(en), b = stamps(zh)
      if (!a.length || !b.length || JSON.stringify(a) !== JSON.stringify(b)) errors.push('中英文逐字稿缺少对齐时间戳')
      if (!sources.video?.url) errors.push('逐字稿缺少视频来源')
      warnings.push('时间戳对齐不证明内容完整；需人工回听和语义校对')
    } else warnings.push('未取得课堂字幕；没有生成逐字稿')
    const state = errors.length ? 'failed' : 'structure-passed'
    const result = { schemaVersion: 1, checkedAt: new Date().toISOString(), course: courseId, unit: item.id,
      state, reviewState: approved ? 'approved' : 'pending', evidenceMode: manifest.evidenceMode, errors, warnings,
      humanChecksRequired: ['来源确实支持论点', '课程版本与单元归属', '示例正确性与补充解释边界', '教学深度与术语'],
      limitation: '结构检查不等同于人工内容审核，不授权发布。' }
    if (existsSync(candidate)) writeFileSync(join(candidate, 'checks.yaml'), stringify(result))
    if (errors.length) { failed = true; summary.failed++; console.error(`${courseId}/${item.id}: ${errors.join('；')}`) }
  }
  console.log(JSON.stringify(summary))
}
if (failed) process.exitCode = 1
