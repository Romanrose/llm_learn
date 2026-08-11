---
title: llm_learn
description: 大模型、智能体与 AI Infra 的课程学习笔记
pageClass: course-map-home
outline: [2, 3]
---

# llm_learn

这里是大模型、智能体与 AI Infra 的课程学习站。课程官方链接、视频字幕、Slides 和扩展资料经过审核后，逐步沉淀为可搜索的逐字稿、Lecture Note、Blog 与排版 PDF。

<CourseMap />

## 推荐学习路线

<div class="learning-route-grid">
  <div class="learning-route">
    <strong>从零理解大模型</strong>
    <p>CS336 课程地图 → Tokenization 与架构 → GPU 与并行训练 → Scaling Laws → Evaluation</p>
  </div>
  <div class="learning-route">
    <strong>深入 Agent 系统</strong>
    <p>Hello Agents → ReAct 与工具使用 → Memory 与 Context Engineering → Agentic Evaluation</p>
  </div>
  <div class="learning-route">
    <strong>补齐 AI Infra</strong>
    <p>GPU 基础 → Attention 性能 → 分布式训练 → 网络与远程开发 → 可复现工程环境</p>
  </div>
  <div class="learning-route">
    <strong>论文到可运行实现</strong>
    <p>经典论文机制 → Notebook 复现 → 课程中的对应章节 → 工程化扩展</p>
  </div>
</div>

## 内容如何生成

<PipelineFlow />

自动化负责发现与生成，人负责确认来源、术语、公式和发布质量。完整状态依次为：

`discovered → resources-approved → ingested → transcribed → drafted → reviewed → published`

## 维护原则

- 原始内容仍保留在 `llm/`、`agent/`、`infra/` 和 `papers/`，网站不改变物理目录。
- `website/course.yaml` 定义全站结构，`website/catalog-data/` 描述课程、Lecture 和产物之间的关系。
- 逐字稿默认不进入全文搜索，Lecture Note 和 Blog 作为主要阅读入口。
- 官方 Slides 可以归档；能够从 LaTeX 重建的 PDF 不重复提交生成物。
