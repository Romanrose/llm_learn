# Agent Memory 从零到一：TencentDB-Agent-Memory 教学项目

这是一个基于 VitePress 的中文渐进式教程，参考 [TencentCloud/TencentDB-Agent-Memory](https://github.com/TencentCloud/TencentDB-Agent-Memory) 的公开源码与文档，讲解 L0/L1/L2/L3 分层、L0 捕获、L1 提取与去重、BM25/向量/RRF 召回、短期上下文 offload，以及 Agent Hook/Gateway 接入链路。

本项目是 `agent/<project-id>/` 模板下的独立 Agent 教程，保留自己的 `docs/`、`examples/` 和 Node.js 依赖；它不会复制 CS336 的 Lecture 目录。网站目录由 `website/course.yaml` 统一登记，后续如果需要课程化，再按[统一项目结构](../../workflow/standards/project-structure.md)增加网站元数据。`docs/.vitepress/cache/`、`docs/.vitepress/dist/` 和 `node_modules/` 都是本地构建目录，不提交 Git。

## 快速开始

```bash
npm install
npm run dev
```

构建静态站点：

```bash
npm run build
npm run preview
```

运行渐进式 Demo：

```bash
npm run demo:basic
npm run demo:layered
npm run demo:hybrid
npm run demo:final
```

最终 Demo 使用 JSON 文件持久化，数据会写入 `examples/final/data/memory.json`，该目录已加入 `.gitignore`。

## 内容导航

- `docs/guide/`：原理、架构、源码拆解、生产化设计和最终项目。
- `docs/demos/`：四个由浅入深的小 Demo。
- `examples/final/src/memory.ts`：可直接阅读和改造的教学版 Memory Core。

## 说明

示例项目为了降低学习门槛，使用规则提取器、JSON Store 和轻量 token/n-gram 检索，不需要 API Key 或外部数据库。教程会明确指出这些组件在生产实现中应如何替换为 LLM、SQLite/向量数据库、Gateway 和 SDK。
