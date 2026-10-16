type Hit = { id: string; text: string }

function rrfMerge(lists: Hit[][], k = 60) {
  const scores = new Map<string, { hit: Hit; score: number }>()
  lists.forEach((list) => list.forEach((hit, rank) => {
    const previous = scores.get(hit.id)
    const score = 1 / (k + rank + 1)
    scores.set(hit.id, { hit, score: (previous?.score ?? 0) + score })
  }))
  return [...scores.values()].sort((a, b) => b.score - a.score)
}

const keyword: Hit[] = [
  { id: 'a', text: '项目测试命令是 pnpm test' },
  { id: 'b', text: '用户喜欢先给结论' },
]
const semantic: Hit[] = [
  { id: 'a', text: '项目测试命令是 pnpm test' },
  { id: 'c', text: '项目发布前要先跑检查' },
]
console.log(rrfMerge([keyword, semantic]))
