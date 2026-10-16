# reading-06 · 抽象数据类型由操作定义

来源：[MIT 6.102 Spring 2026 · Reading 6: Abstract Data Types](https://web.mit.edu/6.102/www/sp26/classes/06-abstract-data-types/)。依据官方阅读正文整理，非课堂逐字稿；下方示例与练习为本地自写教学示例。

> 待审核候选稿 · evidenceMode: reading-only · 尚未人工审核，未登记公开 outputs。

## 核心概念与推理

ADT 的身份由操作与操作的规格确定，不由数组、链表等具体表示确定。creator 创造对象，producer 从旧对象产生新对象，observer 观察值，mutator 改变抽象状态。一个好的 ADT 应简单、连贯、足够且表示独立。测试需要组合这些操作建立并检查状态，但不能绕过公共接口读内部字段。可变与不可变是在抽象层观察到的性质，不是某个字段声明的外观。

## 具体示例

```ts
interface IntSet {
  has(x: number): boolean;
  size(): number;
  add(x: number): void;
}
```

客户只依赖集合操作，内部可由数组改为哈希表。add 是 mutator；has 与 size 是 observer。若公开底层数组，客户可能依赖顺序并插入重复值，集合抽象随即失守。

## 关键机制补充

不可变集合的 add 应返回一个新抽象值，旧集合仍可观察为原内容；测试应同时检查新旧对象。creator 不一定是构造函数，工厂也可创造值。producer 与 mutator 的区别应按抽象结果判断，内部缓存更新若不改变抽象值，并不自动构成抽象修改。

## 常见误区

把类等同于 ADT；暴露所有实现方法；在通用集合接口中混入业务特定操作。

## 练习与检查点

设计不可变集合接口：将 add 改成 producer，并说明如何只用公共操作测试它。

检查答案时必须写清前提、推导和一个反例；仅给出术语名称不足以说明理解。可回到官方文中的 reading exercises 检验，再记录与自己最初判断的差异。

## 原文阅读范围

Introduction, What abstraction means, Classifying types and operations, An abstract type is defined by its operations, Designing an abstract type, Representation independence, Realizing ADT concepts in TypeScript, Testing an abstract data type, Summary。

## 资料与边界

完整官方阅读通过上方链接查看；作业、项目及考试见 [软件工程学习入口](/topics/software-engineering/)。官方 [录像说明](https://web.mit.edu/6.102/www/sp26/general/#are_lectures_recorded) 明确：本课不设概念讲授式 lectures，课堂用于主动练习且不录像。概念材料以交互阅读提供，因此本单元不适用课堂逐字稿，也没有生成时间轴。
