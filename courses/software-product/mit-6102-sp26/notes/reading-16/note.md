# reading-16 · 异步 ADT 必须维护安全与活性

> 已获用户批准接入 · 来源范围见本文说明。

来源：[MIT 6.102 Spring 2026 · Reading 16: Mutual Exclusion](https://web.mit.edu/6.102/www/sp26/classes/16-mutual-exclusion/)。依据官方阅读正文整理，非课堂逐字稿；下方示例与练习为本地自写教学示例。


## 核心概念与推理

安全性要求坏事不发生，活性要求好事最终发生。单线程 TypeScript 的同步片段可利用事件循环的互斥性质，但 await 必然交出控制，等待前成立的条件可能失效。异步借书 ADT 可用 deferred Promise 表示归还事件，等待结束后需重新检查资源。多个客户同时醒来不能各自认为自己获得同一本书。死锁则可能来自等待关系成环，而不是数据竞争。

## 具体示例

```ts
while (!available(book)) {
  await returnedSignal(book);
}
// 同步片段内重新检查后立即登记借出
markBorrowed(book);
```

唤醒表示状态可能改变，不代表资源已预留给当前客户。循环重检并让检查与登记之间没有 await，才能在单线程事件循环模型下防止另一异步调用插入。

## 关键机制补充

单线程同步片段的互斥推理只适用于同一个 JavaScript 执行线程；引入共享内存 Worker 以后不能沿用这个保证。await 已完成的 Promise 也会交出控制。设计 deferred 时明确谁负责 resolve/reject、何时删除已完成通知，以及等待者是否需要重新注册下一轮事件。

## 常见误区

用 if 替代重检循环；在检查与更新之间 await；只保证不重复借出却让等待者永远无法完成。

## 练习与检查点

为两位读者等待一本书画执行时序，分别找一个竞态与一个永远等不到的情形。

检查答案时必须写清前提、推导和一个反例；仅给出术语名称不足以说明理解。可回到官方文中的 reading exercises 检验，再记录与自己最初判断的差异。

## 原文阅读范围

Library example, Synchronous ADT, Asynchronous methods, Making and keeping a promise, Asynchronous method making a promise, Race conditions, Fixing the race, Deadlock, Interleaving and mutual exclusion, Redesigning checkout, Other techniques for mutual exclusion。

## 资料与边界

完整官方阅读通过上方链接查看；作业、项目及考试见 [软件工程学习入口](/topics/software-engineering/)。官方 [录像说明](https://web.mit.edu/6.102/www/sp26/general/#are_lectures_recorded) 明确：本课不设概念讲授式 lectures，课堂用于主动练习且不录像。概念材料以交互阅读提供，因此本单元不适用课堂逐字稿，也没有生成时间轴。
