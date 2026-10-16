# reading-09 · 相等必须尊重抽象值

> 已获用户批准接入 · 来源范围见本文说明。

来源：[MIT 6.102 Spring 2026 · Reading 9: Equality](https://web.mit.edu/6.102/www/sp26/classes/09-equality/)。依据官方阅读正文整理，非课堂逐字稿；下方示例与练习为本地自写教学示例。


## 核心概念与推理

相等应满足自反、对称和传递。不可变 ADT 的值相等由 AF 决定，而对象引用相等不能直接替代它。可变对象需要区分当前观察相等和未来行为相等：两个独立数组现在内容相同，修改一个后就能区分它们。TypeScript 的对象 === 按身份比较，Set 与 Map 的对象键也依赖身份；自定义 equalValue 不会改变其查找规则。深比较表示字段未必等于比较抽象值。

## 具体示例

```ts
const a = new Set([1,2]);
const b = new Set([2,1]);
console.log(a === b); // false
console.log(a.size === b.size); // true，但不足以证明值相等
```

同大小集合也可能有不同元素。集合值相等需要大小相同且每个元素都相互属于对方；对于对象元素，还必须先选定身份或值的元素相等语义。

## 关键机制补充

观察相等比较当前所有观察结果；行为相等还考虑之后允许的操作。不可变对象二者一致，而独立可变对象即使内容一致，也可能被一次修改区分。Set 和 Map 对对象使用身份比较；要按业务值去重，可以选择稳定基本类型键或显式索引，不能期望它们自动使用自定义 equalValue。

## 常见误区

用 JSON.stringify 定义所有值相等；以为 equalValue 能改变内置 Map；给可变状态定义不稳定的哈希键。

## 练习与检查点

为一个以秒或毫秒表示的不可变 Duration 定义 equalValue，验证 1 秒与 1000 毫秒相等。

检查答案时必须写清前提、推导和一个反例；仅给出术语名称不足以说明理解。可回到官方文中的 reading exercises 检验，再记录与自己最初判断的差异。

## 原文阅读范围

Introduction, Equivalence relation, Equality of immutable types, Reference equality vs. value equality, Equality of mutable types, “Deep equality” on collections, Hash functions, Equality in Python and TypeScript/JavaScript, Summary。

## 资料与边界

完整官方阅读通过上方链接查看；作业、项目及考试见 [软件工程学习入口](/topics/software-engineering/)。官方 [录像说明](https://web.mit.edu/6.102/www/sp26/general/#are_lectures_recorded) 明确：本课不设概念讲授式 lectures，课堂用于主动练习且不录像。概念材料以交互阅读提供，因此本单元不适用课堂逐字稿，也没有生成时间轴。
