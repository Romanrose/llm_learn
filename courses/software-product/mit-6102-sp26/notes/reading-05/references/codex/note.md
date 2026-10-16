# reading-05 · 规格强弱与替换关系

来源：[MIT 6.102 Spring 2026 · Reading 5: Designing Specifications](https://web.mit.edu/6.102/www/sp26/classes/05-designing-specs/)。依据官方阅读正文整理，非课堂逐字稿；下方示例与练习为本地自写教学示例。

> 待审核候选稿 · evidenceMode: reading-only · 尚未人工审核，未登记公开 outputs。

## 核心概念与推理

规格的强弱取决于允许输入和允许输出。更弱的前置条件允许更多客户调用，更强的后置条件给客户更多保证；两者使规格整体更强。不是任意两份规格都可比较。确定性要求同一输入对应一个结果，欠确定规格则允许多个合法结果，它不意味着实现必须随机。声明式规格描述应该成立的关系，操作式规格描述具体步骤；前者通常给实现保留更多空间。

## 具体示例

```ts
// S1: requires target exists; returns any matching index
// S2: accepts all arrays; returns first matching index or undefined
```

S2 接受更多输入，也在重复匹配时给出更精确结果，因此相对 S1 更强。若新规格只接受排序数组，即使结果更精确，也不一定整体更强。

## 关键机制补充

欠确定规格通常比过度指定更利于换实现，但也可能弱到无法支撑客户。异常发生前的修改尤其要明确：如果追加操作在途中失败，规格应说明原对象保持不变、部分改变还是允许某种限定状态，不能只列出异常名称。不可变数据可以直接排除一类共享修改造成的客户误解。

## 常见误区

把更严格前置条件称为更强契约；把欠确定误解为随机；在异常规格里遗漏失败前已经发生的修改。

## 练习与检查点

比较“接受任意数组返回任意匹配”与“接受排序数组返回首个匹配”，找出无法直接替换的客户。

检查答案时必须写清前提、推导和一个反例；仅给出术语名称不足以说明理解。可回到官方文中的 reading exercises 检验，再记录与自己最初判断的差异。

## 原文阅读范围

Introduction, Deterministic vs. underdetermined specs, Declarative vs. operational specs, Stronger vs. weaker specs, Diagramming specifications, Mutability, Designing good specifications, Precondition or postcondition?, Where we use specs, Summary。

## 资料与边界

完整官方阅读通过上方链接查看；作业、项目及考试见 [软件工程学习入口](/topics/software-engineering/)。官方 [录像说明](https://web.mit.edu/6.102/www/sp26/general/#are_lectures_recorded) 明确：本课不设概念讲授式 lectures，课堂用于主动练习且不录像。概念材料以交互阅读提供，因此本单元不适用课堂逐字稿，也没有生成时间轴。
