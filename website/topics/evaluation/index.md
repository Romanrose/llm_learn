---
title: 评测与基准
description: 语言模型与 Agent 评测：历史脉络、评测的作用、课程、核心论文与工具
---

# 评测与基准

评测首先不是排行榜上的一个数字，而是一次推理：从准确率、胜率、通过率或人工投票这类观测出发，推断模型的能力、比较结果或是否可以部署。本专题把课程、论文与工具串成一条线，所有条目只做外链，不复制全文。

综合整理参考了本项目评测知识库对课程、论文与工具的核对记录；下列链接均已在 2026-11-23 访问核对。

## 1. 历史脉络

1. 共享测试集与自动指标：信息检索的 Cranfield / TREC 传统，机器翻译的 [BLEU（2002）](https://aclanthology.org/P02-1040/) 与 [Reiter 对 BLEU 效度的结构化回顾（2018）](https://aclanthology.org/J18-3002/)。
2. 多任务榜单时代：[GLUE](https://arxiv.org/abs/1804.07461)、[MMLU](https://arxiv.org/abs/2009.03300)。
3. 对基准文化的反思：[Bowman 与 Dahl：How to fix benchmarking in NLU](https://aclanthology.org/2021.naacl-main.385/)、[Raji 等：Everything in the Whole Wide World Benchmark](https://arxiv.org/abs/2111.15366)。
4. 整体评测与偏好评测：[HELM](https://arxiv.org/abs/2211.09110)、[LLM-as-a-Judge / MT-Bench / Chatbot Arena](https://arxiv.org/abs/2306.05685)、LMSYS [Arena 博客](https://www.lmsys.org/blog/2023-05-03-arena/)。
5. 污染、Agent 评测与榜单有效性：[Sainz 等：数据污染](https://aclanthology.org/2023.findings-emnlp.722/)、[LiveBench](https://arxiv.org/abs/2406.19314)、[SWE-bench](https://arxiv.org/abs/2310.06770)、[The Leaderboard Illusion](https://arxiv.org/abs/2504.20879)。

## 2. 评测在做什么

- **能力度量**：考试式与任务式基准（MMLU、HELM 场景、SWE-bench）。
- **偏好与质量**：人工投票、LLM-as-a-judge 对开放式生成打分。
- **训练与选择信号**：评分器和单元测试同时参与训练与选型，所以污染与古德哈特效应很重要。
- **部署门控**：评测作为发版与安全门槛。
- **Agent 的过程控制**：轨迹、离线与线上评测、结果检验。

## 3. 本站收录的评测课程

[评测与基准课程区](/#evaluation)：

| 课程 | 内容 | 视频 |
| --- | --- | --- |
| [Stanford CME 295 · Autumn 2026](/generated/courses/cme295-fall26/) | Transformers 与 LLM，第 7 讲专讲 LLM 评测（LLM-as-a-judge、偏差、Agent 评测、基准） | 官方 YouTube 播放列表 |
| [Stanford CS321M · Spring 2026](/generated/courses/cs321m-sp26/) | AI Measurement Science：预测建模、效度与信度、基准与治理 | 未发现公开录像 |
| [CMU 11-801 · Fall 2026](/generated/courses/cmu-11801-fall26/) | 语言技术的定量评测：离线与在线指标、实验设计、假设检验 | 未发现公开录像 |
| [JHU PH.140.850 · 2026](/generated/courses/jhu-ph140850-2026/) | Six Ideas in AI Evaluation：预测评估、基准、模型标注、分布偏移、研究设计 | 未发现公开录像 |

## 4. 其他课程中的评测讲次

- CS336 第 12 讲 Evaluation（Percy Liang）：[已发布的讲义笔记](/generated/courses/cs336-2026/lecture-12/) · [官方录像](https://www.youtube.com/watch?v=JpAxdTWQJxM)。
- CS224N Winter 2026 第 11 讲 Benchmarking and Evaluation（Yejin Choi）：[课程页](/generated/courses/cs224n-winter26/) · [官方 Slides](https://web.stanford.edu/class/cs224n/slides_w26/cs224n-2026-lecture11-evaluation.pdf)；录播需选课权限。
- CS329Z Fall 2026：第 10 讲 Terminal-Bench（[Slides](https://web.stanford.edu/class/cs329z/slides/lecture10.pdf)）、第 13 讲评测基础（[Slides](https://web.stanford.edu/class/cs329z/slides/lecture13.pdf)）、第 15 讲 LLM-as-a-judge（[Slides](https://web.stanford.edu/class/cs329z/slides/lecture15.pdf)）；[课程页](/generated/courses/cs329z-fall26/)。
- CMU 11-768 Assignment 2 · Evaluate an Agent：[课程页](/generated/courses/cmu-11768-fall26/) · [作业仓库](https://github.com/cmu-agents/assignment-2)。

## 5. 工具与实践指南

- [Stanford HELM](https://crfm.stanford.edu/helm/)：多场景、多指标的整体评测框架与排行榜。
- [lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness)：EleutherAI 的开源评测框架。
- [Inspect](https://inspect.aisi.org.uk/)：UK AISI 的评测框架。
- [Hugging Face Evaluation Guidebook](https://github.com/huggingface/evaluation-guidebook)：评测方法实践指南。
- [Anthropic：Demystifying evals for AI agents](https://www.anthropic.com/research/demystifying-evals-for-ai-agents)：Agent 评测实践。
- 教材：[AIMS · AI Measurement Science](https://aims.stanford.edu/textbook/)。

## 说明

- 课程的讲义、教材与视频版权归原作者；本站仅保留官方链接与自行整理的学习内容。
- 评测课程的候选笔记审核通过前不公开。
