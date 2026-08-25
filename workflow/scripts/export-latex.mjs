#!/usr/bin/env node

import { copyFileSync, existsSync, mkdirSync, readFileSync, readdirSync, rmSync, writeFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
import { dirname, extname, join, relative, resolve, sep } from 'node:path'
import { fileURLToPath } from 'node:url'
import { parse } from 'yaml'

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), '../..')
const catalogRoot = join(repoRoot, 'website', 'catalog-data', 'courses')
const templateRoot = join(repoRoot, 'workflow', 'templates', 'latex')
const publicRoot = join(repoRoot, 'website', 'public', 'generated', 'exports')

function relativeToRepo(path) {
  return relative(repoRoot, path) || '.'
}

function ensureParent(path) {
  mkdirSync(dirname(path), { recursive: true })
}

function write(path, content) {
  ensureParent(path)
  writeFileSync(path, `${content.trimEnd()}\n`, 'utf8')
}

function escapeLatex(value) {
  return value
    .replaceAll('\\', '\\textbackslash{}')
    .replaceAll('&', '\\&')
    .replaceAll('%', '\\%')
    .replaceAll('$', '\\$')
    .replaceAll('#', '\\#')
    .replaceAll('_', '\\_')
    .replaceAll('{', '\\{')
    .replaceAll('}', '\\}')
    .replaceAll('~', '\\textasciitilde{}')
    .replaceAll('^', '\\textasciicircum{}')
}

function escapeUrl(value) {
  return value.replaceAll('\\', '\\textbackslash{}').replaceAll('#', '\\#').replaceAll('%', '\\%').replaceAll('&', '\\&').replaceAll('_', '\\_')
}

function protectMath(value, state) {
  return value.replace(/(\$\$[\s\S]*?\$\$|\\\[[\s\S]*?\\\]|\\\([\s\S]*?\\\)|(?<!\$)\$(?!\$)[^\n$]+?(?<!\$)\$(?!\$))/g, (match) => {
    const token = `LLMATHTOKEN${state.math.length}LL`
    state.math.push(match)
    return token
  })
}

function restoreMath(value, state) {
  return state.math.reduce((result, math, index) => result.replace(`LLMATHTOKEN${index}LL`, math), value)
}

function inlineLatex(value, state) {
  let text = escapeLatex(protectMath(value, state))
  text = text.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, (_match, alt, target) => {
    const asset = state.assets.get(target) ?? target
    return `\\includegraphics[width=0.9\\textwidth]{${asset}}`
  })
  text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_match, label, target) => `\\href{${escapeUrl(target.replaceAll('\\&', '&'))}}{${label}}`)
  text = text.replace(/\*\*([^*]+)\*\*/g, (_match, content) => `\\textbf{${content}}`)
  text = text.replace(/`([^`]+)`/g, (_match, content) => `\\texttt{${content}}`)
  text = text.replace(/\*([^*]+)\*/g, (_match, content) => `\\emph{${content}}`)
  return restoreMath(text, state)
}

function parseTable(lines, state) {
  const rows = lines
    .map((line) => line.trim().replace(/^\||\|$/g, '').split('|').map((cell) => cell.trim()))
    .filter((row) => !row.every((cell) => /^:?-{3,}:?$/.test(cell)))
  if (!rows.length) return ''
  const columns = Math.max(...rows.map((row) => row.length))
  const formatRow = (row, header = false) => {
    const cells = Array.from({ length: columns }, (_value, index) => row[index] ?? '')
      .map((cell) => header ? `\\textbf{${inlineLatex(cell, state)}}` : inlineLatex(cell, state))
    return `${cells.join(' & ')} \\\\`
  }
  return [
    '\\begin{table}[htbp]',
    '\\centering',
    '\\small',
    `\\begin{tabularx}{\\textwidth}{${'|X'.repeat(columns)}|}`,
    '\\hline',
    formatRow(rows[0], true),
    '\\hline',
    ...rows.slice(1).map((row) => `${formatRow(row)}\\hline`),
    '\\end{tabularx}',
    '\\end{table}',
  ].join('\n')
}

function renderList(lines, state) {
  const ordered = /^\s*\d+\.\s+/.test(lines[0])
  const environment = ordered ? 'enumerate' : 'itemize'
  const items = lines.map((line) => line.replace(/^\s*(?:\d+\.|[-*])\s+/, '').trim())
  return [`\\begin{${environment}}`, ...items.map((item) => `\\item ${inlineLatex(item, state)}`), `\\end{${environment}}`].join('\n')
}

function renderParagraph(lines, state) {
  return inlineLatex(lines.map((line) => line.trim()).join(' '), state)
}

function collectAssets(markdown, noteDirectory, outputDirectory) {
  const assets = new Map()
  const assetDirectory = join(outputDirectory, 'assets')
  for (const match of markdown.matchAll(/!\[[^\]]*\]\(([^)]+)\)/g)) {
    const source = resolve(noteDirectory, match[1])
    if (!existsSync(source)) continue
    const destination = join(assetDirectory, source.split(sep).at(-1))
    mkdirSync(assetDirectory, { recursive: true })
    copyFileSync(source, destination)
    assets.set(match[1], `assets/${destination.split(sep).at(-1)}`)
  }
  return assets
}

function markdownToLatex(markdown, { noteDirectory, outputDirectory }) {
  const titleMatch = markdown.match(/^#\s+(.+)$/m)
  const title = titleMatch ? titleMatch[1].trim() : '课程讲义'
  const state = { math: [], assets: collectAssets(markdown, noteDirectory, outputDirectory) }
  const lines = markdown.replace(/\r/g, '').split('\n')
  const body = []
  let index = 0

  while (index < lines.length) {
    const line = lines[index]
    if (!line.trim()) {
      index += 1
      continue
    }
    if (/^#\s+/.test(line)) {
      index += 1
      continue
    }
    const heading = line.match(/^(#{2,4})\s+(.+)$/)
    if (heading) {
      const command = { 2: 'section', 3: 'subsection', 4: 'subsubsection' }[heading[1].length]
      const headingText = heading[2].replace(/^\d+(?:\.\d+)*[.)]\s+/, '')
      body.push(`\\${command}{${inlineLatex(headingText, state)}}`)
      index += 1
      continue
    }
    if (/^---\s*$/.test(line)) {
      body.push('\\medskip\\noindent\\rule{\\textwidth}{0.4pt}\\medskip')
      index += 1
      continue
    }
    if (/^```/.test(line)) {
      const requestedLanguage = line.slice(3).trim().toLowerCase()
      const supportedLanguages = new Set(['bash', 'c', 'c++', 'java', 'javascript', 'json', 'matlab', 'python', 'sql', 'tex', 'xml'])
      const language = supportedLanguages.has(requestedLanguage) ? `[language=${requestedLanguage}]` : ''
      const code = []
      index += 1
      while (index < lines.length && !/^```/.test(lines[index])) code.push(lines[index++])
      index += 1
      body.push(`\\begin{lstlisting}${language}\n${code.join('\n')}\n\\end{lstlisting}`)
      continue
    }
    if (/^\s*\|/.test(line) && lines[index + 1]?.includes('|---')) {
      const table = []
      while (index < lines.length && /^\s*\|/.test(lines[index])) table.push(lines[index++])
      body.push(parseTable(table, state))
      continue
    }
    if (/^\s*(?:[-*]|\d+\.)\s+/.test(line)) {
      const list = []
      const ordered = /^\s*\d+\.\s+/.test(line)
      while (index < lines.length && /^\s*(?:[-*]|\d+\.)\s+/.test(lines[index])) {
        if (/^\s*\d+\.\s+/.test(lines[index]) !== ordered) break
        list.push(lines[index++])
      }
      body.push(renderList(list, state))
      continue
    }
    if (/^>\s?/.test(line)) {
      const quote = []
      while (index < lines.length && /^>\s?/.test(lines[index])) quote.push(lines[index++].replace(/^>\s?/, ''))
      body.push(`\\begin{SourceBox}[课堂提示]\n${renderParagraph(quote, state)}\n\\end{SourceBox}`)
      continue
    }
    const paragraph = [line]
    index += 1
    while (index < lines.length && lines[index].trim() && !/^(?:#{2,4}\s|---\s*$|```|\s*\||\s*(?:[-*]|\d+\.)\s+|>\s?)/.test(lines[index])) {
      paragraph.push(lines[index++])
    }
    body.push(renderParagraph(paragraph, state))
  }

  return { title, body: body.join('\n\n') }
}

function copyTemplateStyles(outputDirectory) {
  const stylesDirectory = join(outputDirectory, 'styles')
  mkdirSync(stylesDirectory, { recursive: true })
  for (const name of ['mi-core.sty', 'mi-book.sty']) copyFileSync(join(templateRoot, name), join(stylesDirectory, name))
}

function makeTex({ course, item, title, body }) {
  const courseTitle = course.shortTitle ?? course.title ?? course.id
  const lectureLabel = `Lecture ${String(item.order ?? '').padStart(2, '0')} - ${item.title ?? ''}`
  return `% Auto-generated by llm_learn. Edit note.md, not this file.\n\\documentclass[10pt,openany]{book}\n\\usepackage{styles/mi-core}\n\\usepackage{styles/mi-book}\n\\begin{document}\n\\MakeBookCover{${title}}{${escapeLatex(courseTitle)}}{${escapeLatex(lectureLabel)}}\n\\setcounter{tocdepth}{2}\n\\tableofcontents\n\\mainmatter\n\\renewcommand{\\thesection}{\\arabic{section}}\n\\renewcommand{\\thesubsection}{\\thesection.\\arabic{subsection}}\n\\renewcommand{\\thesubsubsection}{\\thesubsection.\\arabic{subsubsection}}\n\\markboth{${escapeLatex(courseTitle)}}{${escapeLatex(lectureLabel)}}\n${body}\n\\backmatter\n\\end{document}\n`
}

function runXeLatex(outputDirectory, texName) {
  const binary = process.env.XELATEX ?? 'xelatex'
  for (let pass = 1; pass <= 2; pass += 1) {
    const result = spawnSync(binary, ['-interaction=nonstopmode', '-halt-on-error', '-file-line-error', texName], {
      cwd: outputDirectory,
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'pipe'],
    })
    if (result.error) throw new Error(`无法运行 XeLaTeX：${result.error.message}`)
    if (result.status !== 0) {
      const output = `${result.stdout ?? ''}\n${result.stderr ?? ''}`.trim()
      throw new Error(`XeLaTeX 第 ${pass} 次编译失败：\n${output.split('\n').slice(-24).join('\n')}`)
    }
  }
}

function notePath(course, item) {
  const source = (item.outputs ?? []).find((output) => output.id === 'lecture-note')?.source
  if (source) return resolve(repoRoot, source)
  return join(repoRoot, course.paths.notes, item.id, 'note.md')
}

function exportItem(course, item) {
  const source = notePath(course, item)
  if (!existsSync(source)) throw new Error(`找不到 Lecture Note：${relativeToRepo(source)}`)
  const outputDirectory = join(repoRoot, course.paths.root, 'exports', 'latex', item.id)
  rmSync(outputDirectory, { recursive: true, force: true })
  mkdirSync(outputDirectory, { recursive: true })
  copyTemplateStyles(outputDirectory)
  const markdown = readFileSync(source, 'utf8')
  const converted = markdownToLatex(markdown, { noteDirectory: dirname(source), outputDirectory })
  const texPath = join(outputDirectory, `${item.id}.tex`)
  write(texPath, makeTex({ course, item, title: converted.title, body: converted.body }))
  runXeLatex(outputDirectory, `${item.id}.tex`)

  const publicDirectory = join(publicRoot, course.id, item.id)
  rmSync(publicDirectory, { recursive: true, force: true })
  mkdirSync(publicDirectory, { recursive: true })
  for (const name of readdirSync(outputDirectory)) {
    const sourcePath = join(outputDirectory, name)
    if (name.endsWith('.aux') || name.endsWith('.log') || name.endsWith('.toc') || name.endsWith('.out')) continue
    const destination = join(publicDirectory, name)
    if (existsSync(sourcePath) && !sourcePath.endsWith('.pdf') && !sourcePath.endsWith('.tex') && !sourcePath.endsWith('.sty')) continue
    if (sourcePath.endsWith('.pdf') || sourcePath.endsWith('.tex') || sourcePath.endsWith('.sty')) copyFileSync(sourcePath, destination)
  }
  for (const name of ['styles', 'assets']) {
    const sourceDirectory = join(outputDirectory, name)
    if (!existsSync(sourceDirectory)) continue
    const destinationDirectory = join(publicDirectory, name)
    mkdirSync(destinationDirectory, { recursive: true })
    for (const file of readdirSync(sourceDirectory)) copyFileSync(join(sourceDirectory, file), join(destinationDirectory, file))
  }
  console.log(`LaTeX 导出完成：${relativeToRepo(texPath)}`)
  console.log(`PDF：${relativeToRepo(join(outputDirectory, `${item.id}.pdf`))}`)
}

function loadCourse(courseId) {
  const path = join(catalogRoot, `${courseId}.yaml`)
  if (!existsSync(path)) throw new Error(`找不到课程配置：${relativeToRepo(path)}`)
  return parse(readFileSync(path, 'utf8'))
}

function exportOne(courseId, lectureId) {
  const course = loadCourse(courseId)
  const item = (course.items ?? []).find((candidate) => candidate.id === lectureId)
  if (!item) throw new Error(`课程 ${courseId} 中找不到 ${lectureId}`)
  exportItem(course, item)
}

function exportConfigured() {
  for (const file of readdirSync(catalogRoot).filter((name) => name.endsWith('.yaml'))) {
    const course = parse(readFileSync(join(catalogRoot, file), 'utf8'))
    for (const item of course.items ?? []) if (item.exports?.length) exportItem(course, item)
  }
}

const [, , courseId, lectureId] = process.argv
try {
  if (courseId && lectureId) exportOne(courseId, lectureId)
  else exportConfigured()
} catch (error) {
  console.error(`latex export: ${error.message}`)
  process.exitCode = 1
}
