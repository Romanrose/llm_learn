# Demo 1：内存中的记忆本

先不碰 LLM、数据库和向量。我们只做两个方法：`remember()` 和 `recall()`。

源码位置：`examples/basic/index.ts`。

## 运行

```bash
npm install
npm run demo:basic
```

## 最小实现

```ts
type Memory = { id: number; text: string; createdAt: string }

class BasicMemory {
  private memories: Memory[] = []

  remember(text: string) {
    this.memories.push({ id: this.memories.length + 1, text, createdAt: new Date().toISOString() })
  }

  recall(query: string) {
    return this.memories.filter((memory) => memory.text.includes(query))
  }
}
```

## 这个 Demo 教会了什么？

- Memory 至少需要持久化内容、时间和 ID。
- 召回是一个独立动作，不应该隐含在 `remember()` 里。
- 直接字符串查找只能演示接口，不能解决“测试命令”和“怎么跑测试”的语义差异。

## 故意保留的缺陷

1. 进程退出后全部丢失。
2. 没有 L0/L1 区分。
3. 没有去重，重复调用会重复存储。
4. 没有预算，可能把所有内容都返回。

下一步我们把数据分层。
