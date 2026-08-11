type Message = { role: 'user' | 'assistant'; content: string }
type Atom = { layer: 'L1'; content: string; source: number }

const l0: Message[] = [
  { role: 'user', content: '这个项目使用 pnpm，测试命令是 pnpm test。' },
  { role: 'assistant', content: '收到，我会遵守项目约定。' },
  { role: 'user', content: '我喜欢先给结论，再给解释。' },
]

const l1: Atom[] = l0
  .map((message, source) => message.content)
  .filter((text) => /使用|喜欢|偏好|命令/.test(text))
  .map((content, source) => ({ layer: 'L1' as const, content, source }))

const l2 = `# 项目工程约定\n\n${l1.map((atom) => `- ${atom.content}（来源 L0 #${atom.source}）`).join('\n')}`
const l3 = '用户偏好：回答先给结论，再给解释。'

console.log({ L0: l0, L1: l1, L2: l2, L3: l3 })
