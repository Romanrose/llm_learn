# reading-10 · 函数作为数据与序列变换

来源：[MIT 6.102 Spring 2026 · Reading 10: Functional Programming](https://web.mit.edu/6.102/www/sp26/classes/10-functional-programming/)。依据官方阅读正文整理，非课堂逐字稿；下方示例与练习为本地自写教学示例。

> 待审核候选稿 · evidenceMode: reading-only · 尚未人工审核，未登记公开 outputs。

## 核心概念与推理

函数是一等值，可以传入、返回或存储。高阶函数将重复的控制模式抽象为 map、filter 与 reduce；纯函数避免副作用并使输入输出关系更清楚。Iterable 表示可遍历序列，Iterator 则保存遍历进度，next 会修改迭代器状态，因此共享同一迭代器会互相干扰。函数式风格并不自动保证不可变，回调仍可能捕获并修改外部状态。

## 具体示例

```ts
const total = [1,2,3,4]
  .filter(x => x % 2 === 0)
  .map(x => x * x)
  .reduce((sum,x) => sum + x, 0); // 20
```

filter 保留偶数，map 把元素映射为平方，reduce 用 0 作为空序列结果与累加初值。每一步有独立语义，比一个同时过滤、变换、累加的循环更容易检查。

## 关键机制补充

Iterable 可以生成新的迭代器，Iterator 只代表当前遍历进度；让两个客户共享同一迭代器会使一个客户消费掉另一个想读取的元素。高阶函数闭包保存的是可访问的环境，捕获对象之后仍可观察未来修改，因此“传入函数”本身不等于纯函数。

## 常见误区

把 map 用来执行副作用；省略 reduce 初值而忽略空数组；认为 const 回调不能修改捕获对象。

## 练习与检查点

用 map/filter/reduce 统计文件列表中特定后缀的总长度，给空列表和全被过滤的情况设测试。

检查答案时必须写清前提、推导和一个反例；仅给出术语名称不足以说明理解。可回到官方文中的 reading exercises 检验，再记录与自己最初判断的差异。

## 原文阅读范围

First-class functions, Abstracting out control, Iterator, Map/filter/reduce abstraction, Back to the motivating example, Benefits of abstracting out control, Summary。

## 资料与边界

完整官方阅读通过上方链接查看；作业、项目及考试见 [软件工程学习入口](/topics/software-engineering/)。官方 [录像说明](https://web.mit.edu/6.102/www/sp26/general/#are_lectures_recorded) 明确：本课不设概念讲授式 lectures，课堂用于主动练习且不录像。概念材料以交互阅读提供，因此本单元不适用课堂逐字稿，也没有生成时间轴。
