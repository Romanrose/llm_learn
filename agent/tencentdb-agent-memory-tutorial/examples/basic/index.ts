type Memory = { id: number; text: string; createdAt: string }

class BasicMemory {
  private memories: Memory[] = []

  remember(text: string) {
    this.memories.push({ id: this.memories.length + 1, text, createdAt: new Date().toISOString() })
  }

  recall(query: string) {
    const words = query.toLowerCase().split(/\s+/)
    return this.memories
      .map((memory) => ({ memory, score: words.filter((word) => memory.text.toLowerCase().includes(word)).length }))
      .filter((item) => item.score > 0)
      .sort((a, b) => b.score - a.score)
      .map((item) => item.memory)
  }
}

const memory = new BasicMemory()
memory.remember('项目使用 pnpm，测试命令是 pnpm test')
memory.remember('用户喜欢先给结论，再给解释')
console.log(memory.recall('pnpm test'))
