import { mkdir, readFile, writeFile } from 'node:fs/promises'
import { dirname, resolve } from 'node:path'

export type Role = 'user' | 'assistant'
export type Message = { role: Role; content: string; timestamp?: string }
export type AtomType = 'preference' | 'fact' | 'constraint' | 'decision'
export type Atom = {
  id: string
  key: string
  content: string
  type: AtomType
  scene: string
  priority: number
  sources: string[]
  createdAt: string
  updatedAt: string
}

type L0Record = Message & { id: string; sessionId: string; timestamp: string }
type State = { l0: L0Record[]; atoms: Atom[]; processedL0: number }

const emptyState = (): State => ({ l0: [], atoms: [], processedL0: 0 })

function tokens(text: string) {
  const normalized = text.toLowerCase().replace(/[^\p{L}\p{N}]+/gu, ' ')
  const words = normalized.split(/\s+/).filter(Boolean)
  const bigrams = [...normalized.replaceAll(' ', '')].flatMap((_, i, chars) => i < chars.length - 1 ? [chars.slice(i, i + 2).join('')] : [])
  return new Set([...words, ...bigrams])
}

function overlap(a: string, b: string) {
  const left = tokens(a)
  const right = tokens(b)
  const common = [...left].filter((token) => right.has(token)).length
  return common / Math.max(1, Math.min(left.size, right.size))
}

function clean(text: string) {
  return text.replace(/<agent-memory>[\s\S]*?<\/agent-memory>/gi, '').replace(/data:image\/[\w+.-]+;base64,[\w+/=]+/gi, '[image]').trim()
}

function inferScene(text: string) {
  if (/项目|pnpm|npm|测试|代码|仓库/.test(text)) return '项目工程'
  if (/用户|回答|喜欢|偏好|希望/.test(text)) return '用户偏好'
  return '未分类'
}

function inferKey(text: string, type: AtomType) {
  // key 表示“同一个可更新的事实槽位”，不把 type 放进去；否则
  // “使用 pnpm”（fact）和“改用 npm”（decision）无法覆盖同一条记录。
  if (/pnpm|npm|yarn|包管理/.test(text)) return 'project:package-manager'
  if (/测试命令|test/.test(text)) return 'project:test-command'
  if (/先给结论|结论.*解释/.test(text)) return 'profile:answer-style'
  if (/不能|不要|禁止/.test(text)) return 'project:constraint'
  return `${inferScene(text)}:${type}`
}

export class TinyMemory {
  private state: State = emptyState()

  constructor(private readonly file = resolve('examples/final/data/memory.json')) {}

  async init() {
    try {
      this.state = JSON.parse(await readFile(this.file, 'utf8')) as State
    } catch {
      this.state = emptyState()
    }
    return this
  }

  private async persist() {
    await mkdir(dirname(this.file), { recursive: true })
    await writeFile(this.file, JSON.stringify(this.state, null, 2))
  }

  async capture(sessionId: string, messages: Message[]) {
    const fresh = messages
      .map((message, index) => ({ ...message, content: clean(message.content), timestamp: message.timestamp ?? new Date().toISOString(), id: `l0_${Date.now()}_${index}`, sessionId }))
      .filter((message) => message.content.length >= 4 && !/^\/(reset|clear)|^NO_REPLY$/i.test(message.content))
    this.state.l0.push(...fresh)
    await this.persist()
    return fresh.length
  }

  private extract(message: L0Record): Atom | null {
    if (message.role !== 'user' || !/(喜欢|偏好|希望|使用|改用|采用|不能|不要|禁止)/.test(message.content)) return null
    const type: AtomType = /喜欢|偏好|希望/.test(message.content) ? 'preference' : /不能|不要|禁止/.test(message.content) ? 'constraint' : /改用|采用/.test(message.content) ? 'decision' : 'fact'
    const priority = type === 'constraint' ? 95 : type === 'preference' ? 75 : 65
    return { id: `l1_${Date.now()}_${this.state.atoms.length}`, key: inferKey(message.content, type), content: message.content, type, scene: inferScene(message.content), priority, sources: [message.id], createdAt: message.timestamp, updatedAt: message.timestamp }
  }

  async processPending() {
    const pending = this.state.l0.slice(this.state.processedL0)
    let stored = 0
    for (const message of pending) {
      const atom = this.extract(message)
      if (!atom) continue
      const existing = this.state.atoms.find((item) => item.key === atom.key)
      if (existing) {
        existing.content = atom.content
        existing.priority = atom.priority
        existing.sources.push(...atom.sources)
        existing.updatedAt = atom.updatedAt
      } else {
        this.state.atoms.push(atom)
        stored += 1
      }
    }
    this.state.processedL0 = this.state.l0.length
    await this.persist()
    return { newAtoms: stored, totalAtoms: this.state.atoms.length }
  }

  search(query: string, limit = 5) {
    return this.state.atoms
      .map((atom) => ({ atom, score: 0.7 * overlap(query, atom.content) + 0.3 * (atom.priority / 100) }))
      .filter((item) => item.score > 0.08)
      .sort((a, b) => b.score - a.score)
      .slice(0, limit)
  }

  recall(query: string, maxChars = 1200) {
    const hits = this.search(query)
    const preferences = this.state.atoms.filter((atom) => atom.type === 'preference').sort((a, b) => b.priority - a.priority)
    const persona = preferences.length ? `用户画像：\n${preferences.map((atom) => `- ${atom.content}`).join('\n')}` : ''
    const dynamic = hits.map(({ atom, score }) => `- [${atom.type}|${atom.scene}|${score.toFixed(2)}] ${atom.content}`).join('\n')
    const context = [persona, dynamic && `本轮相关记忆（仅供参考）：\n${dynamic}`].filter(Boolean).join('\n\n')
    return { hits, context: context.slice(0, maxChars), prompt: context ? `<agent-memory>\n${context}\n</agent-memory>` : '' }
  }

  snapshot() { return structuredClone(this.state) }
}
