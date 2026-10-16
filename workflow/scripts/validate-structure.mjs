import { existsSync, readFileSync, readdirSync } from 'node:fs'
import { dirname, join, relative, resolve, sep } from 'node:path'
import { fileURLToPath } from 'node:url'
import assert from 'node:assert/strict'
import { parse } from 'yaml'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '../..')
const catalogRoot = join(root, 'website/catalog-data/courses')
const site = parse(readFileSync(join(root, 'website/course.yaml'), 'utf8'))
const groups = new Map([
  ['foundation-courses', 'foundations'],
  ['llm-courses', 'models-agents'],
  ['software-product', 'software-product'],
  ['robotics-hardware', 'robotics-hardware'],
])
const courses = new Map()
let publishedOutputs = 0

function insideRoot(value) {
  assert.equal(typeof value, 'string', `Invalid source path: ${value}`)
  const path = resolve(root, value)
  assert(path.startsWith(root + sep), `Path leaves repository: ${value}`)
  return path
}

for (const file of readdirSync(catalogRoot).filter(file => file.endsWith('.yaml'))) {
  const course = parse(readFileSync(join(catalogRoot, file), 'utf8'))
  assert.equal(file, `${course.id}.yaml`)
  assert(!courses.has(course.id), `Duplicate course: ${course.id}`)
  courses.set(course.id, course)
  assert(/^courses\/(foundations|models-agents|software-product|robotics-hardware)\/[^/]+$/.test(course.paths?.root), `Invalid course root: ${course.id}`)
  assert.equal(course.paths.root.split('/').at(-1), course.id)
  assert(existsSync(join(insideRoot(course.paths.root), 'README.md')), `Missing course README: ${course.id}`)
  for (const value of Object.values(course.paths)) {
    insideRoot(value)
    assert(value === course.paths.root || value.startsWith(course.paths.root + '/'), `Path outside course workspace: ${value}`)
  }
  const itemIds = new Set()
  for (const item of course.items ?? []) {
    assert(!itemIds.has(item.id), `Duplicate unit: ${course.id}/${item.id}`)
    itemIds.add(item.id)
    // Hidden outputs may point to local drafts absent from a clean checkout.
    if (course.publishOutputs === false) continue
    for (const output of item.outputs ?? []) {
      assert(existsSync(insideRoot(output.source)), `Missing published source: ${output.source}`)
      assert(output.source.startsWith(course.paths.root + '/'), `Published source belongs to another workspace: ${output.source}`)
      publishedOutputs++
    }
  }
}

const registered = new Set()
for (const section of site.sections) {
  assert(groups.has(section.id), `Unknown homepage section: ${section.id}`)
  for (const entry of section.items) {
    for (const version of [entry, ...(entry.versions ?? [])]) {
      const course = courses.get(version.courseId)
      assert(course, `Homepage references missing course: ${version.courseId}`)
      assert(!registered.has(course.id), `Duplicate homepage course/version: ${course.id}`)
      registered.add(course.id)
      assert.equal(course.paths.root, `courses/${groups.get(section.id)}/${course.id}`)
      assert.equal(version.route, `/generated/courses/${course.id}/`)
    }
  }
}
assert.equal(registered.size, courses.size, 'Catalog and homepage course versions differ')

// Check the maintained GitHub entry documents, without imposing new rules on upstream projects.
const docs = ['README.md', 'courses/README.md', 'references/README.md', ...[...groups.values()].map(group => `courses/${group}/README.md`)]
for (const doc of docs) {
  for (const match of readFileSync(join(root, doc), 'utf8').matchAll(/\]\(([^)]+)\)/g)) {
    const target = match[1].split('#')[0]
    if (!target || /^(?:[a-z]+:|\/)/i.test(target)) continue
    const path = resolve(root, dirname(doc), decodeURIComponent(target))
    assert(existsSync(path), `Broken local link in ${doc}: ${relative(root, path)}`)
  }
}

console.log(`Structure valid: ${courses.size} course versions, ${site.sections.length} sections, ${publishedOutputs} published sources; README links resolve.`)
