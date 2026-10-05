# reading-01 · 静态检查能承诺什么

来源：[MIT 6.102 Spring 2026 · Reading 1: Static Checking](https://web.mit.edu/6.102/www/sp26/classes/01-static-checking/)。依据官方阅读正文整理，非课堂逐字稿；下方示例与练习为本地自写教学示例。

> 待审核候选稿 · evidenceMode: reading-only · 尚未人工审核，未登记公开 outputs。

## 核心概念与推理

类型描述一组值以及这些值允许的操作。静态检查在运行之前发现错误，动态检查在执行时发现非法状态，而有些语言行为根本不会报错。TypeScript 的 number 同时包含整数、浮点数、NaN 和 Infinity；类型正确不意味着数学值正确。const 固定的是变量绑定，不会冻结它指向的数组。课程把质量拆为免于缺陷、易于理解、便于修改，类型只是三者共同的一个起点。

## 具体示例

```ts
const xs: number[] = [1];
xs.push(2); // 合法：数组仍可变
const ratio: number = 1 / 0; // Infinity，类型检查通过
```

数组追加并没有重新赋值 xs。除零结果仍属于 number，因此不能期待编译器拒绝。若业务要求有限数，必须另外检查 Number.isFinite。

## 关键机制补充

静态类型在编译后被擦除，运行时实际执行的是 JavaScript；来自文件、网络或用户输入的值不会因为写了类型断言就变成可信数据。number 的安全整数范围与最大有限浮点数不是同一概念。数组越界可能得到 undefined，除零可能得到 Infinity，这些未必触发异常；检查策略需要依据语言运行时而非数学直觉。

## 常见误区

把 const 当作深度不可变；把通过 tsc 当作证明正确；忽略安全整数范围。

## 练习与检查点

给 hailstone 函数写输入约束，并说明 n=0、非整数和大整数各自的问题。

检查答案时必须写清前提、推导和一个反例；仅给出术语名称不足以说明理解。可回到官方文中的 reading exercises 检验，再记录与自己最初判断的差异。

## 原文阅读范围

Hailstone sequence, Types, Static typing, Static checking, dynamic checking, no checking, Arrays, Functions, Mutating values vs. reassigning variables, Documenting assumptions, Hacking vs. engineering, The goals of 6.102, Summary。

## 资料与边界

完整官方阅读通过上方链接查看；作业、项目及考试见 [软件工程学习入口](/topics/software-engineering/)。官方 [录像说明](https://web.mit.edu/6.102/www/sp26/general/#are_lectures_recorded) 明确：本课不设概念讲授式 lectures，课堂用于主动练习且不录像。概念材料以交互阅读提供，因此本单元不适用课堂逐字稿，也没有生成时间轴。
