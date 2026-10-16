# reading-04 · 规格是模块之间的契约

来源：[MIT 6.102 Spring 2026 · Reading 4: Specifications](https://web.mit.edu/6.102/www/sp26/classes/04-specifications/)。依据官方阅读正文整理，非课堂逐字稿；下方示例与练习为本地自写教学示例。

> 待审核候选稿 · evidenceMode: reading-only · 尚未人工审核，未登记公开 outputs。

## 核心概念与推理

前置条件约束合法输入及调用前状态，后置条件规定返回值、异常和允许的状态变化。调用者保证前置条件，实现者在此前提下保证后置条件。规格应围绕参数和可观察行为，不能依赖局部变量或内部算法。未说明的输入修改不应自行引入。异常也属于契约的一部分，但 TypeScript 不会静态检查调用方处理了所有异常，因此结果类型与异常各有取舍。

## 具体示例

```ts
/** requires xs contains target
 * returns an index i such that xs[i] === target
 * does not modify xs */
function find(xs: ReadonlyArray<number>, target: number): number;
```

有多个匹配时，该规格允许任何一个匹配下标。没有匹配时前置条件不成立，调用方不能依赖返回 -1。若希望支持缺失情况，应把它明确加入契约。

## 关键机制补充

前置条件外的行为属于客户不能依赖的区域；这与规格明确承诺抛异常的错误输入不同。写测试时先判断调用是否合法，再判断期望值是否由后置条件推出。把一个未定义输入的偶然结果固定下来，会使测试拒绝本来合法的替代实现。

## 常见误区

把当前实现的行为写成必然承诺；只写参数类型而遗漏合法值；忘记说明副作用和异常。

## 练习与检查点

将 find 的契约改成允许不存在 target，并分别设计返回 undefined 与抛异常两种接口。

检查答案时必须写清前提、推导和一个反例；仅给出术语名称不足以说明理解。可回到官方文中的 reading exercises 检验，再记录与自己最初判断的差异。

## 原文阅读范围

Introduction, Behavioral equivalence, Why specifications?, Specification structure, Specifications in TypeScript, What a spec may talk about, Avoid null, Include emptiness, Testing and specifications, Specifications for mutating functions, Exceptions, Special results, Modules, Summary。

## 资料与边界

完整官方阅读通过上方链接查看；作业、项目及考试见 [软件工程学习入口](/topics/software-engineering/)。官方 [录像说明](https://web.mit.edu/6.102/www/sp26/general/#are_lectures_recorded) 明确：本课不设概念讲授式 lectures，课堂用于主动练习且不录像。概念材料以交互阅读提供，因此本单元不适用课堂逐字稿，也没有生成时间轴。
