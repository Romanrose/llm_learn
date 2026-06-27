# LLM 共学项目

大模型学习共同体 — 一起学习 LLM 理论与应用。

## 📁 项目结构

```
llm/
├── agent/                  # Agent 学习
│   ├── hello-agents/       # 《Hello Agents》课程（来自 datawhalechina/hello-agents）
│   ├── memory/             # 个人知识记忆
│   └── system/             # 系统配置
├── cs336/                  # CS336 课程 — Stanford 大模型课程
│   ├── lectures/           # 课程讲义与代码
│   ├── notes/              # 个人笔记（每人一个文件夹）
│   │   └── ljy/            # ljy 的笔记
│   ├── papers/             # 论文阅读与分享
│   │   └── 30-paper-zhCN/  # 论文中文解读参考（来自 Romanrose/30-paper-zhCN）
│   └── references/         # 参考资料
└── infra/                  # 基础设施（环境、脚本等）
```

## 📖 学习内容

### 1. CS336 — 大语言模型课程
- 跟随 Stanford CS336 课程体系学习 LLM 原理与实现
- 每节课后整理笔记到 `cs336/notes/<你的名字>/`
- 鼓励互相 review 笔记，共同进步

### 2. Agent — 智能体学习
- 使用 Datawhale《Hello Agents》教材入门 Agent
- 学习 Agent 框架、工具调用、多智能体协作等

### 3. Paper Reading — 论文分享
- 每周阅读并分享一篇大模型相关论文
- 论文解读放在 `cs336/papers/`，可参考 `30-paper-zhCN` 的中文解读
- 鼓励 PPT/文档 + 演示的形式分享

## 🚀 如何参与

1. **Fork 本仓库**
2. **在 `cs336/notes/` 下创建自己的笔记文件夹**（如 `cs336/notes/<你的名字>/`）
3. **每周提交笔记和论文分享**
4. **发起 Pull Request**

## ✅ 规范

- 笔记命名：`lecture<数字>.md`、`lecture<数字>.py`
- 论文命名：`YYYY-MM-DD-论文简称.md`
- 代码请附注释，方便他人理解
