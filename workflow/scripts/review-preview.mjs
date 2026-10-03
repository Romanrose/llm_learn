#!/usr/bin/env node
import { cpSync, mkdtempSync, realpathSync, symlinkSync, writeFileSync } from 'node:fs'
import { spawn, spawnSync } from 'node:child_process'
import { tmpdir } from 'node:os'
import { dirname, join, relative, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

// Render the existing website into a disposable snapshot. Normal builds cannot
// replace the candidate content served by this preview.
const repo = resolve(dirname(fileURLToPath(import.meta.url)), '../..')
const source = join(repo, 'website')
const snapshot = realpathSync(mkdtempSync(join(tmpdir(), 'llm-learn-review-')))
const excluded = new Set(['generated', '.vitepress/generated', '.vitepress/dist', '.vitepress/cache'])
cpSync(source, snapshot, { recursive: true, filter: path => !excluded.has(relative(source, path)) })
writeFileSync(join(snapshot, 'package.json'), JSON.stringify({ private: true, type: 'module' }))
symlinkSync(join(repo, 'node_modules'), join(snapshot, 'node_modules'), 'dir')
const generation = spawnSync(process.execPath, [join(repo, 'workflow/scripts/generate-site.mjs'), '--review', '--preview-root', snapshot], { stdio: 'inherit' })
if (generation.error || generation.status !== 0) throw generation.error ?? Error('审核页面生成失败')
const child = spawn(process.execPath, [join(repo, 'node_modules/vitepress/bin/vitepress.js'), 'dev', snapshot, '--host', '127.0.0.1', '--port', '4184', '--strictPort'], { stdio: 'inherit' })
child.on('error', error => { console.error(error.message); process.exitCode = 1 })
child.on('exit', code => { process.exitCode = code ?? 0 })
for (const signal of ['SIGINT', 'SIGTERM']) process.on(signal, () => child.kill(signal))
