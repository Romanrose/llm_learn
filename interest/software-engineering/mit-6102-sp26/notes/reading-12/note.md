# reading-12 · 从文法到语法树

> 已获用户批准接入 · 来源范围见本文说明。

来源：[MIT 6.102 Spring 2026 · Reading 12: Grammars & Parsing](https://web.mit.edu/6.102/www/sp26/classes/12-grammars-parsing/)。依据官方阅读正文整理，非课堂逐字稿；下方示例与练习为本地自写教学示例。


## 核心概念与推理

文法为字符串规定合法结构：终结符是实际符号，非终结符通过产生式组合结构。正则表达式适合无需递归的规则，而嵌套结构需要递归文法。解析树保留语法推导，抽象语法树 AST 保留后续计算需要的结构；两者不是同一层。空白跳过规则的位置影响接受哪些输入，歧义和优先级必须在规则中处理。解析仅证明语法合法，业务约束仍需检查。

## 具体示例

```text
expr ::= number | "(" expr "+" expr ")"
number ::= [0-9]+
// AST: Constant(n) | Plus(left,right)
```

(1+(2+3)) 具有递归嵌套，AST 可以表示为 Plus(Constant(1),Plus(Constant(2),Constant(3)))。圆括号帮助解析但无须保存为 AST 节点。

## 关键机制补充

抽象语法树可以消去括号与空白，却必须保留运算关系与必要值。解析树到 AST 的函数应按产生式逐个处理，非法或未覆盖变体不能静默略过。正则里的反斜线同时可能参与字符串转义、字面字符转义与字符类缩写，调试时应先分清源码字符串和实际正则这两层。

## 常见误区

用一个复杂正则覆盖任意嵌套；把解析成功等同于业务有效；在数字内部跳过空白而意外接受 4 2。

## 练习与检查点

扩展文法支持乘法，定义明确优先级，并画出 1+2*3 的 AST；为非法括号设计拒绝用例。

检查答案时必须写清前提、推导和一个反例；仅给出术语名称不足以说明理解。可回到官方文中的 reading exercises 检验，再记录与自己最初判断的差异。

## 原文阅读范围

Introduction, Grammars, Parse trees, Regular expressions, Parser generators, Summary。

## 资料与边界

完整官方阅读通过上方链接查看；作业、项目及考试见 [软件工程学习入口](/topics/software-engineering/)。官方 [录像说明](https://web.mit.edu/6.102/www/sp26/general/#are_lectures_recorded) 明确：本课不设概念讲授式 lectures，课堂用于主动练习且不录像。概念材料以交互阅读提供，因此本单元不适用课堂逐字稿，也没有生成时间轴。
