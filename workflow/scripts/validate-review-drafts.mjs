#!/usr/bin/env node
import { createHash } from 'node:crypto'
import { existsSync, readFileSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { parse, stringify } from 'yaml'

// Structural checks only. This does not approve or publish generated content.
const [courseId, ...ids] = process.argv.slice(2)
if (!courseId || !ids.length) throw Error('用法：node workflow/scripts/validate-review-drafts.mjs <course-id> <lecture-id...>')
const course = parse(readFileSync(`website/catalog-data/courses/${courseId}.yaml`, 'utf8'))
const read = p => existsSync(p) ? readFileSync(p, 'utf8') : ''
const stamps = s => [...s.matchAll(/^\[([\d:.]+)\]/gm)].map(x => x[1])
const seconds = s => s.split(':').reduce((n, x) => n * 60 + Number(x), 0)
let failed = false
for (const id of ids) {
  const dir = join(course.paths.notes, id)
  const candidate = join(dir, 'references/deepseek')
  const manifest = parse(read(join(candidate, 'run.yaml')))
  const errors = []; const warnings = []
  if (manifest?.state !== 'candidate-ready') errors.push('候选稿未完成')
  const en = read(join(candidate, 'transcript.en.md'))
  const zh = read(join(candidate, 'transcript.zh-CN.md'))
  const note = read(join(candidate, 'note.md'))
  const blog = read(join(candidate, 'blog.md'))
  const sourceEn = read(join(dir, 'transcript.en.md'))
  const slides = read(join(dir, 'references/source/slides.md'))
  const source = parse(read(join(dir, 'sources.yaml'))) ?? {}
  const hash = createHash('sha256').update(sourceEn + slides).digest('hex')
  if (hash !== manifest?.inputHash) errors.push('来源已变更，需要重新核对候选稿')
  if (!note || !blog) errors.push('Note 或 Blog 缺失')
  const a = stamps(en); const b = stamps(zh)
  let coverage = null
  if (manifest?.evidenceMode !== 'slides-only') {
    if (!a.length || !b.length) errors.push('英文或中文逐字稿缺失时间戳')
    if (JSON.stringify(a) !== JSON.stringify(b)) errors.push('中英文段落时间戳未逐项对齐')
    if (en !== sourceEn) errors.push('候选英文稿与来源稿不一致')
    if (a.some((s, i) => i > 0 && seconds(s) <= seconds(a[i - 1]))) errors.push('时间戳不严格递增')
    if (zh.length < en.length * 0.28) errors.push('中文翻译长度异常')
    if (seconds(a[0] ?? '0') > 10) warnings.push('字幕首段晚于视频开始 10 秒，需回听核对')
    const gaps = a.slice(1).map((s, i) => seconds(s) - seconds(a[i]))
    if (gaps.some(x => x > 180)) warnings.push('存在超过三分钟的字幕间隔，需回听核对')
    if (source.video?.durationSeconds && a.length) {
      coverage = Math.round(seconds(a.at(-1)) / source.video.durationSeconds * 1000) / 1000
      if (coverage < 0.94) errors.push('字幕末段尚未覆盖视频尾部 94%')
    }
  } else if (en || zh) errors.push('Slides-only 候选稿不应伪造逐字稿')
  const maxSlide = [...slides.matchAll(/^## Slide (\d+)/gm)].length
  for (const [label, text] of [['Note', note], ['Blog', blog]]) {
    if (!/^# /m.test(text) || !text.includes('待审核候选稿')) errors.push(`${label} 缺少候选稿声明`)
    if (stamps(text).length) errors.push(`${label} 错用了逐字稿段首时间戳`)
    const pages = [...text.matchAll(/Slides?\s*第\s*(\d+)/gi)].map(x => Number(x[1]))
    if (!maxSlide && pages.length) errors.push(`${label} 在没有 Slides 时引用页码`)
    if (pages.some(x => x > maxSlide || x < 1)) errors.push(`${label} 引用的 Slides 页码超出来源`)
  }
  for (const text of [en, zh, note, blog]) {
    if (/\/Users\/|127\.0\.0\.1|localhost|sk-[A-Za-z0-9]{20,}/.test(text)) errors.push('正文存在本地地址或疑似密钥')
  }
  const result = { schemaVersion: 1, checkedAt: new Date().toISOString(), course: courseId, lecture: id,
    state: errors.length ? 'failed' : 'structure-passed', reviewState: 'pending', evidenceMode: manifest?.evidenceMode,
    inputHash: hash, counts: { englishParagraphs: a.length, chineseParagraphs: b.length, slides: maxSlide },
    timeline: a.length ? { first: a[0], last: a.at(-1), durationSeconds: source.video?.durationSeconds, lastParagraphToDurationRatio: coverage } : null,
    errors, warnings, humanChecksRequired: ['字幕错词与专名', '中文语义完整性与术语一致性', '公式与图示', '引用支持论点', 'Note / Blog 来源忠实性'],
    limitation: '段落与时间戳对齐不证明语义翻译正确；未进行完整视频回听或人工内容审核。' }
  writeFileSync(join(candidate, 'checks.yaml'), stringify(result, { lineWidth: 0 }))
  console.log(`${courseId}/${id}: ${result.state} · EN/ZH ${a.length}/${b.length} · Slides ${maxSlide}`)
  for (const message of [...errors, ...warnings]) console.log(`  ${message}`)
  failed ||= errors.length > 0
}
if (failed) process.exitCode = 1
