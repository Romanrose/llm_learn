# reading-11 · 递归结构需要逐变体定义

> 已获用户批准接入 · 来源范围见本文说明。

来源：[MIT 6.102 Spring 2026 · Reading 11: Recursive Data Types](https://web.mit.edu/6.102/www/sp26/classes/11-recursive-data-types/)。依据官方阅读正文整理，非课堂逐字稿；下方示例与练习为本地自写教学示例。


## 核心概念与推理

递归数据类型由有限个变体组成，其中某些变体包含同类值。不可变列表可定义为 Empty 或 Cons(first,rest)，递归函数对每个变体各有一条规则。基本情况负责终止，递归步骤缩小结构。不可变尾部允许多个列表共享，而不造成可变别名风险。缓存长度等实现细节仍需要 RI 保证；递归结构也要考虑循环与深度，不能把任意对象图当作树。

## 具体示例

```text
// ImList<T> = Empty + Cons(first:T, rest:ImList<T>)
// size(Empty) = 0
// size(Cons(x,xs)) = 1 + size(xs)
```

把两条规则转成实现后，正确性沿结构展开。Cons(1,Cons(2,Empty)) 的大小为 2；给旧列表添加头节点可以共享整个旧列表，不必复制尾部。

## 关键机制补充

结构递归的终止依赖子结构更小和存在基本变体。对于 ImList 的共享尾部，返回 rest 安全是因为尾部不可变，而不是因为方法叫 observer。若把 Cons 的 first 设为可变对象，只读列表并不能阻止客户修改元素，需要在类型及规格层另外处理。

## 常见误区

遗漏一个变体；没有减小问题规模；认为只读容器自动使可变元素不可变。

## 练习与检查点

为布尔公式 Variable、Not、And、Or 定义变量集合操作，每个变体写一条递归规则。

检查答案时必须写清前提、推导和一个反例；仅给出术语名称不足以说明理解。可回到官方文中的 reading exercises 检验，再记录与自己最初判断的差异。

## 原文阅读范围

Introduction, Recursion, Example: Immutable lists, Recursive data type definitions, Functions over recursive data types, Rep independence and rep exposure revisited, Null vs. empty, Static type vs. dynamic type, Dynamic type inspection, Equality, Another example: Boolean formulas, Backtracking search with immutability, Immutability and performance, Summary。

## 资料与边界

完整官方阅读通过上方链接查看；作业、项目及考试见 [软件工程学习入口](/topics/software-engineering/)。官方 [录像说明](https://web.mit.edu/6.102/www/sp26/general/#are_lectures_recorded) 明确：本课不设概念讲授式 lectures，课堂用于主动练习且不录像。概念材料以交互阅读提供，因此本单元不适用课堂逐字稿，也没有生成时间轴。
