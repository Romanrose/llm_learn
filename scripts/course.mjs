#!/usr/bin/env node

import './load-env.mjs'
import { createHash } from 'node:crypto'
import { execFile, spawn } from 'node:child_process'
import { copyFileSync, existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { basename, dirname, extname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { promisify } from 'node:util'
import { parse, stringify } from 'yaml'
import { krillinAiArtifact, runKrillinAiSubtitle, srtToTranscriptBody } from './adapters/krillinai.mjs'

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const catalogRoot = join(repoRoot, 'catalog', 'courses')
const reviewRoot = join(repoRoot, 'catalog', 'reviews')
const userAgent = 'llm_learn-course/0.1 (+https://github.com/Romanrose/llm_learn)'
const execFileAsync = promisify(execFile)
const localYtDlp = process.env.COURSE_YT_DLP ?? join(repoRoot, 'workflow', 'video', 'transcript-pipeline', '.venv', 'bin', 'yt-dlp')
const subtitleTool = process.env.COURSE_SUBTITLE_TOOL ?? '/Users/romanrose/.codex/skills/video-subtitle-transcript/scripts/subtitle_transcript.py'
const generatorCli = process.env.COURSE_GENERATOR ?? '/opt/homebrew/bin/codex'

function usage(exitCode = 0) {
  console.log(`course — 课程资源进入知识库前的发现与审核工具

用法：
  course sync <course-id>
  course prepare <course-id> <lecture-id>
  course transcript <course-id> <lecture-id> --engine krillinai [--dry-run] [--caption-source any|manual|auto|whisper] [--allow-audio-download] [--overwrite]
  course generate <course-id> <lecture-id> [--provider codex-cli|deepseek] [--run]
  course validate <course-id> <lecture-id> [--provider deepseek]
  course promote <course-id> <lecture-id> [--provider deepseek] --reviewed [--overwrite]
  course discover <course-id>
  course approve <course-id> <resource-id...>
  course approve <course-id> --all
  course ingest <course-id> [--download]
  course status <course-id>

通过 npm 调用：npm run course -- <command> ...`)
  process.exitCode = exitCode
}

function loadCourse(courseId) {
  const path = join(catalogRoot, `${courseId}.yaml`)
  if (!existsSync(path)) throw new Error(`找不到课程配置：catalog/courses/${courseId}.yaml`)
  return { path, data: parse(readFileSync(path, 'utf8')) }
}

function reviewPath(courseId) {
  return join(reviewRoot, `${courseId}.resources.yaml`)
}

function loadReview(courseId) {
  const path = reviewPath(courseId)
  if (!existsSync(path)) throw new Error(`尚无候选清单，请先运行：course discover ${courseId}`)
  return { path, data: parse(readFileSync(path, 'utf8')) }
}

function writeYaml(path, value) {
  mkdirSync(dirname(path), { recursive: true })
  writeFileSync(path, stringify(value, { lineWidth: 0 }), 'utf8')
}

function relativeToRepo(path) {
  return path.slice(repoRoot.length + 1)
}

function courseItem(course, lectureId) {
  const item = (course.items ?? []).find((candidate) => candidate.id === lectureId)
  if (!item) throw new Error(`课程 ${course.id} 中找不到 ${lectureId}`)
  return item
}

function courseLabel(course) {
  return course.title ?? course.shortTitle ?? course.id
}

function lectureLabel(course, item) {
  return `${courseLabel(course)} Lecture ${item.order}「${item.title}」`
}

function executable(path, label) {
  if (!existsSync(path)) throw new Error(`找不到${label}：${path}`)
  return path
}

async function ytDlpJson(args) {
  const binary = executable(localYtDlp, '本地 yt-dlp')
  const { stdout } = await execFileAsync(binary, args, { timeout: 60_000, maxBuffer: 30 * 1024 * 1024 })
  return JSON.parse(stdout)
}

function chooseCaption(metadata) {
  const priorities = ['en-US', 'en', 'zh-Hans', 'zh-CN', 'zh']
  for (const [kind, tracks] of [['manual', metadata.subtitles], ['auto', metadata.automatic_captions]]) {
    for (const language of priorities) {
      if (tracks?.[language]?.length) return { kind, language }
    }
  }
  return null
}

function mergeTimestampedTranscript(markdown, { title, videoUrl, subtitle }) {
  const timestampPattern = /^\[((?:\d{2}:)?\d{2}:\d{2}(?:[.,]\d+)?|\d{2}:\d{2}(?:[.,]\d+)?)\]\s*(.*)$/
  const cues = []
  for (const line of markdown.split(/\r?\n/)) {
    const match = line.match(timestampPattern)
    if (!match) continue
    const text = match[2].replace(/\s+/g, ' ').trim()
    if (text) cues.push({ timestamp: formatTranscriptTimestamp(match[1]), text })
  }
  const paragraphs = groupTimestampBlocks(cues).map((group) => `[${group[0].timestamp}] ${group.map((cue) => cue.text).join(' ')}`)
  if (!paragraphs.length) throw new Error('字幕清洗后没有找到带时间戳的正文')
  return [
    `# ${title}`,
    '',
    `- 视频：[官方视频](${videoUrl})`,
    `- 字幕：${subtitle}`,
    '- 处理：连续字幕合并为自然段；每段保留首条字幕的起始时间戳',
    '- 状态：原语言字幕稿，待校对',
    '',
    '---',
    '',
    '## 正文',
    '',
    paragraphs.join('\n\n'),
    '',
  ].join('\n')
}

function formatTranscriptTimestamp(raw) {
  const normalized = raw.replace(',', '.')
  const parts = normalized.split(':')
  if (parts.length === 2) return normalized
  const [hours, minutes, seconds] = parts
  if (hours === '00') return `${minutes}:${seconds}`
  return normalized
}

function timestampParagraphBlocks(markdown) {
  return transcriptBody(markdown).split(/\n\s*\n/).map((block) => {
    const match = block.match(/^(\[[^\]]+\])\s*([\s\S]*)$/)
    return match ? { timestamp: match[1].slice(1, -1), text: match[2].replace(/\s+/g, ' ').trim() } : null
  }).filter(Boolean)
}

function groupTimestampBlocks(blocks) {
  const groups = []
  let current = []
  for (const block of blocks) {
    const currentLength = current.reduce((sum, item) => sum + item.text.length, 0)
    const shouldBreak = current.length > 0 && (
      currentLength + block.text.length + 1 > 380 ||
      (currentLength >= 250 && /[.!?。！？]$/.test(current.at(-1).text))
    )
    if (shouldBreak) {
      groups.push(current)
      current = []
    }
    current.push(block)
  }
  if (current.length) groups.push(current)
  return groups
}

function renderTimestampGroups(markdown, groups, separator) {
  const heading = markdown.match(/^## 正文\s*$/m)
  if (!heading) throw new Error('逐字稿缺少 ## 正文标题')
  const header = markdown.slice(0, heading.index + heading[0].length).trimEnd()
  const body = groups.map((group) => `[${group[0].timestamp}] ${group.map((item) => item.text).join(separator)}`).join('\n\n')
  return `${header}\n\n${body}\n`
}

function reflowAlignedTranscripts(englishMarkdown, chineseMarkdown) {
  const englishBlocks = timestampParagraphBlocks(englishMarkdown)
  const chineseBlocks = timestampParagraphBlocks(chineseMarkdown)
  if (englishBlocks.length !== chineseBlocks.length) throw new Error('中英文时间戳数量不一致，无法重新合并段落')
  const chineseGroups = groupTimestampBlocks(chineseBlocks)
  let offset = 0
  const englishGroups = chineseGroups.map((group) => {
    const selected = englishBlocks.slice(offset, offset + group.length)
    offset += group.length
    return selected
  })
  return {
    english: renderTimestampGroups(englishMarkdown, englishGroups, ' '),
    chinese: renderTimestampGroups(chineseMarkdown, chineseGroups, ''),
  }
}

async function playlistVideo(course, item) {
  const directVideo = (item.official ?? []).find((link) => /youtu(?:\.be|be\.com)/.test(link.url))
  const playlist = (course.official ?? []).find((link) => /youtube\.com\/playlist/.test(link.url))
  if (!playlist && directVideo) return { url: directVideo.url, playlist: null, playlistIndex: null }
  if (!playlist) throw new Error('课程配置中没有找到 YouTube 播放列表或 Lecture 视频')
  const data = await ytDlpJson(['--flat-playlist', '--dump-single-json', playlist.url])
  const lecturePattern = new RegExp(`\\bLecture\\s+${item.order}\\s*:`, 'i')
  const entryIndex = (data.entries ?? []).findIndex((entry) => lecturePattern.test(entry.title ?? ''))
  if (entryIndex === -1 && directVideo) return { url: directVideo.url, playlist: playlist.url, playlistIndex: null }
  if (entryIndex === -1) throw new Error(`播放列表中没有匹配到 Lecture ${item.order}`)
  const entry = data.entries[entryIndex]
  return {
    url: `https://www.youtube.com/watch?v=${entry.id}`,
    playlist: playlist.url,
    playlistIndex: entryIndex + 1,
  }
}

async function prepare(courseId, lectureId, args) {
  if (!lectureId || lectureId.startsWith('--')) throw new Error('用法：course prepare <course-id> <lecture-id>')
  const { path: coursePath, data: course } = loadCourse(courseId)
  const item = courseItem(course, lectureId)
  const lectureDirectory = lectureNotesDirectory(course, item)
  mkdirSync(lectureDirectory, { recursive: true })

  const located = await playlistVideo(course, item)
  const metadata = await ytDlpJson(['--skip-download', '--dump-single-json', located.url])
  const caption = chooseCaption(metadata)
  const transcriptPath = join(lectureDirectory, 'transcript.en.md')
  const manifestPath = join(lectureDirectory, 'sources.yaml')
  const preparedAt = new Date().toISOString()
  const baseManifest = {
    schemaVersion: 1,
    course: courseId,
    lecture: lectureId,
    title: item.title,
    preparedAt,
    video: {
      id: metadata.id,
      title: metadata.title,
      url: located.url,
      playlist: located.playlist,
      playlistIndex: located.playlistIndex,
      channel: metadata.channel ?? metadata.uploader,
      durationSeconds: metadata.duration,
    },
    materials: item.resources ?? [],
  }

  if (!caption) {
    writeYaml(manifestPath, {
      ...baseManifest,
      state: 'needs-audio-authorization',
      caption: { state: 'unavailable' },
    })
    item.preparation = { state: 'needs-audio-authorization', manifest: relativeToRepo(manifestPath), preparedAt }
    writeYaml(coursePath, course)
    console.log(`未发现字幕；已写入清单：${relativeToRepo(manifestPath)}`)
    console.log('下一步需要用户明确授权后才能下载音频并运行 ASR。')
    return
  }

  const tool = executable(subtitleTool, '字幕清洗工具')
  const pythonPath = join(repoRoot, 'workflow', 'video', 'transcript-pipeline', '.venv', 'bin', 'python')
  const executablePython = executable(pythonPath, '字幕环境 Python')
  await execFileAsync(executablePython, [
    tool,
    located.url,
    '--output', transcriptPath,
    '--langs', `${caption.language},en-US,en,zh-Hans,zh-CN,zh`,
    '--with-timestamps',
  ], {
    timeout: 120_000,
    maxBuffer: 20 * 1024 * 1024,
    env: { ...process.env, PATH: `${dirname(localYtDlp)}:${process.env.PATH ?? ''}` },
  })

  const rawTranscript = readFileSync(transcriptPath, 'utf8')
  const transcript = mergeTimestampedTranscript(rawTranscript, {
    title: `${course.shortTitle ?? course.title} · Lecture ${item.order} · ${item.title}`,
    videoUrl: located.url,
    subtitle: `${caption.language} · ${caption.kind === 'manual' ? 'manual captions' : 'auto captions'}`,
  })
  writeFileSync(transcriptPath, transcript, 'utf8')
  writeYaml(manifestPath, {
    ...baseManifest,
    state: 'subtitle-ready',
    caption: {
      state: 'extracted',
      kind: caption.kind,
      language: caption.language,
      transcript: relativeToRepo(transcriptPath),
      processor: 'video-subtitle-transcript',
    },
  })

  const videoLink = { label: '课程视频', url: located.url }
  item.official = [videoLink, ...(item.official ?? []).filter((link) => link.url !== located.url)]
  item.preparation = { state: 'subtitle-ready', manifest: relativeToRepo(manifestPath), preparedAt }
  writeYaml(coursePath, course)
  console.log(`Lecture 已准备：${lectureId}`)
  console.log(`视频：${located.url}`)
  console.log(`字幕：${caption.language} (${caption.kind})`)
  console.log(`逐字稿：${relativeToRepo(transcriptPath)}`)
  console.log(`来源清单：${relativeToRepo(manifestPath)}`)
}

function coursePath(course, key, fallback) {
  const path = resolve(repoRoot, course.paths?.[key] ?? fallback)
  if (!path.startsWith(`${repoRoot}/`)) throw new Error(`paths.${key} 必须位于仓库内部`)
  return path
}

function lectureNotesDirectory(course, item) {
  const notesRoot = coursePath(course, 'notes', `llm/${course.id}/notes`)
  return join(notesRoot, item.id)
}

function optionValue(args, option, fallback) {
  const index = args.indexOf(option)
  if (index === -1) return fallback
  const value = args[index + 1]
  if (!value || value.startsWith('--')) throw new Error(`${option} 需要一个值`)
  return value
}

function candidateTranscriptMarkdown({ course, item, languageLabel, videoUrl, srtPath, body }) {
  return [
    `# ${course.shortTitle ?? course.title} · Lecture ${item.order} · ${item.title}｜${languageLabel}候选逐字稿`,
    '',
    `- 视频：${videoUrl}`,
    `- 字幕引擎：KrillinAI（来源 SRT：${relativeToRepo(srtPath)}）`,
    '- 状态：候选稿，尚未采纳为正式逐字稿',
    '',
    body,
    '',
  ].join('\n')
}

async function transcript(courseId, lectureId, args) {
  if (!lectureId || lectureId.startsWith('--')) throw new Error('用法：course transcript <course-id> <lecture-id> --engine krillinai')
  const engine = optionValue(args, '--engine', null)
  if (engine !== 'krillinai') throw new Error('当前仅支持：--engine krillinai')
  const { data: course } = loadCourse(courseId)
  const item = courseItem(course, lectureId)
  const transcriptConfig = course.transcript ?? {}
  const originLanguage = optionValue(args, '--origin-lang', transcriptConfig.originLanguage ?? 'en')
  const targetLanguage = optionValue(args, '--target-lang', transcriptConfig.targetLanguage ?? 'zh_cn')
  const captionSource = optionValue(args, '--caption-source', transcriptConfig.captionSource ?? 'any')
  if (!['any', 'manual', 'auto', 'whisper'].includes(captionSource)) {
    throw new Error('--caption-source 必须是 any、manual、auto 或 whisper')
  }
  const dryRun = args.includes('--dry-run')
  if (!dryRun && ['any', 'whisper'].includes(captionSource) && !args.includes('--allow-audio-download')) {
    throw new Error(`${captionSource} 可能回退到音频下载/ASR；明确授权后增加 --allow-audio-download，或改用 --caption-source manual|auto`)
  }
  const lectureDirectory = lectureNotesDirectory(course, item)
  const candidateDirectory = join(lectureDirectory, 'references', 'krillinai')
  const workdir = join(repoRoot, 'var', 'krillinai', courseId, lectureId)
  const outputs = [
    'origin_language_srt.srt',
    'target_language_srt.srt',
    'transcript.en.md',
    'transcript.zh-CN.md',
    'run.yaml',
  ].map((name) => join(candidateDirectory, name))
  if (!dryRun && !args.includes('--overwrite') && outputs.some(existsSync)) {
    throw new Error(`候选稿已存在：${relativeToRepo(candidateDirectory)}；确认覆盖后增加 --overwrite`)
  }
  const located = await playlistVideo(course, item)
  const run = await runKrillinAiSubtitle({
    repoRoot,
    input: located.url,
    originLanguage,
    targetLanguage,
    captionSource,
    workdir,
    dryRun,
  })

  if (dryRun) {
    console.log(`KrillinAI dry-run 通过：${lectureId}`)
    console.log(`视频：${located.url}`)
    console.log(`workdir：${relativeToRepo(run.workdir)}`)
    return
  }

  const originSrt = krillinAiArtifact(run.workdir, 'origin_language_srt.srt')
  const targetSrt = krillinAiArtifact(run.workdir, 'target_language_srt.srt')
  const originBody = srtToTranscriptBody(readFileSync(originSrt, 'utf8'))
  const targetBody = srtToTranscriptBody(readFileSync(targetSrt, 'utf8'))
  if (!originBody || !targetBody) throw new Error('KrillinAI SRT 为空，未写入候选稿')

  mkdirSync(candidateDirectory, { recursive: true })
  const originCandidateSrt = join(candidateDirectory, 'origin_language_srt.srt')
  const targetCandidateSrt = join(candidateDirectory, 'target_language_srt.srt')
  const englishCandidate = join(candidateDirectory, 'transcript.en.md')
  const chineseCandidate = join(candidateDirectory, 'transcript.zh-CN.md')
  copyFileSync(originSrt, originCandidateSrt)
  copyFileSync(targetSrt, targetCandidateSrt)
  writeFileSync(englishCandidate, candidateTranscriptMarkdown({ course, item, languageLabel: '英文', videoUrl: located.url, srtPath: originCandidateSrt, body: originBody }), 'utf8')
  writeFileSync(chineseCandidate, candidateTranscriptMarkdown({ course, item, languageLabel: '中文', videoUrl: located.url, srtPath: targetCandidateSrt, body: targetBody }), 'utf8')
  writeYaml(join(candidateDirectory, 'run.yaml'), {
    schemaVersion: 1,
    state: 'candidate-ready',
    provider: 'krillinai',
    createdAt: new Date().toISOString(),
    course: courseId,
    lecture: lectureId,
    video: located.url,
    options: { originLanguage, targetLanguage, captionSource },
    workdir: relativeToRepo(run.workdir),
    manifest: { path: relativeToRepo(run.manifestPath), localOnly: true },
    outputs: {
      originSrt: relativeToRepo(originCandidateSrt),
      targetSrt: relativeToRepo(targetCandidateSrt),
      transcriptEn: relativeToRepo(englishCandidate),
      transcriptZh: relativeToRepo(chineseCandidate),
    },
    review: { state: 'pending', required: ['completeness', 'terminology', 'timestamps'] },
  })
  console.log(`KrillinAI 候选稿已写入：${relativeToRepo(candidateDirectory)}`)
  console.log('请审核后再手动采纳为 notes/<lecture>/ 下的正式逐字稿。')
}

function transcriptBody(markdown) {
  const bodyHeading = markdown.match(/^## 正文\s*$/m)
  if (bodyHeading) return markdown.slice(bodyHeading.index + bodyHeading[0].length).trim()
  return markdown.replace(/^# .*?\n(?:\n- .*?)*\n+/s, '').trim()
}

const transcriptTimestampPattern = /^\[((?:\d{2}:)?\d{2}:\d{2}(?:[.,]\d+)?|\d{2}:\d{2}(?:[.,]\d+)?)\]\s+/gm

function timestampSeconds(value) {
  const parts = value.replace(',', '.').split(':').map(Number)
  if (parts.length === 2) return parts[0] * 60 + parts[1]
  return parts[0] * 3600 + parts[1] * 60 + parts[2]
}

function timestampMatches(markdown) {
  return [...markdown.matchAll(transcriptTimestampPattern)].map((match) => ({ raw: match[1], seconds: timestampSeconds(match[1]) }))
}

function repeatedParagraphs(markdown) {
  const paragraphs = transcriptBody(markdown).split(/\n\s*\n/).map((part) => part.trim()).filter(Boolean)
  const repeats = []
  for (let index = 1; index < paragraphs.length; index += 1) {
    if (paragraphs[index] === paragraphs[index - 1]) repeats.push(index + 1)
  }
  return repeats
}

function validateTranscriptFiles({ englishPath, chinesePath, notePath, blogPath }) {
  const errors = []
  const warnings = []
  for (const path of [englishPath, chinesePath, notePath, blogPath]) {
    if (!existsSync(path) || !readFileSync(path, 'utf8').trim()) errors.push(`文件缺失或为空：${relativeToRepo(path)}`)
  }
  if (errors.length) return { errors, warnings }
  const english = readFileSync(englishPath, 'utf8')
  const chinese = readFileSync(chinesePath, 'utf8')
  const note = readFileSync(notePath, 'utf8')
  const blog = readFileSync(blogPath, 'utf8')
  const englishTimestamps = timestampMatches(english)
  const chineseTimestamps = timestampMatches(chinese)
  if (!englishTimestamps.length) errors.push(`英文逐字稿没有段落时间戳：${relativeToRepo(englishPath)}`)
  if (!chineseTimestamps.length) errors.push(`中文逐字稿没有段落时间戳：${relativeToRepo(chinesePath)}`)
  if (englishTimestamps.length !== chineseTimestamps.length) {
    errors.push(`中英文时间戳数量不一致：英文 ${englishTimestamps.length}，中文 ${chineseTimestamps.length}`)
  }
  const englishOrder = englishTimestamps.some((item, index, list) => index > 0 && item.seconds < list[index - 1].seconds)
  const chineseOrder = chineseTimestamps.some((item, index, list) => index > 0 && item.seconds < list[index - 1].seconds)
  if (englishOrder) warnings.push('英文来源时间戳存在倒序，保留原顺序并要求人工复核')
  if (chineseOrder) errors.push('中文翻译时间戳发生倒序')
  if (note.match(transcriptTimestampPattern)) errors.push('Lecture Note 不应包含逐段时间戳')
  if (blog.match(transcriptTimestampPattern)) errors.push('Blog 不应包含逐段时间戳')
  const repeated = [...repeatedParagraphs(english), ...repeatedParagraphs(chinese)]
  if (repeated.length) warnings.push(`发现相邻重复段落：${repeated.length} 处`)
  if (chinese.length < english.length * 0.28) errors.push(`中文稿长度异常：${chinese.length} 字符 / 英文 ${english.length} 字符`)
  for (const [label, content] of [['英文逐字稿', english], ['中文逐字稿', chinese]]) {
    if (!/^# .+/m.test(content) || !/^## 正文/m.test(content)) warnings.push(`${label} 文件头缺少标准标题或“## 正文”`)
  }
  return { errors, warnings, counts: { english: englishTimestamps.length, chinese: chineseTimestamps.length } }
}

function candidatePaths(course, item, provider) {
  const lectureDirectory = lectureNotesDirectory(course, item)
  const candidateDirectory = join(lectureDirectory, 'references', provider)
  return {
    lectureDirectory,
    candidateDirectory,
    english: join(lectureDirectory, 'transcript.en.md'),
    chinese: join(candidateDirectory, 'transcript.zh-CN.md'),
    note: join(candidateDirectory, 'note.md'),
    blog: join(candidateDirectory, 'blog.md'),
    run: join(candidateDirectory, 'run.yaml'),
    review: join(lectureDirectory, 'review.yaml'),
  }
}

function validate(courseId, lectureId, args) {
  if (!lectureId || lectureId.startsWith('--')) throw new Error('用法：course validate <course-id> <lecture-id> [--provider deepseek]')
  const provider = optionValue(args, '--provider', 'deepseek')
  const { data: course } = loadCourse(courseId)
  const item = courseItem(course, lectureId)
  const paths = candidatePaths(course, item, provider)
  const result = validateTranscriptFiles({ englishPath: paths.english, chinesePath: paths.chinese, notePath: paths.note, blogPath: paths.blog })
  console.log(`校验：${courseId}/${lectureId} · ${provider}`)
  if (result.counts) console.log(`时间戳：英文 ${result.counts.english} / 中文 ${result.counts.chinese}`)
  for (const warning of result.warnings) console.warn(`警告：${warning}`)
  if (result.errors.length) throw new Error(`校验失败：\n- ${result.errors.join('\n- ')}`)
  console.log('校验通过：可以进入人工审核或 promote。')
}

function promote(courseId, lectureId, args) {
  if (!lectureId || lectureId.startsWith('--')) throw new Error('用法：course promote <course-id> <lecture-id> [--provider deepseek] --reviewed [--overwrite]')
  if (!args.includes('--reviewed')) throw new Error('promote 需要明确传入 --reviewed，表示已完成人工审核')
  const provider = optionValue(args, '--provider', 'deepseek')
  const { path: courseConfigPath, data: course } = loadCourse(courseId)
  const item = courseItem(course, lectureId)
  const paths = candidatePaths(course, item, provider)
  const result = validateTranscriptFiles({ englishPath: paths.english, chinesePath: paths.chinese, notePath: paths.note, blogPath: paths.blog })
  if (result.errors.length) throw new Error(`候选稿未通过校验：\n- ${result.errors.join('\n- ')}`)
  const formalPaths = {
    chinese: join(paths.lectureDirectory, 'transcript.zh-CN.md'),
    note: join(paths.lectureDirectory, 'note.md'),
    blog: join(paths.lectureDirectory, 'blog.md'),
  }
  if (!args.includes('--overwrite') && Object.values(formalPaths).some(existsSync)) {
    throw new Error(`正式文件已存在；确认覆盖后增加 --overwrite`)
  }
  for (const [source, destination] of [[paths.chinese, formalPaths.chinese], [paths.note, formalPaths.note], [paths.blog, formalPaths.blog]]) {
    if (destination === formalPaths.chinese) {
      const content = readFileSync(source, 'utf8').replaceAll('../../transcript.en.md', './transcript.en.md')
      writeFileSync(destination, content, 'utf8')
    } else copyFileSync(source, destination)
  }
  writeYaml(paths.review, {
    schemaVersion: 1,
    state: 'reviewed',
    course: courseId,
    lecture: lectureId,
    provider,
    reviewedAt: new Date().toISOString(),
    source: relativeToRepo(paths.candidateDirectory),
    outputs: Object.fromEntries(Object.entries(formalPaths).map(([key, path]) => [key, relativeToRepo(path)])),
    checks: { errors: result.errors, warnings: result.warnings },
  })
  const outputs = [...(item.outputs ?? [])]
  upsertOutput(outputs, { id: 'lecture-note', label: 'Lecture Note', source: relativeToRepo(formalPaths.note), searchable: true, reviewStatus: 'reviewed' })
  upsertOutput(outputs, { id: 'blog', label: 'Blog 解读', source: relativeToRepo(formalPaths.blog), searchable: true, reviewStatus: 'reviewed' })
  upsertOutput(outputs, { id: 'transcript-zh', label: '中文逐字稿', source: relativeToRepo(formalPaths.chinese), searchable: false, reviewStatus: 'reviewed' })
  item.outputs = outputs
  item.generation = { state: 'reviewed', manifest: relativeToRepo(paths.review), reviewedAt: new Date().toISOString() }
  writeYaml(courseConfigPath, course)
  console.log(`已提升为正式稿：${relativeToRepo(paths.lectureDirectory)}`)
  console.log(`审核记录：${relativeToRepo(paths.review)}`)
}

function splitParagraphs(markdown, targetCharacters = 8_000) {
  const paragraphs = transcriptBody(markdown).split(/\n\s*\n|\n(?=[A-Z])/).map((part) => part.trim()).filter(Boolean)
  const chunks = []
  let current = ''
  for (const paragraph of paragraphs) {
    if (current && current.length + paragraph.length + 2 > targetCharacters) {
      chunks.push(current)
      current = paragraph
    } else {
      current = current ? `${current}\n\n${paragraph}` : paragraph
    }
  }
  if (current) chunks.push(current)
  return chunks
}

async function runDeepSeek(prompt) {
  const apiKey = process.env.DEEPSEEK_API_KEY ?? process.env.OPENAI_API_KEY
  const baseUrl = (process.env.DEEPSEEK_BASE_URL ?? process.env.OPENAI_BASE_URL ?? 'https://api.deepseek.com').replace(/\/$/, '')
  const model = process.env.DEEPSEEK_MODEL ?? process.env.OPENAI_MODEL ?? 'deepseek-v4-flash'
  if (!apiKey) throw new Error('未找到 DeepSeek API Key，请在 .env 中配置 DEEPSEEK_API_KEY')
  const response = await fetch(`${baseUrl}/chat/completions`, {
    method: 'POST',
    headers: { authorization: `Bearer ${apiKey}`, 'content-type': 'application/json' },
    body: JSON.stringify({
      model,
      messages: [{ role: 'user', content: prompt }],
      max_tokens: Number(process.env.DEEPSEEK_MAX_TOKENS ?? 8_192),
      thinking: { type: 'disabled' },
      stream: false,
    }),
    signal: AbortSignal.timeout(12 * 60_000),
  })
  const body = await response.json().catch(() => ({}))
  if (!response.ok) throw new Error(`DeepSeek API 失败：${body?.error?.message ?? `HTTP ${response.status}`}`)
  const content = body.choices?.[0]?.message?.content?.trim()
  if (!content) throw new Error('DeepSeek 返回了空内容')
  return { content, model: body.model ?? model, usage: body.usage ?? null }
}

async function generateDeepSeekTranslation({ courseId, course, item, transcriptEnPath, lectureSourcePath, lectureDirectory, args }) {
  if (!args.includes('--run')) {
    console.log(`DeepSeek 翻译任务已准备：${relativeToRepo(transcriptEnPath)}`)
    console.log(`执行候选稿翻译：course generate ${courseId} ${item.id} --provider deepseek --run`)
    return
  }
  const candidateDirectory = join(lectureDirectory, 'references', 'deepseek')
  const candidatePath = join(candidateDirectory, 'transcript.zh-CN.md')
  const runPath = join(candidateDirectory, 'run.yaml')
  if (!args.includes('--overwrite') && (existsSync(candidatePath) || existsSync(runPath))) {
    throw new Error(`DeepSeek 候选稿已存在：${relativeToRepo(candidateDirectory)}；确认覆盖后增加 --overwrite`)
  }
  const englishTranscript = readFileSync(transcriptEnPath, 'utf8')
  const chunks = splitParagraphs(englishTranscript)
  const translations = new Array(chunks.length)
  let nextChunk = 0
  let completedChunks = 0
  console.log(`DeepSeek 中文候选逐字稿：共 ${chunks.length} 个分块`)
  const translateWorker = async () => {
    while (nextChunk < chunks.length) {
      const index = nextChunk++
      const timestampPattern = /^(\[(?:(?:\d{2}:)?\d{2}:\d{2}(?:\.\d+)?|\d{2}:\d{2}(?:\.\d+)?)\])\s*/gm
      const timestamps = []
      const protectedChunk = chunks[index].replace(timestampPattern, (_, timestamp) => {
        const marker = `[[[TIMESTAMP_${timestamps.length}]]]`
        timestamps.push({ marker, timestamp })
        return `${marker} `
      })
      const result = await runDeepSeek(`你在翻译 ${lectureLabel(course, item)} 的英文逐字稿。请参考 Lecture 04 的成稿风格，将下面内容完整、忠实地翻译为简体中文。\n\n要求：\n1. 不摘要、不删减、不补写原文没有的事实。\n2. 保留技术术语、模型名、论文名、函数名和常用缩写；首次出现可写中文（English）。\n3. 只修正明显断句、重复、语序和能够确认的术语错误，保留讲者的论证、例子、提问、玩笑和课堂互动。\n4. 只输出自然语义段落，不添加标题、前言、总结或代码围栏。\n5. 输入中的 [[[TIMESTAMP_N]]] 标记是视频时间戳，必须原样保留在对应段落开头，不能翻译、删除、合并或改写。\n6. 这是第 ${index + 1}/${chunks.length} 个分块，只翻译给定文本。\n\n英文原文：\n${protectedChunk}`)
      let translated = result.content
      for (const { marker, timestamp } of timestamps) translated = translated.replaceAll(marker, timestamp)
      if (timestamps.some(({ timestamp }) => !translated.includes(timestamp))) {
        throw new Error(`DeepSeek 分块 ${index + 1} 丢失时间戳`)
      }
      translations[index] = translated
      completedChunks += 1
      console.log(`  完成翻译 ${completedChunks}/${chunks.length}`)
    }
  }
  await Promise.all(Array.from({ length: Math.min(3, chunks.length) }, () => translateWorker()))
  const chineseTranscript = [
    `# ${course.shortTitle ?? course.title} Lecture ${item.order}：完整中文逐字稿`,
    '',
    `- 视频：[官方视频](${item.official?.find((link) => link.label === '课程视频')?.url ?? ''})`,
    '- 来源：英文人工字幕提取后翻译为中文；保留段落起始时间戳，只修正明显的断句、重复和语序。',
    '- 说明：这是逐字稿，不是讲义摘要；相邻且语义连续的片段已合并为阅读段落；术语保留必要英文。',
    '',
    '---',
    '',
    '## 正文',
    '',
    translations.join('\n\n'),
    '',
  ].join('\n')
  const aligned = reflowAlignedTranscripts(englishTranscript, chineseTranscript)
  const finalChineseTranscript = aligned.chinese
  writeFileSync(transcriptEnPath, aligned.english, 'utf8')
  const shortChunk = translations.findIndex((translation, index) => translation.length < chunks[index].length * 0.2)
  if (shortChunk !== -1 || finalChineseTranscript.length < englishTranscript.length * 0.28) {
    throw new Error(`中文候选稿长度异常${shortChunk === -1 ? '' : `（分块 ${shortChunk + 1}）`}，可能发生输出截断`)
  }
  mkdirSync(candidateDirectory, { recursive: true })
  writeFileSync(candidatePath, finalChineseTranscript, 'utf8')
  writeYaml(runPath, {
    schemaVersion: 1,
    state: 'candidate-ready',
    provider: 'deepseek',
    model: process.env.DEEPSEEK_MODEL ?? process.env.OPENAI_MODEL ?? 'deepseek-v4-flash',
    createdAt: new Date().toISOString(),
    course: courseId,
    lecture: item.id,
    inputs: { transcriptEn: relativeToRepo(transcriptEnPath) },
    output: relativeToRepo(candidatePath),
    translation: { chunks: chunks.length, maxConcurrent: Math.min(3, chunks.length) },
    review: { state: 'pending', required: ['completeness', 'terminology', 'hallucination'] },
  })
  console.log(`DeepSeek 中文候选稿已写入：${relativeToRepo(candidatePath)}`)

  const sourceText = existsSync(lectureSourcePath) ? readFileSync(lectureSourcePath, 'utf8') : ''
  const evidence = `\n\n中文候选逐字稿：\n${finalChineseTranscript}${sourceText ? `\n\n本讲讲义代码：\n${sourceText}` : ''}`
  console.log('DeepSeek 生成 Lecture Note 候选稿')
  const noteResult = await runDeepSeek(`为 ${lectureLabel(course, item)} 编写中文 Lecture Note 候选稿。只能依据下面提供的逐字稿和讲义代码，不要虚构课程未提及的观点、数据或引用。\n\n要求：\n- 输出完整 Markdown，不要代码围栏，也不要逐段添加时间戳。\n- 面向有编程基础的学习者，结构清晰、信息密度高。\n- 包含：学习目标、课程主线、核心概念、关键公式或原则、课程作业关联、常见误区、复习清单。\n- 区分课程原意与解释，不要写成逐字稿，不要使用空泛的 AI 套话。\n- 保留重要英文术语。\n- 目标长度 3000–6000 个中文字符。${evidence}`)
  const notePath = join(candidateDirectory, 'note.md')
  if (noteResult.content.length < 2_000) throw new Error('DeepSeek Lecture Note 候选稿长度不足')
  writeFileSync(notePath, `${noteResult.content.replace(/^```(?:markdown)?\s*/i, '').replace(/\s*```$/, '').trim()}\n`, 'utf8')

  console.log('DeepSeek 生成 Blog 候选稿')
  const blogResult = await runDeepSeek(`为 ${lectureLabel(course, item)} 编写一篇可独立阅读的中文技术 Blog 候选稿。只能依据下面提供的逐字稿和讲义代码，不要虚构课程未提及的观点、数据或外部引用。\n\n要求：\n- 输出完整 Markdown，不要代码围栏，也不要逐段添加时间戳。\n- 文章要有明确标题、导语、递进论证和结语，不能只是课程提纲的改写。\n- 使用课程中的具体例子支撑观点。\n- 解释本讲内容在本课程整体学习路径中的位置。\n- 文末列出官方视频和讲义入口。\n- 保留重要英文术语。\n- 目标长度 3500–7000 个中文字符。${evidence}`)
  const blogPath = join(candidateDirectory, 'blog.md')
  if (blogResult.content.length < 2_500) throw new Error('DeepSeek Blog 候选稿长度不足')
  writeFileSync(blogPath, `${blogResult.content.replace(/^```(?:markdown)?\s*/i, '').replace(/\s*```$/, '').trim()}\n`, 'utf8')

  writeYaml(runPath, {
    schemaVersion: 1,
    state: 'candidate-ready',
    provider: 'deepseek',
    model: process.env.DEEPSEEK_MODEL ?? process.env.OPENAI_MODEL ?? 'deepseek-v4-flash',
    createdAt: new Date().toISOString(),
    course: courseId,
    lecture: item.id,
    inputs: {
      transcriptEn: relativeToRepo(transcriptEnPath),
      lecture: existsSync(lectureSourcePath) ? relativeToRepo(lectureSourcePath) : null,
    },
    outputs: {
      transcriptZh: relativeToRepo(candidatePath),
      note: relativeToRepo(notePath),
      blog: relativeToRepo(blogPath),
    },
    translation: { chunks: chunks.length, maxConcurrent: Math.min(3, chunks.length) },
    review: { state: 'pending', required: ['completeness', 'terminology', 'hallucination', 'citations'] },
  })
  console.log(`DeepSeek Note 候选稿已写入：${relativeToRepo(notePath)}`)
  console.log(`DeepSeek Blog 候选稿已写入：${relativeToRepo(blogPath)}`)
  console.log(`运行清单：${relativeToRepo(runPath)}`)
}

async function runGenerator(prompt, outputPath) {
  const binary = executable(generatorCli, 'Codex CLI')
  const generatorArgs = [
    'exec',
    '--ephemeral',
    '--ignore-user-config',
    '--ignore-rules',
    '--config', 'model_reasoning_effort="low"',
    '--sandbox', 'read-only',
    '--color', 'never',
    '--cd', repoRoot,
    '--output-last-message', outputPath,
    prompt,
  ]
  await new Promise((resolvePromise, rejectPromise) => {
    const child = spawn(binary, generatorArgs, { cwd: repoRoot, stdio: ['ignore', 'pipe', 'pipe'] })
    let stderr = ''
    child.stderr.on('data', (chunk) => {
      if (stderr.length < 100_000) stderr += chunk.toString()
    })
    const timer = setTimeout(() => {
      child.kill('SIGTERM')
      rejectPromise(new Error('模型生成超过 12 分钟'))
    }, 12 * 60_000)
    child.on('error', (error) => {
      clearTimeout(timer)
      rejectPromise(error)
    })
    child.on('close', (code, signal) => {
      clearTimeout(timer)
      if (code === 0) resolvePromise()
      else rejectPromise(new Error(`Codex CLI 退出（code=${code}, signal=${signal ?? 'none'}）：${stderr.trim().slice(-2_000)}`))
    })
  })
  const result = readFileSync(outputPath, 'utf8').trim()
  if (!result) throw new Error('模型返回了空内容')
  return result.replace(/^```(?:markdown)?\s*/i, '').replace(/\s*```$/, '').trim()
}

function upsertOutput(outputs, next) {
  const index = outputs.findIndex((output) => output.id === next.id)
  if (index === -1) outputs.push(next)
  else outputs[index] = { ...outputs[index], ...next }
}

async function generate(courseId, lectureId, args) {
  if (!lectureId || lectureId.startsWith('--')) throw new Error('用法：course generate <course-id> <lecture-id> [--run]')
  const { path: courseConfigPath, data: course } = loadCourse(courseId)
  const item = courseItem(course, lectureId)
  if (item.preparation?.state !== 'subtitle-ready') throw new Error(`请先运行：course prepare ${courseId} ${lectureId}`)

  const lectureDirectory = lectureNotesDirectory(course, item)
  mkdirSync(lectureDirectory, { recursive: true })
  const transcriptEnPath = join(lectureDirectory, 'transcript.en.md')
  if (!existsSync(transcriptEnPath)) throw new Error(`缺少英文逐字稿：${relativeToRepo(transcriptEnPath)}`)

  const lectureNumber = String(item.order).padStart(2, '0')
  const lectureSourcePath = join(coursePath(course, 'lectures', `llm/${course.id}/lectures`), `lecture_${lectureNumber}.py`)
  const transcriptZhPath = join(lectureDirectory, 'transcript.zh-CN.md')
  const notePath = join(lectureDirectory, 'note.md')
  const blogPath = join(lectureDirectory, 'blog.md')
  const generationPath = join(lectureDirectory, 'generation.yaml')
  const provider = optionValue(args, '--provider', 'codex-cli')
  if (!['codex-cli', 'deepseek'].includes(provider)) throw new Error('--provider 必须是 codex-cli 或 deepseek')
  if (provider === 'deepseek') {
    return generateDeepSeekTranslation({ courseId, course, item, transcriptEnPath, lectureSourcePath, lectureDirectory, args })
  }
  const runRequested = args.includes('--run')
  const createdAt = new Date().toISOString()
  const generation = {
    schemaVersion: 1,
    course: courseId,
    lecture: lectureId,
    state: runRequested ? 'generating' : 'task-ready',
    createdAt,
    inputs: {
      transcript: relativeToRepo(transcriptEnPath),
      lecture: existsSync(lectureSourcePath) ? relativeToRepo(lectureSourcePath) : null,
      sources: item.preparation.manifest,
    },
    outputs: {
      transcriptZh: relativeToRepo(transcriptZhPath),
      lectureNote: relativeToRepo(notePath),
      blog: relativeToRepo(blogPath),
    },
    review: { state: 'not-started' },
  }
  writeYaml(generationPath, generation)

  if (!runRequested) {
    console.log(`生成任务已准备：${relativeToRepo(generationPath)}`)
    console.log(`执行草稿生成：course generate ${courseId} ${lectureId} --run`)
    return
  }

  const tempDirectory = mkdtempSync(join(tmpdir(), `course-generate-${lectureId}-`))
  try {
    const englishTranscript = readFileSync(transcriptEnPath, 'utf8')
    const chunks = splitParagraphs(englishTranscript)
    const translations = new Array(chunks.length)
    console.log(`中文逐字稿：共 ${chunks.length} 个分块`)
    let nextChunk = 0
    let completedChunks = 0
    const translateWorker = async () => {
      while (nextChunk < chunks.length) {
        const index = nextChunk++
        const chunk = chunks[index]
        console.log(`  开始翻译 ${index + 1}/${chunks.length}`)
        const outputPath = join(tempDirectory, `translation-${index + 1}.md`)
        translations[index] = await runGenerator(`你在翻译 ${lectureLabel(course, item)} 的英文人工字幕。请将下面内容完整、忠实地翻译为简体中文。\n\n要求：\n1. 不摘要、不删减、不补写字幕中没有的事实。\n2. 保留技术术语、模型名、论文名、函数名和常用缩写；首次出现可写中文（English）。\n3. 修正明显的自动断句问题，但保留讲者的论证、例子、提问和课堂互动。\n4. 按自然语义段输出 Markdown 正文，不添加标题、前言、总结或代码围栏。\n5. 本段是 ${index + 1}/${chunks.length}，只翻译所给文本。\n\n英文字幕：\n${chunk}`, outputPath)
        completedChunks += 1
        console.log(`  完成翻译 ${index + 1}/${chunks.length}（总进度 ${completedChunks}/${chunks.length}）`)
      }
    }
    await Promise.all(Array.from({ length: Math.min(3, chunks.length) }, () => translateWorker()))
    const transcriptZh = [
      `# ${course.shortTitle ?? course.title} · Lecture ${item.order} · ${item.title}｜中文逐字稿`,
      '',
      `- 视频：${item.official?.find((link) => link.label === '课程视频')?.url ?? ''}`,
      `- 英文来源：${relativeToRepo(transcriptEnPath)}`,
      '- 状态：机器翻译草稿，待对照视频与讲义校对',
      '',
      translations.join('\n\n'),
      '',
    ].join('\n')
    const shortChunk = translations.findIndex((translation, index) => translation.length < chunks[index].length * 0.2)
    console.log(`中文逐字稿长度：${transcriptZh.length} 字符（英文源 ${englishTranscript.length} 字符）`)
    if (shortChunk !== -1 || transcriptZh.length < englishTranscript.length * 0.28) {
      throw new Error(`中文逐字稿长度异常${shortChunk === -1 ? '' : `（分块 ${shortChunk + 1}）`}，可能发生输出截断`)
    }
    writeFileSync(transcriptZhPath, transcriptZh, 'utf8')

    const commonEvidence = `只能依据以下仓库文件写作，不要虚构课程未提及的观点或引用：\n- ${relativeToRepo(transcriptEnPath)}\n- ${relativeToRepo(transcriptZhPath)}\n${existsSync(lectureSourcePath) ? `- ${relativeToRepo(lectureSourcePath)}` : ''}`
    console.log('生成 Lecture Note')
    const note = await runGenerator(`为 ${lectureLabel(course, item)} 编写中文 Lecture Note 草稿。\n${commonEvidence}\n\n要求：\n- 输出完整 Markdown，不要代码围栏，也不要逐段添加时间戳。\n- 面向有编程基础的学习者，结构清晰、信息密度高。\n- 包含：学习目标、课程主线、核心概念、关键公式或原则、课程作业关联、常见误区、复习清单。\n- 区分讲义原意与解释，不要写成逐字稿，不要使用空泛的 AI 套话。\n- 保留重要英文术语，目标长度 3000–6000 个中文字符。`, join(tempDirectory, 'note.md'))
    if (note.length < 2_000) throw new Error('Lecture Note 长度不足')
    writeFileSync(notePath, `${note.trim()}\n`, 'utf8')

    console.log('生成 Blog 草稿')
    const blog = await runGenerator(`为 ${lectureLabel(course, item)} 编写一篇可独立阅读的中文技术 Blog 草稿。\n${commonEvidence}\n\n要求：\n- 输出完整 Markdown，不要代码围栏，也不要逐段添加时间戳。\n- 文章要有明确标题、导语、递进论证和结语，不能只是课程提纲的改写。\n- 解释本讲内容在本课程整体学习路径中的位置。\n- 使用课程中的具体例子支撑观点；不要虚构数据和外部引用。\n- 文末列出官方视频和讲义入口。\n- 目标长度 3500–7000 个中文字符。`, join(tempDirectory, 'blog.md'))
    if (blog.length < 2_500) throw new Error('Blog 长度不足')
    writeFileSync(blogPath, `${blog.trim()}\n`, 'utf8')

    generation.state = 'draft-ready'
    generation.completedAt = new Date().toISOString()
    generation.generator = { provider: 'codex-cli', mode: 'read-only', translationChunks: chunks.length }
    generation.review = { state: 'pending', required: ['terminology', 'completeness', 'citations'] }
    writeYaml(generationPath, generation)

    item.generation = { state: 'draft-ready', manifest: relativeToRepo(generationPath), completedAt: generation.completedAt }
    const outputs = [...(item.outputs ?? [])]
    upsertOutput(outputs, { id: 'lecture-note', label: 'Lecture Note', source: relativeToRepo(notePath), searchable: true, reviewStatus: 'draft' })
    upsertOutput(outputs, { id: 'blog', label: 'Blog 解读', source: relativeToRepo(blogPath), searchable: true, reviewStatus: 'draft' })
    upsertOutput(outputs, { id: 'transcript-zh', label: '中文逐字稿', source: relativeToRepo(transcriptZhPath), searchable: false, reviewStatus: 'draft' })
    upsertOutput(outputs, { id: 'transcript-en', label: '英文逐字稿', source: relativeToRepo(transcriptEnPath), searchable: false, reviewStatus: 'source' })
    item.outputs = outputs
    writeYaml(courseConfigPath, course)
    console.log(`草稿生成完成：${relativeToRepo(generationPath)}`)
  } catch (error) {
    generation.state = 'error'
    generation.error = error.message
    generation.failedAt = new Date().toISOString()
    writeYaml(generationPath, generation)
    throw error
  } finally {
    rmSync(tempDirectory, { recursive: true, force: true })
  }
}

function decodeHtml(text) {
  return text
    .replace(/<[^>]+>/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&quot;/g, '"')
    .replace(/&#39;|&apos;/g, "'")
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/\s+/g, ' ')
    .trim()
}

function normalizeUrl(input) {
  const url = new URL(input)
  url.hash = ''
  for (const key of [...url.searchParams.keys()]) {
    if (/^utm_/i.test(key)) url.searchParams.delete(key)
  }
  return url.toString()
}

function resourceType(label, urlString) {
  const url = new URL(urlString)
  const value = `${label} ${url.pathname}`.toLowerCase()
  if (/youtube\.com|youtu\.be/.test(url.hostname)) return 'video'
  if (/assignment|homework|problem|作业/.test(value)) return 'assignment'
  if (/\.(?:pdf|ppt|pptx)$/.test(url.pathname.toLowerCase()) || /slides?|讲义|课件/.test(value)) return 'slides'
  if (url.hostname === 'github.com') return 'code'
  if (/syllabus|schedule|课程主页|course website/.test(value)) return 'course-page'
  return 'reference'
}

function isCandidate(label, urlString) {
  const url = new URL(urlString)
  const value = `${label} ${url.pathname}`.toLowerCase()
  return (
    /\.(?:pdf|ppt|pptx|ipynb|zip)$/.test(url.pathname.toLowerCase()) ||
    /youtube\.com|youtu\.be|github\.com/.test(url.hostname) ||
    /lecture|recording|slides?|assignment|homework|problem|syllabus|schedule|project|handout|notes?|讲义|课件|视频|作业/.test(value)
  )
}

function resourceId(type, url) {
  const hint = basename(new URL(url).pathname).replace(/\.[^.]+$/, '').replace(/[^a-z0-9]+/gi, '-').replace(/^-|-$/g, '').toLowerCase()
  const hash = createHash('sha256').update(url).digest('hex').slice(0, 8)
  return `${type}-${hint || 'resource'}-${hash}`.slice(0, 80)
}

async function fetchHtml(url) {
  const response = await fetch(url, {
    redirect: 'follow',
    headers: { 'user-agent': userAgent, accept: 'text/html,application/xhtml+xml' },
    signal: AbortSignal.timeout(20_000),
  })
  if (!response.ok) throw new Error(`${response.status} ${response.statusText}`)
  const contentType = response.headers.get('content-type') ?? ''
  if (!contentType.includes('text/html')) return { finalUrl: response.url, html: '', contentType }
  return { finalUrl: response.url, html: await response.text(), contentType }
}

function extractLinks(html, baseUrl) {
  const links = []
  const anchorPattern = /<a\b[^>]*?href\s*=\s*(["'])(.*?)\1[^>]*>([\s\S]*?)<\/a>/gi
  for (const match of html.matchAll(anchorPattern)) {
    try {
      const url = normalizeUrl(new URL(decodeHtml(match[2]), baseUrl).toString())
      if (!/^https?:/.test(url)) continue
      const rawLabel = decodeHtml(match[3])
      const label = rawLabel.length <= 180 ? rawLabel : basename(new URL(url).pathname) || new URL(url).hostname
      links.push({ label, url })
    } catch {
      // Ignore malformed and non-HTTP links.
    }
  }
  return links
}

function extractCells(rowHtml) {
  return [...rowHtml.matchAll(/<td\b[^>]*>([\s\S]*?)<\/td>/gi)].map((match) => match[1])
}

function parseSchedule(html, baseUrl, reviewResources = []) {
  const scheduleSection = html.match(/<div\b[^>]*id=["']schedule["'][^>]*>([\s\S]*?)<\/table>/i)?.[1]
  if (!scheduleSection) throw new Error('官方课程页中没有找到 #schedule 课程表')
  const bodyHtml = scheduleSection.match(/<tbody\b[^>]*>([\s\S]*?)<\/tbody>/i)?.[1]
  if (!bodyHtml) throw new Error('官方课程表中没有找到 tbody')
  const body = bodyHtml.replace(/<!--[\s\S]*?-->/g, '')

  const reviewByUrl = new Map(reviewResources.map((resource) => [normalizeUrl(resource.url), resource.status]))
  const lectures = []
  for (const row of body.matchAll(/<tr\b[^>]*>([\s\S]*?)<\/tr>/gi)) {
    const cells = extractCells(row[1])
    if (cells.length < 4) continue
    const orderText = decodeHtml(cells[0])
    if (!/^\d+$/.test(orderText)) continue

    const order = Number(orderText)
    const description = decodeHtml(cells[2])
    const instructorMatch = description.match(/\[([^\]]+)\]\s*$/)
    const instructors = instructorMatch
      ? instructorMatch[1].split(/\s*(?:,|\/|&|and)\s*/i).filter(Boolean)
      : []
    const title = description.replace(/\s*\[[^\]]+\]\s*$/, '').trim()
    const resources = extractLinks(cells[3], baseUrl).map((link) => ({
      label: link.label,
      type: resourceType(link.label, link.url),
      url: link.url,
      status: reviewByUrl.get(normalizeUrl(link.url)) ?? 'pending',
    }))
    const deadlineText = cells[4] ? decodeHtml(cells[4]) : ''
    const assignments = [...deadlineText.matchAll(/Assignment\s+(\d+)\s+(out|due)/gi)].map((match) => ({
      id: `assignment-${match[1]}`,
      state: match[2].toLowerCase(),
    }))

    lectures.push({
      id: `lecture-${String(order).padStart(2, '0')}`,
      order,
      date: decodeHtml(cells[1]),
      title,
      ...(instructors.length ? { instructors } : {}),
      resources,
      ...(assignments.length ? { assignments } : {}),
    })
  }
  if (!lectures.length) throw new Error('官方课程表中没有解析到 Lecture')
  return lectures
}

async function sync(courseId) {
  const { path, data: course } = loadCourse(courseId)
  const coursePage = (course.official ?? []).find((resource) => resource.label.includes('课程主页')) ?? course.official?.[0]
  if (!coursePage) throw new Error('课程配置缺少官方课程主页')

  const page = await fetchHtml(coursePage.url)
  const reviewResources = existsSync(reviewPath(courseId))
    ? parse(readFileSync(reviewPath(courseId), 'utf8')).resources ?? []
    : []
  const schedule = parseSchedule(page.html, page.finalUrl, reviewResources)
  const existingById = new Map((course.items ?? []).map((item) => [item.id, item]))
  course.items = schedule.map((lecture) => {
    const existing = existingById.get(lecture.id) ?? {}
    return {
      ...lecture,
      ...existing,
      date: lecture.date,
      title: lecture.title,
      instructors: lecture.instructors,
      resources: lecture.resources,
      assignments: lecture.assignments,
      status: existing.status ?? (lecture.resources.length ? 'resources-discovered' : 'scheduled'),
    }
  })
  course.schedule = {
    source: page.finalUrl,
    syncedAt: new Date().toISOString(),
    lectureCount: course.items.length,
  }
  writeYaml(path, course)
  console.log(`已同步 ${course.items.length} 节课程：catalog/courses/${courseId}.yaml`)
}

async function discover(courseId) {
  const { data: course } = loadCourse(courseId)
  const existing = existsSync(reviewPath(courseId)) ? parse(readFileSync(reviewPath(courseId), 'utf8')) : { resources: [] }
  const previousByUrl = new Map((existing.resources ?? []).map((resource) => [normalizeUrl(resource.url), resource]))
  const candidates = []
  const sources = []

  for (const seed of course.official ?? []) {
    const seedUrl = normalizeUrl(seed.url)
    candidates.push({ label: seed.label, url: seedUrl, discoveredFrom: 'course-config' })

    if (/youtube\.com|youtu\.be|github\.com/.test(new URL(seedUrl).hostname)) {
      sources.push({ url: seedUrl, status: 'seed-only' })
      continue
    }

    try {
      const page = await fetchHtml(seedUrl)
      sources.push({ url: seedUrl, finalUrl: page.finalUrl, status: 'ok', contentType: page.contentType })
      for (const link of extractLinks(page.html, page.finalUrl)) {
        if (isCandidate(link.label, link.url)) candidates.push({ ...link, discoveredFrom: seedUrl })
      }
    } catch (error) {
      sources.push({ url: seedUrl, status: 'error', error: error.message })
    }
  }

  const unique = new Map()
  for (const candidate of candidates) {
    const url = normalizeUrl(candidate.url)
    if (!unique.has(url)) unique.set(url, { ...candidate, url })
  }

  const resources = [...unique.values()]
    .map((candidate) => {
      const type = resourceType(candidate.label, candidate.url)
      const previous = previousByUrl.get(candidate.url)
      return {
        id: previous?.id ?? resourceId(type, candidate.url),
        label: candidate.label,
        type,
        url: candidate.url,
        discoveredFrom: candidate.discoveredFrom,
        status: previous?.status ?? 'pending',
      }
    })
    .sort((a, b) => a.type.localeCompare(b.type) || a.label.localeCompare(b.label, 'zh-CN'))

  const review = {
    course: courseId,
    state: resources.some((resource) => resource.status === 'pending') ? 'discovered' : 'resources-approved',
    discoveredAt: new Date().toISOString(),
    sources,
    resources,
  }
  writeYaml(reviewPath(courseId), review)
  console.log(`发现 ${resources.length} 个候选资源：catalog/reviews/${courseId}.resources.yaml`)
  for (const source of sources.filter((item) => item.status === 'error')) console.warn(`入口不可用：${source.url} (${source.error})`)
  console.log('请检查候选清单，再使用 course approve 批准需要进入知识库的资源。')
}

function approve(courseId, ids) {
  const { path, data: review } = loadReview(courseId)
  const approveAll = ids.includes('--all')
  const requested = new Set(ids.filter((id) => id !== '--all'))

  if (!approveAll && requested.size === 0) {
    for (const resource of review.resources.filter((item) => item.status === 'pending')) {
      console.log(`${resource.id}\n  ${resource.type} · ${resource.label}\n  ${resource.url}`)
    }
    console.log(`\n批准方式：course approve ${courseId} <resource-id...>`)
    return
  }

  let changed = 0
  for (const resource of review.resources) {
    if (approveAll || requested.has(resource.id)) {
      if (resource.status !== 'approved') changed += 1
      resource.status = 'approved'
      resource.reviewedAt = new Date().toISOString()
      requested.delete(resource.id)
    }
  }
  if (requested.size) throw new Error(`未知资源 ID：${[...requested].join(', ')}`)
  review.state = review.resources.some((resource) => resource.status === 'pending') ? 'partially-approved' : 'resources-approved'
  writeYaml(path, review)
  console.log(`已批准 ${changed} 个资源；当前状态：${review.state}`)
}

function safeFilename(resource) {
  const url = new URL(resource.url)
  const original = basename(url.pathname)
  if (original && extname(original)) return original.replace(/[^a-z0-9._-]+/gi, '-')
  return `${resource.id}.html`
}

async function downloadResource(resource, destination) {
  const sourceUrl = new URL(resource.url)
  const githubBlob = sourceUrl.hostname === 'github.com' && sourceUrl.pathname.match(/^\/([^/]+)\/([^/]+)\/blob\/([^/]+)\/(.+)$/)
  const downloadUrl = githubBlob
    ? `https://raw.githubusercontent.com/${githubBlob[1]}/${githubBlob[2]}/${githubBlob[3]}/${githubBlob[4]}`
    : resource.url
  const response = await fetch(downloadUrl, {
    redirect: 'follow',
    headers: { 'user-agent': userAgent },
    signal: AbortSignal.timeout(60_000),
  })
  if (!response.ok) throw new Error(`${response.status} ${response.statusText}`)
  mkdirSync(dirname(destination), { recursive: true })
  writeFileSync(destination, Buffer.from(await response.arrayBuffer()))
}

async function ingest(courseId, flags) {
  const { data: course } = loadCourse(courseId)
  const { path: sourceReviewPath, data: review } = loadReview(courseId)
  const approved = review.resources.filter((resource) => resource.status === 'approved')
  if (!approved.length) throw new Error(`没有已批准资源，请先运行：course approve ${courseId} <resource-id...>`)

  const storage = coursePath(course, 'resources', `llm/${courseId}/resources`)
  mkdirSync(storage, { recursive: true })
  const shouldDownload = flags.includes('--download')
  const entries = []

  for (const resource of approved) {
    const binary = ['slides', 'assignment'].includes(resource.type) && /\.(?:pdf|ppt|pptx|zip)$/i.test(new URL(resource.url).pathname)
    const destination = binary ? join(storage, 'files', safeFilename(resource)) : null
    let ingestStatus = 'linked'
    let error
    if (destination && shouldDownload) {
      try {
        await downloadResource(resource, destination)
        ingestStatus = 'downloaded'
      } catch (downloadError) {
        ingestStatus = 'error'
        error = downloadError.message
      }
    } else if (destination) {
      ingestStatus = 'ready-to-download'
    }
    entries.push({
      id: resource.id,
      label: resource.label,
      type: resource.type,
      url: resource.url,
      status: ingestStatus,
      local: ingestStatus === 'downloaded' ? destination.slice(repoRoot.length + 1) : null,
      ...(error ? { error } : {}),
    })
  }

  const manifestPath = join(storage, 'manifest.yaml')
  writeYaml(manifestPath, {
    course: courseId,
    state: entries.some((entry) => entry.status === 'error') ? 'ingest-errors' : 'ingested',
    ingestedAt: new Date().toISOString(),
    review: sourceReviewPath.slice(repoRoot.length + 1),
    resources: entries,
  })
  console.log(`已写入资源清单：${manifestPath.slice(repoRoot.length + 1)}`)
  if (!shouldDownload && entries.some((entry) => entry.status === 'ready-to-download')) {
    console.log('存在可下载讲义；确认后使用 course ingest --download。')
  }
}

function status(courseId) {
  const { data: course } = loadCourse(courseId)
  if (!existsSync(reviewPath(courseId))) {
    console.log(`${course.shortTitle ?? course.title}: configured → 下一步 discover`)
    return
  }
  const review = parse(readFileSync(reviewPath(courseId), 'utf8'))
  const counts = review.resources.reduce((result, resource) => {
    result[resource.status] = (result[resource.status] ?? 0) + 1
    return result
  }, {})
  console.log(`${course.shortTitle ?? course.title}: ${review.state}`)
  console.log(counts)
}

async function main() {
  const [command, courseId, ...args] = process.argv.slice(2)
  if (!command || ['-h', '--help', 'help'].includes(command)) return usage()
  if (!courseId) return usage(1)
  if (command === 'sync') return sync(courseId)
  if (command === 'prepare') return prepare(courseId, args[0], args.slice(1))
  if (command === 'transcript') return transcript(courseId, args[0], args.slice(1))
  if (command === 'generate') return generate(courseId, args[0], args.slice(1))
  if (command === 'validate') return validate(courseId, args[0], args.slice(1))
  if (command === 'promote') return promote(courseId, args[0], args.slice(1))
  if (command === 'discover') return discover(courseId)
  if (command === 'approve') return approve(courseId, args)
  if (command === 'ingest') return ingest(courseId, args)
  if (command === 'status') return status(courseId)
  throw new Error(`未知命令：${command}`)
}

main().catch((error) => {
  console.error(`course: ${error.message}`)
  process.exitCode = 1
})
