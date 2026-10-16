# reading-19 · 小语言让代码变成可操作的数据

> 已获用户批准接入 · 来源范围见本文说明。

来源：[MIT 6.102 Spring 2026 · Reading 19: Little Languages](https://web.mit.edu/6.102/www/sp26/classes/19-little-languages/)。依据官方阅读正文整理，非课堂逐字稿；下方示例与练习为本地自写教学示例。


## 核心概念与推理

DSL 用一套领域结构表达一类问题，外部 DSL 有独立文本语法，内部 DSL 使用宿主语言 API。组合模式让单个元素和组合结构拥有同一接口；音乐可以由 Note、Rest 与 Concat 组成。解释器模式把每种变体的操作集中在类内，便于增加变体。Visitor 用双重分派把一个操作对所有变体的处理集中在访问者中，便于增加操作。选择取决于主要变化方向。

## 具体示例

```text
// Formula = Variable + Not + And + Or
// variables(Variable(x)) = {x}
// variables(Not(f)) = variables(f)
// variables(And(a,b)) = union(variables(a),variables(b))
```

同一 AST 可以被求值、收集变量或格式化，不必为每个任务重新解析字符串。Visitor 的 accept 先进入具体变体，再调用访问者对应方法，递归对子节点继续处理。

## 关键机制补充

Visitor 的双重分派先通过 AST 的动态类型选择具体变体，再由变体调用 visitor 对应操作；递归时重复这个过程。解释器按变体组织代码，Visitor 按操作组织代码，二者也可以并存。增加新变体通常需要更新全部 visitor；增加新操作通常只添加一个 visitor，选择时要依据预期变化。

## 常见误区

为了一个简单任务过度设计语言；混淆新增变体与新增操作的成本；手写 instanceof 分支漏掉新变体。

## 练习与检查点

给音乐 AST 添加总时长操作，再比较用解释器与 Visitor 的修改位置；说明新增 Repeat 变体的成本。

检查答案时必须写清前提、推导和一个反例；仅给出术语名称不足以说明理解。可回到官方文中的 reading exercises 检验，再记录与自己最初判断的差异。

## 原文阅读范围

Representing code as data, Building languages to solve problems, Music language, Functions on recursive types, Pattern matching, A function on a recursive type, Visitor pattern, Why visitor?, Summary。

## 资料与边界

完整官方阅读通过上方链接查看；作业、项目及考试见 [软件工程学习入口](/topics/software-engineering/)。官方 [录像说明](https://web.mit.edu/6.102/www/sp26/general/#are_lectures_recorded) 明确：本课不设概念讲授式 lectures，课堂用于主动练习且不录像。概念材料以交互阅读提供，因此本单元不适用课堂逐字稿，也没有生成时间轴。
