import { execFile } from 'node:child_process'
import { existsSync, readFileSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { promisify } from 'node:util'

const execFileAsync = promisify(execFile)

export function krillinAiBinary(repoRoot) {
  const executable = process.platform === 'win32' ? 'krillinai-cli.exe' : 'krillinai-cli'
  return process.env.COURSE_KRILLINAI ?? join(repoRoot, 'workflow', '.runtime', 'krillinai', executable)
}

function assertInsideRepo(repoRoot, path) {
  const root = resolve(repoRoot)
  const resolved = resolve(path)
  if (!resolved.startsWith(`${root}/`)) throw new Error('KrillinAI workdir 必须位于仓库内部')
  return resolved
}

function parseLastJsonLine(stdout) {
  const lines = stdout.trim().split(/\r?\n/).filter(Boolean)
  for (let index = lines.length - 1; index >= 0; index -= 1) {
    try {
      return JSON.parse(lines[index])
    } catch {
      // KrillinAI can write human-readable progress before its final JSON result.
    }
  }
  throw new Error('KrillinAI 没有返回可解析的 JSON 结果')
}

export async function runKrillinAiSubtitle({
  repoRoot,
  input,
  originLanguage,
  targetLanguage,
  captionSource = 'any',
  workdir,
  dryRun = false,
}) {
  const binary = krillinAiBinary(repoRoot)
  if (!existsSync(binary)) throw new Error(`找不到 KrillinAI CLI：${binary}`)
  const resolvedWorkdir = assertInsideRepo(repoRoot, workdir)
  const args = [
    'subtitle',
    input,
    '--origin-lang', originLanguage,
    '--target-lang', targetLanguage,
    '--caption-source', captionSource,
    '--workdir', resolvedWorkdir,
    ...(dryRun ? ['--dry-run'] : []),
  ]
  const { stdout, stderr } = await execFileAsync(binary, args, {
    // KrillinAI discovers its config/ directory beside its executable.
    cwd: dirname(binary),
    timeout: 12 * 60_000,
    maxBuffer: 20 * 1024 * 1024,
  })
  const result = parseLastJsonLine(stdout)
  if (!result.ok) throw new Error(result.error ?? 'KrillinAI 字幕任务失败')
  return {
    result,
    stdout,
    stderr,
    workdir: resolvedWorkdir,
    manifestPath: join(resolvedWorkdir, 'krillinai_manifest.json'),
  }
}

export function krillinAiArtifact(workdir, filename) {
  const path = join(workdir, filename)
  if (!existsSync(path)) throw new Error(`KrillinAI 未生成预期文件：${filename}`)
  return path
}

function cleanSrtText(text) {
  return text
    .replace(/<[^>]+>/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&quot;/g, '"')
    .replace(/&#39;|&apos;/g, "'")
    .replace(/\s+/g, ' ')
    .trim()
}

function timestamp(value) {
  return value.replace(',', '.').slice(0, 8)
}

export function srtToTranscriptBody(srt, paragraphCharacters = 700) {
  const cues = []
  for (const block of srt.replace(/^\uFEFF/, '').split(/\r?\n\s*\r?\n/)) {
    const lines = block.split(/\r?\n/).map((line) => line.trim()).filter(Boolean)
    const timeIndex = lines.findIndex((line) => line.includes('-->'))
    if (timeIndex === -1) continue
    const start = lines[timeIndex].split('-->')[0].trim()
    const text = cleanSrtText(lines.slice(timeIndex + 1).join(' '))
    if (text && cues.at(-1)?.text !== text) cues.push({ start, text })
  }
  const paragraphs = []
  let current = null
  for (const cue of cues) {
    if (!current || current.text.length + cue.text.length + 1 > paragraphCharacters) {
      if (current) paragraphs.push(current)
      current = { start: cue.start, text: cue.text }
    } else {
      current.text += ` ${cue.text}`
    }
  }
  if (current) paragraphs.push(current)
  return paragraphs.map((paragraph) => `[${timestamp(paragraph.start)}] ${paragraph.text}`).join('\n\n')
}

export function readKrillinAiManifest(manifestPath) {
  return existsSync(manifestPath) ? JSON.parse(readFileSync(manifestPath, 'utf8')) : null
}
