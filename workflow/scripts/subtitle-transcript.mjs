#!/usr/bin/env node

import { execFile } from 'node:child_process'
import { mkdtemp, readFile, readdir, rm, stat, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { basename, extname, join, resolve } from 'node:path'
import { promisify } from 'node:util'

const execFileAsync = promisify(execFile)
const supportedExtensions = new Set(['.vtt', '.srt'])

function usage(exitCode = 0) {
  console.log(`subtitle-transcript — download platform subtitles without downloading media

Usage:
  node workflow/scripts/subtitle-transcript.mjs <video-url> --output <transcript.md> --langs <en-US,en> [--yt-dlp <path>] [--with-timestamps]

The command downloads only subtitle tracks through yt-dlp. It never downloads audio or video.`)
  process.exitCode = exitCode
}

function option(args, name, fallback = null) {
  const index = args.indexOf(name)
  if (index === -1) return fallback
  const value = args[index + 1]
  if (!value || value.startsWith('--')) throw new Error(`${name} requires a value`)
  return value
}

function cleanText(text) {
  return text
    .replace(/<[^>]+>/g, '')
    .replace(/&amp;/g, '&')
    .replace(/&quot;/g, '"')
    .replace(/&#39;|&apos;/g, "'")
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/\{\\.*?\}/g, '')
    .replace(/\b(?:align|position|size|line):\S+/g, '')
    .replace(/\s+/g, ' ')
    .trim()
}

function formatTimestamp(raw) {
  const value = raw.trim().replace(',', '.')
  const [hours, minutes, seconds] = value.split(':')
  return hours === '00' ? `${minutes}:${seconds}` : value
}

function parseVttOrSrt(contents) {
  const cues = []
  let timestamp = null
  let lines = []
  const flush = () => {
    const text = cleanText(lines.join(' '))
    if (timestamp && text) cues.push({ timestamp, text })
    timestamp = null
    lines = []
  }
  for (const original of contents.split(/\r?\n/)) {
    const line = original.replace(/^\uFEFF/, '').trim()
    if (!line) {
      flush()
      continue
    }
    if (/^(?:WEBVTT|Kind:|Language:|STYLE|NOTE|REGION)\b/i.test(line) || /^\d+$/.test(line)) continue
    const match = line.match(/^(?:(\d{1,2}):)?(\d{2}):(\d{2}(?:[.,]\d+)?)\s+-->\s+/)
    if (match) {
      flush()
      timestamp = formatTimestamp(match[1] ? `${match[1]}:${match[2]}:${match[3]}` : `${match[2]}:${match[3]}`)
      continue
    }
    if (!line.includes('-->')) lines.push(line)
  }
  flush()
  return dedupe(cues)
}

function dedupe(cues) {
  const result = []
  let previous = ''
  for (const cue of cues) {
    const normalized = cue.text.replace(/\s+/g, '').toLowerCase()
    if (!normalized || normalized === previous) continue
    if (previous && normalized.startsWith(previous) && normalized.length < previous.length + 40) {
      result.at(-1).text = cue.text
      result.at(-1).timestamp = cue.timestamp
    } else {
      result.push(cue)
    }
    previous = normalized
  }
  return result
}

async function subtitleFiles(directory) {
  const entries = await readdir(directory, { withFileTypes: true })
  const nested = await Promise.all(entries.map(async (entry) => {
    const path = join(directory, entry.name)
    if (entry.isDirectory()) return subtitleFiles(path)
    return supportedExtensions.has(extname(entry.name).toLowerCase()) ? [path] : []
  }))
  return nested.flat()
}

async function chooseSubtitle(files, languages) {
  const scored = await Promise.all(files.map(async (path) => {
    const lower = basename(path).toLowerCase()
    const languageIndex = languages.findIndex((language) => lower.includes(`.${language.toLowerCase()}.`) || lower.endsWith(`.${language.toLowerCase()}${extname(path).toLowerCase()}`))
    return { path, languageIndex: languageIndex === -1 ? languages.length : languageIndex, mtime: (await stat(path)).mtimeMs }
  }))
  return scored.sort((left, right) => left.languageIndex - right.languageIndex || right.mtime - left.mtime)[0]?.path
}

async function main() {
  const args = process.argv.slice(2)
  if (!args.length || args.includes('--help') || args.includes('-h')) return usage()
  const videoUrl = args[0]
  const output = option(args, '--output')
  const rawLanguages = option(args, '--langs', 'en-US,en')
  const ytDlp = option(args, '--yt-dlp', process.env.COURSE_YT_DLP || 'yt-dlp')
  if (!videoUrl.startsWith('http') || !output) throw new Error('A video URL and --output are required')
  const languages = rawLanguages.split(',').map((item) => item.trim()).filter(Boolean)
  const workdir = await mkdtemp(join(tmpdir(), 'llm-learn-subtitles-'))
  try {
    await execFileAsync(ytDlp, [
      '--skip-download', '--write-subs', '--write-auto-subs', '--sub-langs', languages.join(','),
      '--output', join(workdir, '%(id)s.%(ext)s'), videoUrl,
    ], { timeout: 120_000, maxBuffer: 20 * 1024 * 1024 })
    const files = await subtitleFiles(workdir)
    const selected = await chooseSubtitle(files, languages)
    if (!selected) throw new Error('yt-dlp did not produce a VTT or SRT subtitle track')
    const cues = parseVttOrSrt(await readFile(selected, 'utf8'))
    if (!cues.length) throw new Error(`No readable cues found in ${basename(selected)}`)
    const body = cues.map((cue) => `[${cue.timestamp}] ${cue.text}`).join('\n\n')
    await writeFile(resolve(output), `# Subtitle candidate\n\n- Source: ${videoUrl}\n- Track: ${basename(selected)}\n\n## 正文\n\n${body}\n`, 'utf8')
    console.log(`Subtitle extracted: ${basename(selected)} (${cues.length} cues)`)
  } finally {
    await rm(workdir, { recursive: true, force: true })
  }
}

main().catch((error) => {
  console.error(`subtitle-transcript: ${error.message}`)
  process.exitCode = 1
})
