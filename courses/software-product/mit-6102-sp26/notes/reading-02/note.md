# reading-02 · 测试应从输入空间出发

> 已获用户批准接入 · 来源范围见本文说明。

来源：[MIT 6.102 Spring 2026 · Reading 2: Testing](https://web.mit.edu/6.102/www/sp26/classes/02-testing/)。依据官方阅读正文整理，非课堂逐字稿；下方示例与练习为本地自写教学示例。


## 核心概念与推理

测试无法穷举一般程序的输入空间，需要先按规格划分子域，再选代表值与边界。测试集应正确、充分且小：正确意味着接受所有满足规格的实现，充分意味着覆盖有意义的行为差异，小意味着避免重复而保留诊断价值。黑盒测试从规格选择输入，玻璃盒测试利用实现补充覆盖，但两者的断言都不能超出规格。单元测试隔离模块，回归测试保留已经暴露的失败。

## 具体示例

```ts
// abs 的输入划分：负数、零、正数
assert.strictEqual(abs(-1), 1);
assert.strictEqual(abs(0), 0);
assert.strictEqual(abs(1), 1);
```

零是符号切换的边界。只测 8 和 20 不能覆盖负数分支；重复大量正数也不能替代边界。这里假定规格排除了 NaN 和 Infinity。

## 关键机制补充

多个划分可以覆盖同一输入空间的不同维度。对 max(a,b)，按关系分为 a<b、a=b、a>b，同时对 a 和 b 各按负、零、正分类。不必机械穷举全部笛卡尔积，但需要在选定用例表中逐项确认每个子域被覆盖，并保留重要交叉边界。比如 (-1,-2)、(-1,0)、(0,0)、(0,1)、(1,0)、(1,2) 可用于检查关系与符号覆盖；如果规格还有大数或非有限值约束，应另增分区。语句覆盖也不证明所有条件组合都经历过。

## 常见误区

把高语句覆盖率当作充分正确；用被测函数计算期望值；让单元测试依赖另一个未经验证的模块。

## 练习与检查点

为 max(a,b) 写两个独立划分：a 与 b 的大小关系，以及每个参数的符号；用少量测试覆盖这些子域。

检查答案时必须写清前提、推导和一个反例；仅给出术语名称不足以说明理解。可回到官方文中的 reading exercises 检验，再记录与自己最初判断的差异。

## 原文阅读范围

Validation, Why software testing is hard, Test-first programming, Systematic testing, Choosing test cases by partitioning, Automated unit testing, Documenting your testing strategy, Black box and glass box testing, Coverage, Unit and integration testing, Automated regression testing, Iterative test-first programming, Randomized testing, Summary。

## 资料与边界

完整官方阅读通过上方链接查看；作业、项目及考试见 [软件工程学习入口](/topics/software-engineering/)。官方 [录像说明](https://web.mit.edu/6.102/www/sp26/general/#are_lectures_recorded) 明确：本课不设概念讲授式 lectures，课堂用于主动练习且不录像。概念材料以交互阅读提供，因此本单元不适用课堂逐字稿，也没有生成时间轴。
