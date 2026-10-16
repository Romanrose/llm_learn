---
layout: home
hero:
  name: Agent Memory 从零到一
  text: 读懂 TencentDB-Agent-Memory，并亲手做出一个可运行的教学版
  tagline: 把“记住一切”变成“留下有用的证据，在正确的时机取对的信息”。
  actions:
    - theme: brand
      text: 开始学习
      link: /guide/01-why-memory
    - theme: alt
      text: 直接看最终项目
      link: /guide/09-final-project
features:
  - icon: 🧭
    title: 先建立心智模型
    details: 从上下文窗口、L0～L3 分层、召回预算开始，理解为什么 Memory 不是“把聊天记录塞进向量库”。
  - icon: 🧪
    title: 四个渐进式 Demo
    details: 先做内存字典，再加入分层、去重、混合检索和 Agent Hook，每一步都能运行、观察和修改。
  - icon: 🛠️
    title: 最终可运行项目
    details: Tiny Memory 使用 JSON 文件持久化，不需要 API Key 或数据库，完整走通 capture → extract → recall → inject。
---

## 这套教程适合谁？

如果你已经会 Python 或 TypeScript，理解基本的数据结构、HTTP 和异步编程，就可以跟着完成。教程会把官方工程里的复杂部分分成三类：

| 教程层 | 目标 | 对应官方思想 |
| --- | --- | --- |
| 概念层 | 知道什么该存、什么时候取 | L0/L1/L2/L3 分层、渐进式披露 |
| 机制层 | 能写出提取、去重、检索与注入 | L0 捕获、L1 Pipeline、BM25/向量/RRF |
| 工程层 | 能把 Memory 接到 Agent | Gateway、SDK、Adapter、Hook、隔离与降级 |

## 学完后你会得到什么？

你会在本地拥有一个最小但完整的 Agent Memory：

```text
用户/Agent 回合
      │
      ├── capture：保存原始对话（L0）
      ├── extract：提取事实并去重（L1）
      ├── summarize：聚合场景与画像（L2/L3）
      └── recall：搜索 + 预算控制 + Prompt 注入
```

开始前先读 [为什么 Agent 需要 Memory](/guide/01-why-memory)。
