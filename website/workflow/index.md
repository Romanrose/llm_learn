---
title: Course 工作流
description: 从官方课程资源到网站内容与 PDF
---

# Course 工作流

每项内容都从可追溯的官方来源开始，而不是直接让模型生成文章。

<PipelineFlow />

## 1. Sync

从课程官方主页解析课程表，更新 Lecture、日期、讲师、课程讲义与作业节点；本地已有的逐字稿、Blog 和人工补充信息不会被覆盖。

```bash
npm run course -- sync cs336-2026
```

## 2. Discover

读取课程主页，发现视频、Slides、作业、代码仓库和扩展资料，生成待审核清单。

在进入内容生成前，可以先为单讲匹配视频并提取已有字幕：

```bash
npm run course -- prepare cs336-2026 lecture-01
```

## 3. Approve

人工确认资源归属、有效性和是否需要进入知识库。未批准资源不会下载或参与内容生成。

## 4. Ingest

保存资源清单，按需归档官方 Slides；视频优先提取官方字幕，没有字幕时才进入本地 ASR。

## 5. Generate

从证据材料生成逐字稿、Lecture Note 和 Blog 草稿，并保留源文件之间的关联。

## 6. Review & Publish

核对术语、公式、引用和内容边界，通过后生成 VitePress 页面与 LaTeX PDF。

## 渐进式接入

不需要一次性建立完整课程。新增课程或项目时，先登记稳定 ID，再只创建当前正在学习的 Lecture 或项目文档；有正式产物后才登记到 `website/catalog-data/` 的 `outputs`。候选稿保存在每讲的 `references/<provider>/`，正式稿才进入网站。

正式稿复查：

```bash
npm run course -- validate <course-id> <lecture-id> --published
npm run build
```
