import fs from 'node:fs'
import { spawn } from 'node:child_process'
import { createHash } from 'node:crypto'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { parse as yaml, stringify } from 'yaml'
import { parse as javascript } from '@babel/parser'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '../..')
const configPath = join(root, 'workflow/config/course-updates.yaml')
const today = new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Shanghai', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date())
const norm = s => String(s ?? '').toLowerCase().replace(/[^\p{L}\p{N}]+/gu, '')
const unique = xs => [...new Map(xs.filter(x => x?.url).map(x => [x.url, x])).values()]
export function semesterMatches(html, url, expected) {
  const visible = html.replace(/<(script|style)\b[\s\S]*?<\/\1>/gi,'').replace(/<[^>]+>/g,' ').replace(/\s+/g,' ')
  // A past-offering link later in the page must not satisfy the active banner.
  const active = visible.slice(0,1600).match(/\b(Fall|Autumn|Spring|Winter|Summer)\s*[·•-]?\s*(20\d\d)\b/i)
  if (active && !/^(?:fall|autumn)$/i.test(active[1])) return false
  if (active && active[2] !== '2026') return false
  const description = [...html.matchAll(/<meta\b[^>]*name=["']description["'][^>]*content=["']([^"']*)/gi)].map(m=>m[1]).join(' ')
  return new RegExp(expected,'i').test(visible.slice(0,1600) + ' ' + description + ' ' + url)
}
const month = ['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec']
export function dateKey(value, year = 2026) {
  if (/^\d{4}-\d{2}-\d{2}$/.test(value ?? '')) return value
  const m = String(value ?? '').match(/(Jan\w*|Feb\w*|Mar\w*|Apr\w*|May|Jun\w*|Jul\w*|Aug\w*|Sep\w*|Oct\w*|Nov\w*|Dec\w*)\s+(\d{1,2})/i)
  return m ? `${year}-${String(month.indexOf(m[1].slice(0,3).toLowerCase())+1).padStart(2,'0')}-${m[2].padStart(2,'0')}` : ''
}
export function literal(node) {
  if (['StringLiteral','NumericLiteral','BooleanLiteral'].includes(node?.type)) return node.value
  if (node?.type === 'NullLiteral') return null
  if (node?.type === 'ArrayExpression') return node.elements.map(literal)
  if (node?.type === 'ObjectExpression') return Object.fromEntries(node.properties.map(p => {
    if (p.type !== 'ObjectProperty' || p.computed) throw Error('Nonliteral property in course data')
    return [p.key.name ?? p.key.value, literal(p.value)]
  }))
  if (node?.type === 'UnaryExpression' && node.operator === '!') return !literal(node.argument)
  throw Error('Executable expression rejected in course data')
}
export function bundleSessions(source) {
  const ast = javascript(source, { sourceType: 'module', attachComment: false })
  const found = []
  for (const statement of ast.program.body) {
    if (statement.type !== 'VariableDeclaration') continue
    for (const declaration of statement.declarations) {
      const n = declaration.init
      if (n?.type !== 'ArrayExpression' || n.elements.length < 2 || n.elements[0]?.type !== 'ObjectExpression') continue
      const keys = n.elements[0].properties.map(p => p.key?.name ?? p.key?.value)
      if (keys.includes('date') && keys.includes('title') && keys.includes('code')) found.push(literal(n))
    }
  }
  if (found.length !== 1) throw Error('Official session data layout changed')
  return found[0]
}
function parseHtml(html, url) {
  return new Promise((yes, no) => {
    const child = spawn(process.env.PYTHON ?? 'python3', [join(root,'workflow/scripts/parse-course-page.py')], { stdio: ['pipe','pipe','pipe'] })
    let out = '', err = ''; const timer = setTimeout(() => { child.kill(); no(Error('HTML parser timeout')) }, 15000)
    child.stdout.on('data', chunk => { out += chunk }); child.stderr.on('data', chunk => { err += chunk })
    child.on('error', no); child.on('close', code => { clearTimeout(timer); if (code) no(Error(err)); else { try { yes(JSON.parse(out)) } catch (e) { no(e) } } })
    child.stdin.end(JSON.stringify({ html, url }))
  })
}
async function text(url) {
  for (let attempt = 0; attempt < 2; attempt++) {
    try {
      const response = await fetch(url, { headers: { 'user-agent': 'llm_learn-course-updater/1.0 (+https://github.com/Romanrose/llm_learn)' }, signal: AbortSignal.timeout(20000) })
      if (!response.ok) throw Error(`HTTP ${response.status}: ${url}`)
      if (new URL(response.url).hostname !== new URL(url).hostname) throw Error('Official source redirected to another host')
      const documentPath = value => new URL(value).pathname.replace(/\/index\.html$/,'/').replace(/\/$/,'')
      if (documentPath(response.url) !== documentPath(url)) throw Error('Official source redirected to another document or semester')
      const mime = response.headers.get('content-type') ?? ''
      if (!/text|javascript|json/.test(mime)) throw Error('Source is not an HTML/data document')
      const body = await response.text(); if (body.length > 4_000_000) throw Error('Unexpectedly large source document')
      return body
    } catch (e) { if (attempt === 1) throw e }
  }
}
function type(link) {
  return /youtu|vimeo|panopto|\.mp4(?:\?|$)/i.test(link.url) ? 'video' : /arxiv|openreview|proceedings/i.test(link.url) ? 'paper' : /github|\.(?:zip|tar|py|ipynb)(?:\?|$)/i.test(link.url) ? 'code' : /slides|lectures|\.pptx/i.test(link.url) ? 'slides' : 'docs'
}
const links = cell => cell?.links ?? []
const clean = title => title.replace(/\[[^\]]*\]/g,'').replace(/\s*\((?:\s*(?:pdf|pptx|code|,|slides)\s*)+\)\s*$/i,'').trim()
function candidates(page, adapter) {
  const result = []; const practices = []
  const row = (title, date, resources, readings = [], id) => result.push({ title: clean(title), date, resources, readings, id })
  for (const r of page.rows) {
    if (adapter === 'cs61a' && r.length === 3) {
      const m = r[1].text.match(/^Lecture\s+(\d+)\s+/)
      if (m) row(r[1].headings?.[0] ?? r[1].text, r[0].text, links(r[1]), links(r[2]), `lecture-${m[1].padStart(2,'0')}`)
      practices.push(...links(r[1]).filter(l => /\/fa26\/(?:labs|hw|projects)\//.test(l.url)))
    } else if (adapter === 'cmu213' && r.length === 7 && month.includes(r[1].text.toLowerCase().slice(0,3))) {
      if (!/Recitation|Bootcamp|No class|Exam|Review/i.test(r[3].text)) row(r[3].text.replace(/\s*\([^)]*(?:pdf|pptx)[^)]*\)/i,''), `${r[1].text} ${r[2].text}`, links(r[3]))
      practices.push(...links(r[3]).filter(l => /^L\d+-writeup/i.test(l.label)))
    } else if (adapter === 'cs2680' && r.length === 6 && /^2026-/.test(r[1].text)) {
      if (!/poster|presentation|student sharing/i.test(r[3].text)) row(r[3].text, r[1].text, links(r[3]), links(r[4]))
      practices.push(...links(r[5]).filter(l => /\/assignments\/assignment\d+(?:\.html)?$/.test(l.url)))
    } else if (adapter === 'cs329z' && r.length === 4 && dateKey(r[1].text)) {
      const title = r[2].headings?.at(-1) || r[2].text
      if (!/No Class|Holiday|Poster|Presentation|Review Session/i.test(title)) row(title, r[1].text, links(r[2]).filter(l => /slides|lecture\d+\.pdf/i.test(l.url)), links(r[3]))
    } else if (adapter === 'cs329x' && r.length === 4 && dateKey(r[1].text) && /^\d+$/.test(r[0].text)) {
      if (!/No Class|Holiday|Showcase|Presentation/i.test(r[2].text)) row(r[2].text, r[1].text, links(r[2]).filter(l => /slides/i.test(l.label)), links(r[3]))
    } else if (adapter === 'jhu' && r.length === 5 && dateKey(r[0].text)) {
      if (!/No class/i.test(r[1].text)) row(r[1].text, r[0].text, links(r[3]), links(r[4]))
    }
  }
  if (adapter === 'mit-tinyml') {
    for (const card of page.cards) {
      const title = card.headings.filter(Boolean).at(-1)
      if (/Lecture \d+\s*:/.test(card.text) && !/Chapter [IVX]+:|Holiday|Thanksgiving|Presentation/i.test(title)) row(title, card.text, card.links.filter(l => /slides/i.test(l.label)))
    }
    practices.push(...page.links.filter(l => /^Lab\s+\d+$/.test(l.label)))
  }
  if (adapter === 'cs147') {
    for (const l of page.links.filter(l => /\/assignments\/assignment\d+_26\.pdf$/.test(l.url))) {
      const n = l.url.match(/assignment(\d+)_/)[1]
      row(l.label, '', [l], [], `assignment-${n.padStart(2,'0')}`); practices.push(l)
    }
    const lectures = page.links.filter(l => /\/lectures\/\d+[^/]+\.pdf$/.test(l.url))
    for (const l of lectures) row(l.label, '', [l, ...page.links.filter(x => x.url === l.url.replace(/\.pdf$/,'.pptx'))])
  }
  return { units: result, practices: unique(practices) }
}
function matchingItem(course, candidate) {
  if (candidate.id) return course.items.find(i => i.id === candidate.id)
  const urls = new Set(candidate.resources.map(l => l.url))
  const byResource = course.items.filter(i => [...i.resources ?? [], ...i.readings ?? [], ...i.official ?? []].some(l => urls.has(l.url)))
  if (byResource.length === 1) return byResource[0]
  const sameTitle = course.items.filter(i => norm(i.title) === norm(candidate.title))
  if (sameTitle.length === 1) return sameTitle[0]
  const byDate = candidate.date ? course.items.filter(i => dateKey(i.date) && dateKey(i.date) === dateKey(candidate.date)) : []
  return byDate.length === 1 ? byDate[0] : undefined
}
function safeLink(link) {
  if (!link?.url || !link.label || link.label.length > 600) return false
  try { const u = new URL(link.url); return ['https:','http:'].includes(u.protocol) && !u.username && !u.password && !/[<>\n\r]/.test(link.label + link.url) } catch { return false }
}
export function mergeOfficial(course, parsed, config, checkedAt = today) {
  const next = structuredClone(course); const changes = []
  const allBefore = new Set([...(course.practice ?? []), ...course.items.flatMap(i => [...i.resources ?? [], ...i.readings ?? [], ...i.official ?? []])].map(x => x.url))
  const add = (item, field, list) => {
    const existing = new Set([...item.resources ?? [], ...item.readings ?? [], ...item.official ?? []].map(x => x.url))
    for (const l of unique(list).filter(safeLink)) {
      if (existing.has(l.url)) continue
      item[field] ??= []
      item[field].push({ label: l.label, url: l.url, type: type(l), note: `官方课程页面新增资料；来源：${config.url}；核对：${checkedAt}。${type(l)==='video' && config.adapter==='cs61a' ? '配套主题视频，不作为当期课堂录像。' : ''}` })
      existing.add(l.url); changes.push({ unit: item.id, label: l.label, url: l.url })
    }
  }
  let matched = 0
  for (const candidate of parsed.units) {
    let item = matchingItem(next, candidate)
    if (!item) {
      // A dated new session or a CS147 official lecture PDF can establish a new unit.
      const dated = dateKey(candidate.date)
      const cs147Lecture = config.adapter === 'cs147' && candidate.resources.some(l => /\/lectures\/\d+.*\.pdf$/.test(l.url))
      if ((!dated && !cs147Lecture) || !candidate.resources.length || /TBA|Guest Lecture|Student sharing/i.test(candidate.title)) continue
      if (candidate.resources.every(l => allBefore.has(l.url))) continue
      const order = Math.max(0, ...next.items.map(i => Number(i.order) || 0)) + 1
      const id = `lecture-${String(order).padStart(2,'0')}`
      if (next.items.some(i => i.id === id)) throw Error('New unit ID would collide')
      item = { id, order, displayOrder: order, unitLabel: next.unitLabel ?? '单元', ...(dated ? { date: dated } : {}), title: candidate.title, subtitle: '课程官网新增单元；当前接入官方资料。', status: dated && dated > checkedAt ? 'scheduled' : 'resources-approved', official: [{ label: '官方课程表', url: config.url }], resources: [], readings: [], outputs: [] }
      next.items.push(item)
      if (next.learningModules?.length) next.learningModules.at(-1).to = Math.max(next.learningModules.at(-1).to ?? 0, order)
      changes.push({ unit: id, label: '新增单元：' + candidate.title })
    }
    matched++
    add(item, 'resources', candidate.resources); add(item, 'readings', candidate.readings)
    if (item.status === 'scheduled' && (item.resources?.length || item.readings?.length) && (!dateKey(item.date) || dateKey(item.date) <= checkedAt)) item.status = 'resources-approved'
  }
  if (matched < Math.min(3, course.items.length)) throw Error(`Too few matched units (${matched}); source layout may have changed`)
  next.practice ??= []
  for (const p of parsed.practices.filter(safeLink)) {
    // Existing curated GitHub assignments take precedence over newly seen handouts.
    const number = p.url.match(/assignment(\d+)/)?.[1]
    if (number && next.practice.some(x => x.id === `assignment-${number}` || x.id === `assignment-${number.padStart(2,'0')}`)) continue
    if (next.practice.some(x => x.url === p.url)) continue
    const id = 'official-' + createHash('sha256').update(p.url).digest('hex').slice(0,16)
    if (next.practice.some(x => x.id === id)) throw Error('Practice ID collision')
    next.practice.push({ id, title: p.label, url: p.url, source: config.url, checkedAt, note: '课程官网公布的作业 / Lab 入口；访问权限和题目版本以原站为准。' })
    changes.push({ unit: 'practice', label: p.label, url: p.url })
  }
  // No timestamp-only commits; never touch reviewed content or publication settings.
  if (!changes.length) return { course, changes }
  next.schedule ??= {}; next.schedule.resourceUpdatedAt = checkedAt; next.schedule.unitCount = next.items.length
  return { course: next, changes }
}
async function run() {
  const apply = process.argv.includes('--apply')
  const only = process.argv.find(x => x.startsWith('--course='))?.split('=')[1]
  const configs = yaml(fs.readFileSync(configPath,'utf8')).courses
  const results = []; const prepared = []
  for (const config of configs.filter(c => !only || c.id === only)) {
    if (today > String(config.until)) { results.push({ id: config.id, status: 'retired', changes: [] }); continue }
    try {
      const path = join(root,`website/catalog-data/courses/${config.id}.yaml`)
      const course = yaml(fs.readFileSync(path,'utf8'))
      const html = await text(config.url)
      const identity = config.identityUrl ? await text(config.identityUrl) : html + ' ' + config.url
      if (!semesterMatches(identity,config.identityUrl ?? config.url,config.semester)) throw Error('Pinned semester no longer matches official page')
      const page = await parseHtml(html,config.url)
      let parsed
      if (config.adapter === 'cmu-agents') {
        const src = page.scripts.find(u => new URL(u).hostname === new URL(config.url).hostname && /\/assets\/index-.*\.js$/.test(u))
        if (!src) throw Error('Official course data bundle missing')
        const sessions = bundleSessions(await text(src))
        parsed = { units: sessions.filter(s => s.slides || s.recording || s.readings?.length).map(s => ({ title: s.title, date: s.date, resources: unique([s.slides,s.recording].filter(Boolean).map(l => ({ ...l, url: new URL(l.url,config.url).href }))), readings: s.readings ?? [] })), practices: [] }
      } else parsed = candidates(page,config.adapter)
      const updated = mergeOfficial(course,parsed,config)
      if (updated.changes.length) prepared.push({ path, updated, config })
      results.push({ id: config.id, status: updated.changes.length ? 'updated' : 'unchanged', changes: updated.changes })
    } catch (e) { results.push({ id: config.id, status: 'error', error: e.message, changes: [] }) }
  }
  const report = ['# 课程官方资料更新', '', `检查日期：${today} · ${apply ? '同步' : '预览'}模式`, '', ...results.flatMap(r => [`## ${r.id} · ${r.status}`, ...(r.error ? [`\n${r.error}\n`] : []), ...r.changes.map(c => `- ${c.unit} · ${c.label}${c.url ? ` · ${c.url}` : ''}`), ''])].join('\n')
  if (process.env.GITHUB_STEP_SUMMARY) fs.appendFileSync(process.env.GITHUB_STEP_SUMMARY,report)
  console.log(JSON.stringify(results,null,2))
  // Any parsing/semester/network error aborts writes: a broken source cannot partially publish a batch.
  if (results.some(r => r.status === 'error')) { process.exitCode = 1; return }
  if (apply) for (const { path, updated, config } of prepared) {
    fs.writeFileSync(path,stringify(updated.course,{ lineWidth:0 }))
    const manifestPath = join(root,updated.course.paths.resources,'manifest.yaml')
    const manifest = fs.existsSync(manifestPath) ? yaml(fs.readFileSync(manifestPath,'utf8')) : { schemaVersion:1,course:config.id,state:'linked',resources:[] }
    manifest.resources ??= []
    for (const change of updated.changes.filter(x => x.url)) if (!manifest.resources.some(x => x.url === change.url)) manifest.resources.push({ label: change.label,url:change.url,type:type(change),source:config.url,status:'linked',local:null })
    manifest.resourceUpdatedAt = today; fs.mkdirSync(dirname(manifestPath),{ recursive:true }); fs.writeFileSync(manifestPath,stringify(manifest,{ lineWidth:0 }))
  }
  if (process.env.GITHUB_OUTPUT) fs.appendFileSync(process.env.GITHUB_OUTPUT,`changed=${apply && prepared.length>0}\n`)
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) await run()
