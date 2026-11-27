---
title: 自进化与自我改进
description: 自进化 / 自我改进 LLM 智能体课程，以及安全课中的经典递归自我改进（RSI）讲次
---

# 自进化与自我改进

近几年课堂上所说的自进化（self-evolving）或自我改进（self-improving），多半是指语言模型与 Agent 在交互中改进自己的上下文、工具与 harness、模型参数，或所用的任务与环境。它和经典文献里的递归自我改进（RSI）——系统用更强的能力设计出更强的后继系统，并可能形成智能爆炸——并不等同。后者目前几乎没有整门大学课，主要出现在 AI Safety 课的单讲中。

本专题把相关课程与讲次串在一起，课程页提供自行整理的学习内容，延伸资料保留官方外链，不复制第三方全文。下列链接均已在 2026-11-27 访问核对。

## 1. 本站收录的自进化课程

以下课程/论文研讨课挂在[大模型与智能体](/#llm-courses)下，提供学习内容与官方资源导航。

| 课程 | 内容 | 资料 |
| --- | --- | --- |
| [MIT MAS.S62 · Fall 2026](/generated/courses/mit-mas-s62-fall26/) | Self-Evolving AI（亦称 AI4AI）：按 context / harness / model / environment 四条主线组织 | 课程页、Syllabus、第 1–3、5–7、9 周讲义笔记与 Blog；无公开视频，不提供课堂逐字稿 |
| [Stanford CS329A · Autumn 2025](/generated/courses/cs329a-autumn25/) | Self-Improving AI Agents：测试时计算、验证器、工具反馈、强化学习与开放式演化 | 课程页、[9 讲核心录像](https://www.youtube.com/playlist?list=PLangBM27OtEA)、对应第 1–6、8、17、20 讲的笔记、Blog 与中英字幕稿、作业仓库；公开主页无官方幻灯片 |

| [Saarland / UdS · Winter 26/27](/generated/courses/uds-sia-winter2627/) | Towards Self-Improving Agents；Yupei Du 的论文讨论 Seminar，非录像讲座课 | 12 次讨论：官方导论幻灯片、11 次学生主论文及延伸阅读；[导论笔记](/generated/courses/uds-sia-winter2627/session-01/lecture-note.html) · [Blog](/generated/courses/uds-sia-winter2627/session-01/blog.html) |

MIT 这门是目前能找到的最新开设，2026 秋仍在上课。斯坦福目前可公开使用的最新校园课材料仍是 2025 秋；课程目录已排 2027 春，但还没有新的公开大纲或录像。付费的 Stanford Online Agentic AI 项目不在本站课程目录中。

## 2. 本站已有课程中的相关讲次

- Harvard CS2680 Fall 2026 第 10 讲「Advanced agent design II: agent safety, self-evolving harness」：[本站课程页](/generated/courses/harvard-cs2680-fall26/lecture-10/) · [官方阅读页](https://cs2680.com/readings/oct-14.html)。
- Stanford CS329Z Fall 2026 第 9 讲 Optimization（提示优化、Darwin Gödel Machine、GEPA 等）：[本站课程页](/generated/courses/cs329z-fall26/lecture-09/) · [官方 Slides](https://web.stanford.edu/class/cs329z/slides/lecture09.pdf) · [公开录像](https://youtu.be/e_m99aR7_3Q)。

## 3. 延伸阅读：安全课中的经典 RSI

这两讲以相关单讲托管，不将整个 ML theory / AI Safety seminar 冒充整门自进化课程，也不加入首页整课卡片。

- Harvard CS2881R · 2025 年 10 月 9 日 Recursive Self-Improvement：[官方录像](https://youtu.be/wzep3Rnv6iw) · [课程页](https://boazbk.github.io/mltheoryseminar/fall2025/) · [本站相关单讲](/generated/courses/harvard-cs2881r-rsi-fall25/lecture-06/)。[笔记](/generated/courses/harvard-cs2881r-rsi-fall25/lecture-06/lecture-note.html) · [Blog](/generated/courses/harvard-cs2881r-rsi-fall25/lecture-06/blog.html) · [中文逐字稿](/generated/courses/harvard-cs2881r-rsi-fall25/lecture-06/transcript-zh.html) · [英文字幕稿](/generated/courses/harvard-cs2881r-rsi-fall25/lecture-06/transcript-en.html)。官方归档页当前标题为 CS2881 AI Safety（ML theory seminar 网站）；仅收录 2025-10-09 这讲，英文来源为平台自动字幕。
- 图宾根 AI Safety Summer 2026 第 12 讲 Automating AI R&D（递归自我改进、自动化研发基准与 AI control）：[课程仓库](https://github.com/aisa-group/tue-ai-safety-course) · [第 12 讲幻灯片](https://github.com/aisa-group/tue-ai-safety-course/blob/main/lecture-slides/lecture-12-ai-rnd-automation.html) · [本站幻灯片笔记](/generated/courses/tuebingen-ai-safety-sp26-rnd/lecture-12/lecture-note.html) · [Blog](/generated/courses/tuebingen-ai-safety-sp26-rnd/lecture-12/blog.html)。基于官方 HTML 幻灯片，无课堂逐字稿。

## 4. 其他课程中的相关周次（仅外链）

- UMD CMSC 848N · Generative AI Agents · Fall 2026，[官方课程页](https://furong-huang.com/cmsc848n-fall-2026/)的 Module / Week 12「Learning from experience and self-improvement」：11 月 17 日 Learning from Experience（[Slides](https://furong-huang.com/courses/cmsc848n/fall-2026/slides/W12-L1-2026-Learning-from-Experience.pdf)）、11 月 19 日 Self-Modifying and Evolutionary Agents（[Slides](https://furong-huang.com/courses/cmsc848n/fall-2026/slides/W12-L2-2026-Self-Modifying-and-Evolutionary-Agents.pdf)）。这里只链接相关周次，不接入整门课。
- Princeton COS 597C · AI Agents · Fall 2026，[官方日程](https://princeton-nlp.github.io/ai-agents/)的 W10（11 月 13 日）Self-improvement：Continual Harness、Harnessing Agent Skills、Decentralized Multi-Agent Systems with Shared Context、Voyager，补充 CoALA。这里只链接相关周次，不接入整门课。

## 说明

- 课程的讲义、教材与视频版权归原作者；本站仅保留官方链接与自行整理的学习内容。
- CS329A 基于平台自动字幕整理；MIT 仅基于幻灯片。生成内容已获用户授权发布，但不等于独立人工内容审阅，请对照官方来源核验术语与论证。

- UdS 第 2–12 次为学生论文报告，未发现公开学生幻灯片；不生成课堂笔记或逐字稿。其官网 YouTube 链接 [how to write an OK research paper](https://www.youtube.com/watch?v=qNlwVGxkG7Q) 是学期论文写作指南，不是本课讲座录像。11 月 3 日、12 月 22 日与 29 日为 No class，不计入 12 次讨论。
