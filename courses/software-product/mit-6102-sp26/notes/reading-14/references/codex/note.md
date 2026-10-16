# reading-14 · 并发正确性取决于交错

来源：[MIT 6.102 Spring 2026 · Reading 14: Concurrency](https://web.mit.edu/6.102/www/sp26/classes/14-concurrency/)。依据官方阅读正文整理，非课堂逐字稿；下方示例与练习为本地自写教学示例。

> 待审核候选稿 · evidenceMode: reading-only · 尚未人工审核，未登记公开 outputs。

## 核心概念与推理

并发让多个计算在时间上重叠；进程隔离执行环境，线程通常共享进程内存，Worker 更接近轻量进程。共享内存与消息传递是不同通信模型。竞态出现于结果依赖不可控事件顺序，单次成功不能排除它。读—改—写不是天然原子操作，多步更新可能被其他执行交错。设计应减少共享可变状态或集中其所有权，不能靠增加等待时间来证明正确。

## 具体示例

```ts
// 两个执行单元都做：
const old = balance;
balance = old + 1;
// 若都读到 200，两次增加后可能仍为 201
```

交错顺序为 A 读200、B读200、A写201、B写201。这是明确的丢失更新反例；单线程同步执行时不会发生这类交错，但 Worker 共享内存或异步拆分操作需要重新分析。

## 关键机制补充

消息传递把可变状态收进接收方，也需要考虑协议原子性。两个单独消息构成的“读取后修改”仍可被其他消息插入。并发和并行不等同：计算可在单核上交替推进，也可在多核上同时执行；竞态关注的是允许的时序是否影响规格，而不只是是否用了线程。

## 常见误区

把异步与多线程混为一谈；认为多核必然提升所有任务；通过 sleep 消除竞态。

## 练习与检查点

列出一次存款与一次取款的读写交错，标明哪些违背余额规格，再提出共享状态或消息所有权方案。

检查答案时必须写清前提、推导和一个反例；仅给出术语名称不足以说明理解。可回到官方文中的 reading exercises 检验，再记录与自己最初判断的差异。

## 原文阅读范围

Concurrency, Two models for concurrent programming, Processes, threads, time-slicing, Threads in Python, Workers in TypeScript, Shared memory example, Interleaving, Race condition, Message passing example, Concurrency is hard to test and debug, Summary。

## 资料与边界

完整官方阅读通过上方链接查看；作业、项目及考试见 [软件工程学习入口](/topics/software-engineering/)。官方 [录像说明](https://web.mit.edu/6.102/www/sp26/general/#are_lectures_recorded) 明确：本课不设概念讲授式 lectures，课堂用于主动练习且不录像。概念材料以交互阅读提供，因此本单元不适用课堂逐字稿，也没有生成时间轴。
