# Demo 2：四层记忆与提取器

源码位置：`examples/layered/index.ts`。

这个 Demo 仍然不调用 LLM，但手工写出四层数据：

```text
L0: 原始 user / assistant 消息
L1: 从原话提取出的 Atom
L2: 按项目场景拼成的 Markdown
L3: 稳定的用户回答偏好
```

## 运行

```bash
npm run demo:layered
```

## 关键观察

### L1 不是 L0 的复制品

L0 中 Assistant 的“收到，我会遵守”没有被提取；用户的工程约定和回答偏好才产生了 L1。

### L2 需要带来源

示例中的 Markdown 会把 `L0 #0` 写在后面。真实实现应使用稳定的 `source_message_ids`，而不是数组下标。

### L3 应该稳定

每一轮都将“用户喜欢先给结论”重复写进 Persona 没有意义；应当更新同一个字段，或在多次证据支持后提高置信度。

## 改造练习

把示例中的手工 `filter()` 换成：

```ts
interface Extractor {
  extract(messages: Message[]): Promise<Atom[]>
}
```

先写一个规则实现，再写一个假的 `MockLLMExtractor` 返回固定 JSON。你会发现，接口稳定后，提取策略可以自由替换。
