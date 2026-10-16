# 10. 运行、调试与验证

## 运行站点

```bash
cd tencentdb-agent-memory-tutorial
npm install
npm run dev
```

打开终端输出的本地地址即可浏览教程。

## 构建静态站点

```bash
npm run build
npm run preview
```

构建产物位于 `docs/.vitepress/dist`。

## 验证最终项目

```bash
npm run demo:final
```

重点观察三件事：

- 第二次执行不会重新处理已经处理过的 L0；
- “改用 npm”会更新同一个 `package-manager` Atom，而不是无限追加；
- recall 输出带 `<agent-memory>` 边界，并包含来源层级信息。

## 一个排查表

| 现象 | 排查顺序 |
| --- | --- |
| 没有记忆 | 查看 L0 是否写入，再看 `processedL0`，最后看提取规则 |
| 重复记忆 | 检查 checkpoint 是否在写入后更新，检查 `key` 是否稳定 |
| 召回不相关 | 打印 token、候选分数和 limit，不要只看最终 Prompt |
| Agent 被旧记忆带偏 | 给注入内容加“仅供参考”，并让当前用户消息优先 |
| 站点 Mermaid 不渲染 | 检查 `vitepress-plugin-mermaid` 是否安装以及配置是否使用 `withMermaid` |

## 建议加的测试

```text
capture 同一批消息两次       → L0 不重复
包含 <agent-memory> 的消息   → 不能把注入块写进 L0
旧值与新值冲突               → update 而不是无穷 store
Recall 超过 maxChars         → 输出被截断但仍是合法标记
空 Store / LLM 失败          → Agent 仍可运行
不同 identity                → 不互相召回
```
