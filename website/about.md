---
title: 关于 llm_learn
---

# 关于 llm_learn

这是一个围绕大模型、智能体和 AI Infra 的个人课程学习系统。

它的核心不是“自动写文章”，而是建立一条可追溯的知识生产链：官方资源提供事实边界，字幕和讲义提供原始证据，AI 辅助生成结构化草稿，最终由人完成核对与发布。

项目采用“统一模板、渐进接入”：当前以 `llm/cs336-2026/` 为完整课程样例，其他课程、Agent 教程和论文项目只在真正学习或实践时加入，不预先堆叠空目录。目录规则见[统一项目结构](/about#项目结构)。

## 内容层次

| 产物 | 主要用途 | 推荐格式 |
| --- | --- | --- |
| Transcript | 搜索原话、核对上下文 | Markdown |
| Lecture Note | 系统学习、公式推导 | LaTeX |
| Blog | 快速理解、主题传播 | Markdown |
| PDF | 阅读、打印和归档 | XeLaTeX / PDF |

## 发布状态

内容依次经过 `discovered → resources-approved → ingested → transcribed → drafted → reviewed → published`。只有经过审核的内容才进入正式课程导航。

## 项目结构

课程正文位于 `llm/<course-id>/`，独立 Agent 项目位于 `agent/<project-id>/`，论文复现位于 `papers/<paper-id>/`。课程的 `website/catalog-data/` 只保存元数据，网站页面由 `workflow/scripts/` 中的构建脚本生成，详细约定见仓库的[统一项目结构](https://github.com/Romanrose/llm_learn/blob/master/workflow/standards/project-structure.md)。
