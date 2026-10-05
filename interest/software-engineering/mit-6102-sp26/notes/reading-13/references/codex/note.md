# reading-13 · 调试是一系列可反驳的实验

来源：[MIT 6.102 Spring 2026 · Reading 13: (Avoiding) Debugging](https://web.mit.edu/6.102/www/sp26/classes/13-debugging/)。依据官方阅读正文整理，非课堂逐字稿；下方示例与练习为本地自写教学示例。

> 待审核候选稿 · evidenceMode: reading-only · 尚未人工审核，未登记公开 outputs。

## 核心概念与推理

先把失败变成稳定可复现的测试，再提出原因假设、预测与实验。二分定位缩小可疑区域，delta debugging 删减输入或变更以找到最小失败。探针应尽量少改变运行行为，日志、断言和调试器各有用途。修复前要解释因果链，修复后重跑复现测试及相关回归。静态检查、封装、短作用域和尽早失败能降低未来搜索成本。

## 具体示例

```ts
// 假设：转换阶段丢失最后一个元素
assert.strictEqual(parsed.length, raw.length);
assert.strictEqual(converted.length, parsed.length);
```

两个断言将问题区分为解析前后或转换前后，而不是立即修改循环。若第二个断言失败，再检查转换循环边界；若都通过，就必须放弃或细化当前假设。

## 关键机制补充

二分搜索可以定位长流水线首次破坏不变量的位置，delta debugging 则通过删减输入找出保留失败的最小片段。最小失败更容易暴露必要条件，但仍需解释真实因果。错误修复后不要只删除症状；要确认谁违反契约，修正该模块并保存用例。

## 常见误区

连续修改多处导致无法判断原因；修到测试通过却不理解缺陷；日志改变竞态时序。

## 练习与检查点

记录一次调试的假设、预测、观察和结论，用输入删减找到最小复现，再加入回归测试。

检查答案时必须写清前提、推导和一个反例；仅给出术语名称不足以说明理解。可回到官方文中的 reading exercises 检验，再记录与自己最初判断的差异。

## 原文阅读范围

A rogue’s gallery of bugs, First defense: make bugs impossible, Second defense: make bugs easy to find, Reproduce the bug, Find the bug using the scientific method, Fix the bug。

## 资料与边界

完整官方阅读通过上方链接查看；作业、项目及考试见 [软件工程学习入口](/topics/software-engineering/)。官方 [录像说明](https://web.mit.edu/6.102/www/sp26/general/#are_lectures_recorded) 明确：本课不设概念讲授式 lectures，课堂用于主动练习且不录像。概念材料以交互阅读提供，因此本单元不适用课堂逐字稿，也没有生成时间轴。
