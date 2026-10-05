# MIT 6.102 · Software Construction

以 TypeScript 学习规格、测试、抽象、代码审查与并发。接入 Spring 2026 官方十九篇核心阅读与作业入口；官方明确课堂不录像。

- 稳定课程 ID：`mit-6102-sp26`
- 版本：MIT · Software Construction · Spring 2026
- 来源核对日期：2026-10-03
- [课程官网](https://web.mit.edu/6.102/www/sp26/)
- [本地网站课程入口](../../../website/generated/courses/mit-6102-sp26/index.md)

## 学习目录

按官方十九篇阅读建立单元，不将阅读数当作课堂讲座数；作业、项目均使用公开外链。

1. [Static Checking](https://web.mit.edu/6.102/www/sp26/classes/01-static-checking/)
2. [Testing](https://web.mit.edu/6.102/www/sp26/classes/02-testing/)
3. [Code Review](https://web.mit.edu/6.102/www/sp26/classes/03-code-review/)
4. [Specifications](https://web.mit.edu/6.102/www/sp26/classes/04-specifications/)
5. [Designing Specifications](https://web.mit.edu/6.102/www/sp26/classes/05-designing-specs/)
6. [Abstract Data Types](https://web.mit.edu/6.102/www/sp26/classes/06-abstract-data-types/)
7. [Abstraction Functions & Rep Invariants](https://web.mit.edu/6.102/www/sp26/classes/07-abstraction-functions-rep-invariants/)
8. [Interfaces & Subtyping](https://web.mit.edu/6.102/www/sp26/classes/08-interfaces-subtyping/)
9. [Equality](https://web.mit.edu/6.102/www/sp26/classes/09-equality/)
10. [Functional Programming](https://web.mit.edu/6.102/www/sp26/classes/10-functional-programming/)
11. [Recursive Data Types](https://web.mit.edu/6.102/www/sp26/classes/11-recursive-data-types/)
12. [Grammars & Parsing](https://web.mit.edu/6.102/www/sp26/classes/12-grammars-parsing/)
13. [Debugging](https://web.mit.edu/6.102/www/sp26/classes/13-debugging/)
14. [Concurrency](https://web.mit.edu/6.102/www/sp26/classes/14-concurrency/)
15. [Promises](https://web.mit.edu/6.102/www/sp26/classes/15-promises/)
16. [Mutual Exclusion](https://web.mit.edu/6.102/www/sp26/classes/16-mutual-exclusion/)
17. [Callbacks & Graphical User Interfaces](https://web.mit.edu/6.102/www/sp26/classes/17-callbacks-guis/)
18. [Message-Passing & Networking](https://web.mit.edu/6.102/www/sp26/classes/18-message-passing-networking/)
19. [Little Languages](https://web.mit.edu/6.102/www/sp26/classes/19-little-languages/)

## 延伸阅读

- [Software Engineering at Google](https://abseil.io/resources/swe-book)：官方免费在线阅读；经典工程实践。

## 整理边界

已补齐十九组阅读型中文 Note/Blog 候选稿，位于 `notes/reading-01..19/references/codex/`；每单元的 `sources.yaml` 和 `run.yaml` 标记 `reading-only` 与 `pending`。官方 FAQ 明确：课程概念来自交互阅读，课堂用于主动练习且不录像；因此没有课堂逐字稿。详见 [官方录像说明](https://web.mit.edu/6.102/www/sp26/general/#are_lectures_recorded)。完整入口见 [资源覆盖与审核索引](resources/coverage.md)，作业、考试和工具仍以官方外链保存。候选稿通过人工内容审核后才能登记 outputs；当前未公开发布。来源和访问边界见 [UPSTREAM.md](UPSTREAM.md)。

## 建议的自学闭环

先完成官方 Basic TypeScript 与 Git 1，再按单元顺序阅读原文；候选 Note 用于整理契约、推理与误区，Blog 用于把概念放回工程场景。PS0 练语言与绘图，PS1 练规格和测试，PS2 练 ADT 与表示不变量，PS3 练递归类型及解析，PS4 练异步状态和并发；Star Battle 综合客户端、服务端、协议、解析与团队协作。练习独立完成，课程原答案与学生代码不在本仓库公开。考试用于检查理解，先限时作答再自行对照官方解答。

## 本次用户批准

2026-10-03 用户明确批准本批现有 Note / Blog。正式文件位于 notes/<unit-id>/note.md 与 blog.md，并登记到课程 outputs；references/codex 保留来源稿及审批记录。新生成的 ASR 逐字稿另行保持待校对，不继承旧正文审批。未执行 Git 提交、推送或部署。
