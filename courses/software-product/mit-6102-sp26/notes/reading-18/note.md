# reading-18 · 消息传递需要协议契约

> 已获用户批准接入 · 来源范围见本文说明。

来源：[MIT 6.102 Spring 2026 · Reading 18: Message-Passing and Networking](https://web.mit.edu/6.102/www/sp26/classes/18-message-passing-networking/)。依据官方阅读正文整理，非课堂逐字稿；下方示例与练习为本地自写教学示例。


## 核心概念与推理

消息传递限制模块间共享可变对象，把修改留在各模块内部。Worker 消息可用判别联合定义类型，网络客户与服务端则需要明确请求、响应和状态的协议。消息没有消除并发：多个客户的多条消息仍能交错。HTTP 方法表达操作意图，GET 应用于读取，POST 常用于改变状态；错误、重试与重复提交必须在协议设计中考虑。服务端不能被一个慢客户长期阻塞。

## 具体示例

```ts
type Message =
  | { kind: "get"; id: string }
  | { kind: "put"; id: string; value: number };
// 接收端按 kind 分派并验证运行时数据
```

判别联合让本地编译器检查分支，但网络传来的 JSON 仍是外部数据，不能靠类型断言就信任。若先 get 再 put 进行递增，其他客户可插入；协议可提供单条 increment 操作。

## 关键机制补充

协议设计应把相关状态变化集中在一条完整请求里。例如库存模块应接收一次 tryPurchase，而不是让客户用 readCount 与 writeCount 拼接。HTTP 请求可失败或被重试，服务器应明确重复请求语义；读取与修改分离也帮助缓存和客户理解，但仅选择方法名不会自动兑现这些保证。

## 常见误区

认为消息复制后不存在竞态；把 JSON 强转当验证；重复 POST 导致重复业务操作。

## 练习与检查点

设计库存扣减消息：把检查与扣减作为一次服务端操作，定义不足、成功和重复请求的响应。

检查答案时必须写清前提、推导和一个反例；仅给出术语名称不足以说明理解。可回到官方文中的 reading exercises 检验，再记录与自己最初判断的差异。

## 原文阅读范围

Two models for concurrency, Message passing between workers, Stopping, Race conditions, Client/server design pattern, Networking basics, Web APIs, Web server in TypeScript, Summary。

## 资料与边界

完整官方阅读通过上方链接查看；作业、项目及考试见 [软件工程学习入口](/topics/software-engineering/)。官方 [录像说明](https://web.mit.edu/6.102/www/sp26/general/#are_lectures_recorded) 明确：本课不设概念讲授式 lectures，课堂用于主动练习且不录像。概念材料以交互阅读提供，因此本单元不适用课堂逐字稿，也没有生成时间轴。
