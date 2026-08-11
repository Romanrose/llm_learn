# 11. 从教学版走向生产

Tiny Memory 的代码故意短小，但生产化不是简单地“换个向量数据库”。建议按下面顺序扩展。

## 1. 先替换持久化层

抽象出：

```ts
interface MemoryStore {
  appendL0(records: L0Record[]): Promise<void>
  listPendingL0(cursor: Cursor): Promise<L0Record[]>
  upsertL1(atom: Atom): Promise<UpsertResult>
  searchL1(query: string, options: SearchOptions): Promise<Hit[]>
}
```

先保留 JSON Store 作为测试实现，再实现 SQLite Store。这样可以用同一套测试验证语义，不会被数据库细节绑住。

## 2. 接入真实 LLM，但不要让模型直接写库

推荐流程：

```text
LLM JSON → schema 校验 → 规范化 → 候选召回 → 冲突判定 → Store
```

模型只负责提出候选记忆和动作建议，最终写库由确定性代码完成。生产系统还应记录 prompt 版本、模型版本、来源和置信度。

## 3. 加上混合检索

- 精确字段、命令、错误码：BM25/FTS。
- 自然语言偏好、跨语言表达：Embedding。
- 多路结果：RRF。
- 结果过多：rerank、MMR 或 priority/recency 规则。

切记：Embedding 不是事实正确性判断，只是候选召回工具。

## 4. 引入 L2/L3 的文件化和审核

L2 可以使用 Markdown + index；L3 可以使用带版本的 Persona。每次归纳保留变更记录，支持人工查看“这条 Persona 是由哪些 L1 生成的”。

## 5. 加身份隔离和权限

把每一条 L0/L1 都绑定到 identity：

```ts
type Identity = {
  teamId: string
  agentId: string
  userId: string
  sessionId?: string
}
```

读写、候选去重、L2/L3 聚合都要带 scope；不能只在 HTTP 层校验一次，然后在底层 Store 忘记过滤。

## 6. 把短期 offload 独立出来

长期 Memory 和短期 Context Offload 的数据、保留时间、权限都不同。原始工具日志尤其不能默认成为长期 Persona。

## 7. 用评测驱动迭代

至少建立四类问题：

- 记住：新事实是否被提取？
- 找回：换一种说法能否召回？
- 更新：新事实能否覆盖旧事实？
- 不污染：无关问题是否少注入？

记录 recall@k、precision、注入 token、端到端延迟、L0→L1 延迟和错误降级次数。

## 最终检查清单

- [ ] 原始证据可追溯
- [ ] 写入幂等、游标安全
- [ ] 提取失败不影响主对话
- [ ] 检索有 BM25/向量降级
- [ ] Prompt 注入有预算和边界
- [ ] team/agent/user 隔离
- [ ] L2/L3 有版本、来源和回滚
- [ ] offload 文件有权限和清理策略
- [ ] 有真实任务集和回归评测
