# reading-07 · 抽象函数与表示不变量

来源：[MIT 6.102 Spring 2026 · Reading 7: Abstraction Functions & Rep Invariants](https://web.mit.edu/6.102/www/sp26/classes/07-abstraction-functions-rep-invariants/)。依据官方阅读正文整理，非课堂逐字稿；下方示例与练习为本地自写教学示例。

> 待审核候选稿 · evidenceMode: reading-only · 尚未人工审核，未登记公开 outputs。

## 核心概念与推理

表示不变量 RI 规定哪些具体状态合法，抽象函数 AF 将合法表示映射为抽象值。creator 与 producer 必须建立不变量，observer 与 mutator 必须保持它。checkRep 把可执行部分变成运行时断言，不能代替对全部操作的证明。表示泄露常来自保存外部可变对象或返回内部可变引用，需要防御性复制。不可变 ADT 可以更新缓存，只要其抽象值和客户可观察行为不变。

## 具体示例

```ts
// 表示：private chars: string
// RI: chars 中没有重复字符
// AF(chars): chars 包含的字符集合
// checkRep: new Set(chars).size === chars.length
```

表示 "ab" 和 "ba" 映射到同一抽象集合，而 "abb" 被此 RI 排除。也可以选允许重复的 RI，但相关操作必须按对应 AF 实现；两套设计不能混用。

## 关键机制补充

checkRep 的断言应只表达 RI，不能把特定测试输入的偶然性质写进去。防御性复制必须看对象图深度：复制数组只隔离数组结构，里面的可变对象仍共享。若元素本身不可变则可以安全共享；若元素可变，就需要复制或在操作规格中明确共享语义。

## 常见误区

把 RI 当成每个客户承担的前置条件；只复制外层数组却保留可变元素别名；把 AF 写成含糊的“表示集合”。

## 练习与检查点

为区间集合写 AF 和 RI，明确重叠区间是否允许，再分析返回内部数组会怎样破坏 RI。

检查答案时必须写清前提、推导和一个反例；仅给出术语名称不足以说明理解。可回到官方文中的 reading exercises 检验，再记录与自己最初判断的差异。

## 原文阅读范围

Invariants, Rep invariant and abstraction function, Benevolent side-effects, Documenting the AF, RI, and safety from rep exposure, ADT invariants replace preconditions, Recipes for programming, Summary。

## 资料与边界

完整官方阅读通过上方链接查看；作业、项目及考试见 [软件工程学习入口](/topics/software-engineering/)。官方 [录像说明](https://web.mit.edu/6.102/www/sp26/general/#are_lectures_recorded) 明确：本课不设概念讲授式 lectures，课堂用于主动练习且不录像。概念材料以交互阅读提供，因此本单元不适用课堂逐字稿，也没有生成时间轴。
