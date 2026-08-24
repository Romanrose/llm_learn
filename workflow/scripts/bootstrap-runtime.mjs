#!/usr/bin/env node

import { execFile } from 'node:child_process'
import { existsSync } from 'node:fs'
import { dirname, join, relative, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { promisify } from 'node:util'

const execFileAsync = promisify(execFile)
const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), '../..')
const runtimeRoot = join(repoRoot, 'workflow', '.runtime')
const isWindows = process.platform === 'win32'
const python = join(runtimeRoot, isWindows ? 'Scripts/python.exe' : 'bin/python')
const uv = process.env.COURSE_UV ?? 'uv'
const dryRun = process.argv.slice(2).includes('--dry-run')

async function run(command, args) {
  console.log(`$ ${command} ${args.join(' ')}`)
  if (dryRun) return
  await execFileAsync(command, args, { cwd: repoRoot, timeout: 120_000, maxBuffer: 2 * 1024 * 1024 })
}

async function main() {
  if (!existsSync(python)) {
    await run(uv, ['venv', runtimeRoot, '--python', '3.12'])
  } else {
    console.log(`Runtime already available: ${relative(repoRoot, runtimeRoot)}`)
  }

  // YouTube changes often enough that a historical exact pin becomes unusable.
  // Keep a minimum supported version, and refresh it when bootstrap is rerun.
  await run(uv, ['pip', 'install', '--upgrade', '--python', python, 'yt-dlp>=2025.10.14'])
  console.log('\nTranscript runtime ready. Run `npm run workflow:doctor` to verify it.')
}

main().catch((error) => {
  console.error(`workflow:bootstrap failed: ${error.message}`)
  console.error('Install uv first (https://docs.astral.sh/uv/) or set COURSE_UV to its executable path.')
  process.exitCode = 1
})
