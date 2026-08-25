#!/usr/bin/env node

import { createHash } from 'node:crypto'
import { chmod, copyFile, mkdir, writeFile } from 'node:fs/promises'
import { existsSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), '../..')
const runtimeRoot = join(repoRoot, 'workflow', '.runtime', 'krillinai')
const version = '2.1.0'
const releaseBase = `https://github.com/krillinai/KrillinAI/releases/download/v${version}`
const dryRun = process.argv.slice(2).includes('--dry-run')

const releases = {
  'darwin-arm64': { asset: 'KrillinAI-cli_2.1.0_macOS_arm64', sha256: '3fdf9d573ffd6fc717f63a09d227b62da80919b5efe11e5504d3ad44f7090930' },
  'darwin-x64': { asset: 'KrillinAI-cli_2.1.0_macOS_amd64', sha256: '99f232430d58dd2bf35504afda2f037cb571ef010082a16e65cf5ae3861cd356' },
  'linux-arm64': { asset: 'KrillinAI-cli_2.1.0_Linux_arm64', sha256: '3cbb5a71323a63d293031d91375c3d94f5ca31bf82f58b2fd27c0702058e9ed3' },
  'linux-x64': { asset: 'KrillinAI-cli_2.1.0_Linux_x86_64', sha256: '3f4e35af40d4ab4432e1bf9d40f8ab36c693631a90cd70946ee476034a571529' },
  'win32-arm64': { asset: 'KrillinAI-cli_2.1.0_Windows_arm64.exe', sha256: '4662af8bea298ddd00a83c14b80b4bb46de80d2ecc9b6af60d7ff2bc293fdf1d' },
  'win32-x64': { asset: 'KrillinAI-cli_2.1.0_Windows.exe', sha256: '9050e37d41fa41097c07eb310003f3985422cb6c3ef8a117fd39fb45ac76805f' },
}

function target() {
  const release = releases[`${process.platform}-${process.arch}`]
  if (!release) throw new Error(`暂不支持 KrillinAI 自动安装：${process.platform}/${process.arch}`)
  return { ...release, binary: join(runtimeRoot, process.platform === 'win32' ? 'krillinai-cli.exe' : 'krillinai-cli') }
}

async function main() {
  const selected = target()
  console.log(`KrillinAI ${version}: ${selected.asset}`)
  console.log(`目标：${selected.binary.slice(repoRoot.length + 1)}`)
  if (dryRun) return

  await mkdir(runtimeRoot, { recursive: true })
  if (!existsSync(selected.binary)) {
    const response = await fetch(`${releaseBase}/${selected.asset}`, { signal: AbortSignal.timeout(120_000) })
    if (!response.ok) throw new Error(`官方下载失败：HTTP ${response.status}`)
    const payload = Buffer.from(await response.arrayBuffer())
    const checksum = createHash('sha256').update(payload).digest('hex')
    if (checksum !== selected.sha256) throw new Error(`SHA-256 校验失败：${checksum}`)
    await writeFile(selected.binary, payload, { mode: 0o755 })
    if (process.platform !== 'win32') await chmod(selected.binary, 0o755)
    console.log('KrillinAI CLI 下载并校验完成。')
  } else {
    console.log('KrillinAI CLI 已存在，跳过下载。')
  }

  const configDirectory = join(runtimeRoot, 'config')
  const configPath = join(configDirectory, 'config.toml')
  if (!existsSync(configPath)) {
    await mkdir(configDirectory, { recursive: true })
    const template = join(repoRoot, 'workflow', 'templates', 'krillinai', 'config.example.toml')
    await copyFile(template, configPath)
    console.log(`已创建本机配置模板：${configPath.slice(repoRoot.length + 1)}`)
  }
  console.log('接下来编辑 config.toml 的 [transcribe] 与 [llm]，再运行 workflow:doctor。')
}

main().catch((error) => {
  console.error(`workflow:bootstrap:krillinai failed: ${error.message}`)
  process.exitCode = 1
})
