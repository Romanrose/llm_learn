# Demo 4：接入一个 Agent Loop

现在把 recall 和 capture 放到 Agent Loop 的正确位置：

```ts
for await (const userText of input) {
  const recall = await memory.recall(userText)
  const prompt = [recall.prompt, userText].filter(Boolean).join('\n\n')

  const answer = await agent.run(prompt)
  console.log(answer)

  await memory.capture(sessionId, [
    { role: 'user', content: userText },
    { role: 'assistant', content: answer },
  ])
  await memory.processPending()
}
```

## 两个必须坚持的时机

### Recall 在模型调用前

否则模型已经回答完了，记忆无法影响本轮决策。

### Capture 在模型调用后

这样可以保存本轮新增的用户信息和 Agent 结果。注意不要把 `<agent-memory>` 注入块原样保存，最终项目的 `clean()` 会先移除它。

## 不要让 Memory 变成第二个 Agent

Memory 层应该返回结构化上下文，主 Agent 决定如何使用；Memory 不应该自己执行用户任务，也不应该在每次 recall 时触发复杂的自主循环。
