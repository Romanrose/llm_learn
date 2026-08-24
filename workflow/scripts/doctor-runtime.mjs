#!/usr/bin/env node

import { execFile } from 'node:child_process'
import { existsSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { promisify } from 'node:util'

const execFileAsync = promisify(execFile)
const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), '../..')
const runtimeRoot = join(repoRoot, 'workflow', '.runtime')
const isWindows = process.platform === 'win32'
const defaultYtDlp = join(runtimeRoot, isWindows ? 'Scripts/yt-dlp.exe' : 'bin/yt-dlp')
const subtitleTool = process.env.COURSE_SUBTITLE_TOOL ?? join(repoRoot, 'workflow', 'scripts', 'subtitle-transcript.mjs')
const ytDlp = process.env.COURSE_YT_DLP ?? defaultYtDlp

function executable(path) {
  if (existsSync(path)) return path
  if (!path.includes('/') && !path.includes('\\')) {
    for (const directory of (process.env.PATH ?? '').split(process.platform === 'win32' ? ';' : ':')) {
      const candidate = join(directory, path)
      if (existsSync(candidate)) return candidate
    }
  }
  return null
}

async function check(label, path, required = true) {
  const resolved = executable(path)
  if (!resolved) {
    console.log(`${required ? 'FAIL' : 'INFO'} ${label}: not found (${path})`)
    return !required
  }
  try {
    const { stdout } = await execFileAsync(resolved, ['--version'], { timeout: 10_000 })
    console.log(`OK   ${label}: ${resolved}${stdout.trim() ? ` (${stdout.trim().split('\n')[0]})` : ''}`)
    return true
  } catch {
    console.log(`OK   ${label}: ${resolved}`)
    return true
  }
}

async function main() {
  let healthy = true
  console.log(`Node: ${process.version}`)
  healthy = (await check('yt-dlp', ytDlp)) && healthy
  if (existsSync(subtitleTool)) console.log(`OK   subtitle tool: ${subtitleTool}`)
  else { console.log(`FAIL subtitle tool: not found (${subtitleTool})`); healthy = false }
  await check('Codex CLI (optional for --provider codex-cli)', process.env.COURSE_GENERATOR ?? 'codex', false)
  await check('KrillinAI (optional for transcript --engine krillinai)', process.env.COURSE_KRILLINAI ?? 'krillinai-cli', false)
  if (!process.env.DEEPSEEK_API_KEY && !process.env.OPENAI_API_KEY) console.log('INFO model API key: not configured (needed only for --provider deepseek)')
  if (!healthy) {
    console.log('\nRun `npm run workflow:bootstrap` to install the required subtitle runtime, then run this command again.')
    process.exitCode = 1
  }
}

main().catch((error) => {
  console.error(`workflow:doctor failed: ${error.message}`)
  process.exitCode = 1
})
