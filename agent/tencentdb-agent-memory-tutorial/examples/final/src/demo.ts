import { TinyMemory } from './memory.js'

const memory = await new TinyMemory().init()
const turns = [
  [{ role: 'user' as const, content: '这个项目使用 pnpm，测试命令是 pnpm test。' }, { role: 'assistant' as const, content: '收到。' }],
  [{ role: 'user' as const, content: '我喜欢先给结论，再给解释。' }, { role: 'assistant' as const, content: '之后我会遵守。' }],
  [{ role: 'user' as const, content: '项目后来改用 npm 了。' }, { role: 'assistant' as const, content: '我会更新工程约定。' }],
]

for (const [index, messages] of turns.entries()) {
  await memory.capture('session-demo', messages)
  const result = await memory.processPending()
  console.log(`turn ${index + 1}:`, result)
}

console.log('\nL1 atoms:')
console.dir(memory.snapshot().atoms, { depth: null })
console.log('\nRecall for "项目测试怎么跑？":')
console.log(memory.recall('项目测试怎么跑？').prompt)
