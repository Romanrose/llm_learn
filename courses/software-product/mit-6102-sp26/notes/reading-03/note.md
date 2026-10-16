# reading-03 · 代码审查检验人的理解

> 已获用户批准接入 · 来源范围见本文说明。

来源：[MIT 6.102 Spring 2026 · Reading 3: Code Review](https://web.mit.edu/6.102/www/sp26/classes/03-code-review/)。依据官方阅读正文整理，非课堂逐字稿；下方示例与练习为本地自写教学示例。


## 核心概念与推理

代码审查通过他人的阅读发现缺陷、歧义与未来修改风险。DRY 的关键不是把所有相似文本合并，而是减少同一知识的重复表示。注释应记录规格和非显然假设，变量应只有一个用途，常量应表达设计决定。尽早失败可以缩短错误传播距离；避免全局可变状态可缩小推理范围。返回值比打印结果更便于复用，重构则在不改变外部行为的前提下改善内部结构。

## 具体示例

```ts
function countLong(words: ReadonlyArray<string>): number {
  return words.filter(w => w.length > 8).length;
}
console.log(countLong(["construction"]));
```

统计函数与控制台展示分离。调用方可把结果用于界面、日志或进一步计算，而不必修改统计逻辑。阈值是否应命名或参数化取决于它代表的领域规则。

## 关键机制补充

审查应区分可行为保持的重构与改变契约的修改。提取函数前先确认参数、副作用与返回值，重命名后核查全部调用点，消除重复时保留每条领域规则的意义。全局常量与全局可变变量风险不同：问题主要来自分散写入使读者无法限定状态来源。

## 常见误区

只检查格式而忽略规格；注释机械复述语句；为去掉几行重复制造难懂的万能抽象。

## 练习与检查点

审查一个日期计算函数：指出魔法数字、重复规则和输入假设，给出保持行为的重构步骤。

检查答案时必须写清前提、推导和一个反例；仅给出术语名称不足以说明理解。可回到官方文中的 reading exercises 检验，再记录与自己最初判断的差异。

## 原文阅读范围

Code review, Smelly example #1, Don’t repeat yourself (DRY), Comment where needed, Fail fast, Avoid magic numbers, One purpose for each variable, Smelly example #2, Use good names, Use whitespace and punctuation to help the reader, Smelly example #3, Don’t use global variables, Functions should return results, not print them, Avoid special-case code, Code at the right length, Refactoring, Summary。

## 资料与边界

完整官方阅读通过上方链接查看；作业、项目及考试见 [软件工程学习入口](/topics/software-engineering/)。官方 [录像说明](https://web.mit.edu/6.102/www/sp26/general/#are_lectures_recorded) 明确：本课不设概念讲授式 lectures，课堂用于主动练习且不录像。概念材料以交互阅读提供，因此本单元不适用课堂逐字稿，也没有生成时间轴。
