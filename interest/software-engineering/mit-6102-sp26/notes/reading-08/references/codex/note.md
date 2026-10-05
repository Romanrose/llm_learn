# reading-08 · 接口、子类型和动态分派

来源：[MIT 6.102 Spring 2026 · Reading 8: Defining ADTs with Interfaces, Generics, Enums, and Functions](https://web.mit.edu/6.102/www/sp26/classes/08-interfaces-subtyping/)。依据官方阅读正文整理，非课堂逐字稿；下方示例与练习为本地自写教学示例。

> 待审核候选稿 · evidenceMode: reading-only · 尚未人工审核，未登记公开 outputs。

## 核心概念与推理

接口将 ADT 的操作签名与实现类分离。TypeScript 使用结构子类型：具有要求的成员即可兼容，不一定显式 implements。但编译器只检查可表达的类型条件，无法验证完整语义契约。子类型方法应满足至少同样强的规格。静态类型决定客户可见操作，动态类型决定实际调用哪个实现。工厂函数可以隐藏构造类，泛型减少重复，而枚举适合有限的具名状态。

## 具体示例

```ts
interface Text { length(): number; }
function describe(x: Text): string {
  return `length=${x.length()}`;
}
```

具有 length() 方法的不同类都能被 describe 接纳。若某实现对空文本抛异常而接口承诺总是返回长度，它仍可能通过类型检查，却违反行为子类型约定。

## 关键机制补充

泛型把类型参数传入集合接口，让同一套操作适用于不同元素；它提供元素类型检查，仍无法决定元素的业务相等关系。工厂返回接口而不是实现类，可以把 Array 实现换成 Map 实现。公开 getter 也可暴露观察值而非字段位置，所以接口中的属性不一定要求特定 rep。

## 常见误区

把结构兼容当成语义兼容；用继承只为复用实现而忽略契约；工厂返回具体类导致客户依赖实现细节。

## 练习与检查点

写两个 Text 实现，一个数组表示、一个字符串表示，检查客户是否需要改变，并列出类型检查无法发现的违约。

检查答案时必须写清前提、推导和一个反例；仅给出术语名称不足以说明理解。可回到官方文中的 reading exercises 检验，再记录与自己最初判断的差异。

## 原文阅读范围

Interfaces, Subtypes, Example: MyString, Why interfaces?, Subclassing, Generic types, Enumerations, Getters and setters, ADTs in non-OOP languages, ADTs in TypeScript, Summary。

## 资料与边界

完整官方阅读通过上方链接查看；作业、项目及考试见 [软件工程学习入口](/topics/software-engineering/)。官方 [录像说明](https://web.mit.edu/6.102/www/sp26/general/#are_lectures_recorded) 明确：本课不设概念讲授式 lectures，课堂用于主动练习且不录像。概念材料以交互阅读提供，因此本单元不适用课堂逐字稿，也没有生成时间轴。
